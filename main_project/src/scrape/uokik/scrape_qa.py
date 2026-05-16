"""UOKiK Q&A scraper.

Scrapes consumer Q&A pairs from https://prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/.

Each category page renders questions as `su-spoiler` accordion blocks containing:
- title (heading "N. Question?")
- HTML answer body, optionally ending with `<blockquote>Podstawa prawna: ...</blockquote>`.

We extract Q + A text + parsed `cited_articles` (list of statute references) per pair.

Output:
    uokik_qa.jsonl  -- one Q&A per line
    uokik_meta.json -- aggregate stats

Run:
    uv run python -m src.scrape.uokik.scrape_qa \
        --output ../data/raw/uokik_qa_2026-05-16
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import time
import unicodedata
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable

import requests
from bs4 import BeautifulSoup

LOGGER = logging.getLogger("scrape_qa")

BASE_URL = "https://prawakonsumenta.uokik.gov.pl"
CATEGORIES: dict[str, str] = {
    # slug -> human-readable label
    "zagadnienia-ogolne": "Ogolne",
    "obowiazki-informacyjne": "Prawo do informacji",
    "odstapienie-od-umowy": "Odstapienie od umowy",
    "reklamacje": "Reklamacja",
    "telemarketing": "Telemarketing",
}
USER_AGENT = (
    "Mozilla/5.0 (compatible; PJATK-thesis-bot/1.0; "
    "+research, contact magmarsochacka@gmail.com)"
)
RATE_LIMIT_SECONDS = 1.0
REQUEST_TIMEOUT = 30


# ---------------------------------------------------------------------------
# data model
# ---------------------------------------------------------------------------


@dataclass
class QAPair:
    qa_id: str
    question: str
    answer: str
    cited_articles: list[str]
    category: str
    source_url: str
    scrape_date: str
    anchor: str | None = None


@dataclass
class ScrapeStats:
    scrape_date: str
    source_root: str
    total_pairs: int = 0
    pairs_with_citations: int = 0
    categories: dict[str, int] = field(default_factory=dict)
    citations_per_pair_avg: float = 0.0


# ---------------------------------------------------------------------------
# citation parsing
# ---------------------------------------------------------------------------

# Maps statute names appearing after "ustawy" to canonical short form.
STATUTE_ALIASES: dict[str, str] = {
    "o prawach konsumenta": "ustawy o prawach konsumenta",
    "o przeciwdzialaniu nieuczciwym praktykom rynkowym": (
        "ustawy o przeciwdzialaniu nieuczciwym praktykom rynkowym"
    ),
}

# Article reference fragment, e.g.:
#   art. 22(1) Kodeksu cywilnego
#   art. 10 ust. 1 i 2 ustawy o prawach konsumenta
#   art. 548 § 3 Kodeksu cywilnego
#   art. 38 pkt 12 ustawy o prawach konsumenta
ART_REF_RE = re.compile(
    r"art\.\s*"
    r"\d+[a-zA-Z]*"
    r"(?:\s*[¹²³⁰-⁹])?"  # superscript digits (e.g. art. 22^1)
    r"(?:\s*\([\dA-Za-z]+\))?"
    r"(?:\s*\xa7\s*\d+[a-zA-Z]*)?"  # § N
    r"(?:\s+(?:ust\.|pkt|lit\.|in\.|zd\.)\s*[\w\s\d.,;-]+?(?=\s+(?:i\s+art\.|oraz\s+art\.|art\.|Kodeksu|ustawy|w\s+zwiazku|w\s+zw\.|$|\.|\,)))?",
    re.IGNORECASE,
)

# Full citation block following "Podstawa prawna:" until end-of-line/sentence.
PODSTAWA_RE = re.compile(
    r"Podstawa\s+prawna\s*:\s*(.+?)(?:\s*$)",
    re.IGNORECASE | re.MULTILINE,
)

# Superscript digit translation (art. 22¹ -> art. 22 § 1 style; we keep as-is)
SUPERSCRIPT = {
    "¹": "1",
    "²": "2",
    "³": "3",
    "⁰": "0",
    "⁴": "4",
    "⁵": "5",
    "⁶": "6",
    "⁷": "7",
    "⁸": "8",
    "⁹": "9",
}


def normalize_text(text: str) -> str:
    """NFC unicode normalization + whitespace collapse."""
    text = unicodedata.normalize("NFC", text)
    text = text.replace(" ", " ")  # non-breaking space
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _normalize_superscripts(s: str) -> str:
    """art. 22¹ -> art. 22^1 keeping caret notation for downstream parsers."""
    out = []
    for ch in s:
        if ch in SUPERSCRIPT:
            out.append("^" + SUPERSCRIPT[ch])
        else:
            out.append(ch)
    return "".join(out)


def parse_citations(podstawa_text: str) -> list[str]:
    """Split 'Podstawa prawna: ...' content into discrete article references.

    Heuristic:
      1. Split by ' oraz ' / ' i ' boundaries where followed by 'art. '.
      2. Re-attach the statute name (suffix after the last article in the run)
         to articles that don't already have one.
    """
    text = normalize_text(podstawa_text)
    text = _normalize_superscripts(text)

    # Drop trailing punctuation/sentence noise.
    text = re.sub(r"[;.]+\s*$", "", text)

    # Split into atoms by commas/semicolons or " oraz ", " i " when followed
    # by another art. reference.
    # Use a simpler approach: find each statute group (articles + statute name)
    # within the string.

    citations: list[str] = []

    # Pattern: one or more "art. X[, art. Y, ... art. Z]" followed by a
    # statute marker. We accept:
    #   Kodeksu cywilnego / postępowania cywilnego / karnego / wykroczeń
    #   ustawy / ustawa o ...
    #   Prawa telekomunikacyjnego / bankowego / etc.
    group_re = re.compile(
        r"(art\.[^,;]+?(?:(?:,\s*art\.|;\s*art\.|\s+i\s+art\.|\s+oraz\s+art\.)[^,;]+?)*?)"
        r"\s+("
        r"Kodeksu\s+\w+(?:\s+\w+)?"
        r"|ustaw[ay]\s+o\s+[\w\s]+?"
        r"|Prawa\s+\w+"
        r"|Rozporzadzeni\w+\s+[\w\s.,/]+?"
        r")"
        r"(?=$|[.;]|\s+oraz\s+art\.|\s+i\s+art\.|,\s*art\.)",
        re.IGNORECASE,
    )

    matched_spans: list[tuple[int, int]] = []
    for m in group_re.finditer(text):
        articles_blob = m.group(1).strip()
        statute = re.sub(r"\s+", " ", m.group(2).strip())
        # Split this blob into individual articles. Only split on
        # "," / ";" / " i " / " oraz " when the next token is "art." --
        # otherwise we would chop "art. 10 ust. 1 i 2" in half.
        parts = re.split(
            r"\s*(?:,|;)\s*(?=art\.)|\s+(?:i|oraz)\s+(?=art\.)",
            articles_blob,
        )
        for p in parts:
            p = p.strip().rstrip(",;")
            if p and p.lower().startswith("art."):
                citations.append(f"{p} {statute}")
        matched_spans.append((m.start(), m.end()))

    # Fallback: if no statute-grouped match was found, capture standalone
    # "art. X" references and tag them with "(statute unknown)".
    if not citations:
        for m in ART_REF_RE.finditer(text):
            citations.append(m.group(0).strip())

    # Normalize statute name to canonical genitive form for stable dedup.
    norm = []
    for c in citations:
        c = re.sub(r"\s+", " ", c)
        c = re.sub(r"\bustawa\b", "ustawy", c, flags=re.IGNORECASE)
        norm.append(c)

    # Deduplicate while preserving order.
    seen = set()
    out: list[str] = []
    for c in norm:
        key = c.lower()
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out


# ---------------------------------------------------------------------------
# HTML parsing
# ---------------------------------------------------------------------------


def fetch(url: str, session: requests.Session) -> str:
    LOGGER.info("GET %s", url)
    resp = session.get(url, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    # Force UTF-8 (UOKiK serves UTF-8 but encoding hint can be missing).
    resp.encoding = "utf-8"
    return resp.text


def _clean_title(raw: str) -> str:
    """Strip 'N. ' prefix and any leftover tags."""
    txt = normalize_text(raw)
    txt = re.sub(r"^\d+\.\s*", "", txt)
    return txt


def parse_category_page(
    html: str, category: str, source_url: str, scrape_date: str
) -> list[QAPair]:
    soup = BeautifulSoup(html, "lxml")
    pairs: list[QAPair] = []

    spoilers = soup.select("div.su-spoiler")
    LOGGER.info("  found %d spoiler blocks in category %s", len(spoilers), category)

    for idx, spoiler in enumerate(spoilers, start=1):
        title_div = spoiler.select_one(".su-spoiler-title")
        content_div = spoiler.select_one(".su-spoiler-content")
        if title_div is None or content_div is None:
            LOGGER.warning("    spoiler #%d missing title/content; skipping", idx)
            continue

        # Title: strip the icon span.
        for icon in title_div.select(".su-spoiler-icon"):
            icon.decompose()
        question = _clean_title(title_div.get_text(" ", strip=True))

        # Replace <sup>N</sup> with ^N so "art. 577<sup>2</sup>" becomes
        # "art. 577^2" instead of "art. 577 2".
        for sup in content_div.select("sup"):
            sup.replace_with("^" + sup.get_text(strip=True))

        # Pull out the legal basis blockquote (if present) so the answer
        # text doesn't double-count it.
        cited_articles: list[str] = []
        for bq in content_div.select("blockquote"):
            bq_text = bq.get_text(" ", strip=True)
            m = PODSTAWA_RE.search(bq_text)
            if m:
                cited_articles.extend(parse_citations(m.group(1)))
            bq.decompose()

        # As a fallback, also scan the body for "Podstawa prawna:" lines
        # that weren't inside a blockquote.
        body_text_raw = content_div.get_text("\n", strip=True)
        for m in PODSTAWA_RE.finditer(body_text_raw):
            new_cits = parse_citations(m.group(1))
            for c in new_cits:
                if c not in cited_articles:
                    cited_articles.append(c)
            # Remove that line from the answer.
            body_text_raw = body_text_raw.replace(m.group(0), "").strip()

        answer = normalize_text(body_text_raw)

        if not question or not answer:
            LOGGER.warning("    spoiler #%d empty Q or A; skipping", idx)
            continue

        anchor = spoiler.get("data-anchor")
        qa_id = f"uokik_{category}_{idx:03d}"
        pairs.append(
            QAPair(
                qa_id=qa_id,
                question=question,
                answer=answer,
                cited_articles=cited_articles,
                category=CATEGORIES[category],
                source_url=source_url,
                scrape_date=scrape_date,
                anchor=str(anchor) if isinstance(anchor, str) else None,
            )
        )

    return pairs


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


def scrape_all(output_dir: Path, scrape_date: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = output_dir / "uokik_qa.jsonl"
    meta_path = output_dir / "uokik_meta.json"

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT, "Accept-Language": "pl,en;q=0.7"})

    all_pairs: list[QAPair] = []
    stats = ScrapeStats(
        scrape_date=scrape_date, source_root=f"{BASE_URL}/pytania-i-odpowiedzi/"
    )

    for slug, label in CATEGORIES.items():
        url = f"{BASE_URL}/pytania-i-odpowiedzi/{slug}/"
        try:
            html = fetch(url, session)
        except requests.RequestException as exc:
            LOGGER.error("  failed to fetch %s: %s", url, exc)
            continue
        try:
            pairs = parse_category_page(html, slug, url, scrape_date)
        except Exception as exc:  # noqa: BLE001 - keep scraping other categories
            LOGGER.exception("  parsing failure on %s: %s", url, exc)
            continue

        LOGGER.info("  parsed %d Q&A pairs from %s", len(pairs), label)
        stats.categories[label] = len(pairs)
        all_pairs.extend(pairs)
        time.sleep(RATE_LIMIT_SECONDS)

    # Sanity check + write outputs.
    stats.total_pairs = len(all_pairs)
    stats.pairs_with_citations = sum(1 for p in all_pairs if p.cited_articles)
    total_cits = sum(len(p.cited_articles) for p in all_pairs)
    stats.citations_per_pair_avg = round(total_cits / max(1, stats.total_pairs), 2)

    with jsonl_path.open("w", encoding="utf-8") as f:
        for pair in all_pairs:
            f.write(json.dumps(asdict(pair), ensure_ascii=False) + "\n")

    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(asdict(stats), f, ensure_ascii=False, indent=2)

    LOGGER.info("wrote %d Q&A pairs to %s", stats.total_pairs, jsonl_path)
    LOGGER.info("wrote stats to %s", meta_path)
    LOGGER.info(
        "citations per pair: avg=%.2f, with-cit=%d/%d",
        stats.citations_per_pair_avg,
        stats.pairs_with_citations,
        stats.total_pairs,
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output directory (will be created if missing).",
    )
    parser.add_argument(
        "--scrape-date",
        default="2026-05-16",
        help="ISO date to stamp on each record (default: 2026-05-16).",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    )
    scrape_all(args.output.resolve(), args.scrape_date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
