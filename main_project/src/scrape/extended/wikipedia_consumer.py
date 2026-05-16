"""Polish Wikipedia consumer-law articles scraper.

Pobiera kuratorską listę polskich artykułów Wikipedia o prawie konsumenta
przez MediaWiki REST API (`/api/rest_v1/page/segments/<title>` zwraca clean HTML).

License: CC BY-SA 4.0 (wszystkie Wikipedia tekstowe content). Attribution
zachowana w metadata.source_url + license string.

Output: ``wikipedia_consumer.jsonl`` — jeden EncyclopedicChunk per H2 section
(długie artykuły dzielone na sections). Lead paragraph trafia jako "section=Lead".

Usage::

    uv run python -m src.scrape.extended.wikipedia_consumer \\
        --output ../data/raw/extended_consumer_2026-05-16
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# Setup PYTHONPATH for direct module execution.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scrape.extended.common import (  # noqa: E402
    TODAY,
    EncyclopedicChunk,
    Fetcher,
    ScrapeStats,
    extract_citations,
    normalize_pl,
    write_jsonl,
    write_stats,
)

logger = logging.getLogger("scrape.extended.wikipedia_consumer")

# Kurated lista — confirmed via search 2026-05-16. Każdy artykuł sprawdzony
# że istnieje i ma substantywny consumer-law content.
WIKIPEDIA_ARTICLES: tuple[str, ...] = (
    "Prawa_konsumenta",
    "Ustawa_o_prawach_konsumenta",
    "Ochrona_praw_konsumenta",
    "Konsument_(prawo)",
    "Kredyt_konsumencki",
    "Reklamacja",
    "Rękojmia",
    "Niedozwolone_postanowienie_umowne",
    "Niezgodność_towaru_konsumpcyjnego_z_umową",
    "Urząd_Ochrony_Konkurencji_i_Konsumentów",
    "Klauzula_(prawo)",
    "Sprzedaż_konsumencka",
    "Federacja_Konsumentów",
    "Inspekcja_Handlowa",
    "Umowa",
)

WIKIPEDIA_API_BASE = "https://pl.wikipedia.org/w/api.php"
WIKIPEDIA_PAGE_BASE = "https://pl.wikipedia.org/wiki/"

# Minimalna długość chunk (po normalizacji) — short stub sections są pomijane.
MIN_CHUNK_CHARS = 200

LICENSE = "CC BY-SA 4.0 (Wikipedia)"


def fetch_article_html(fetcher: Fetcher, title: str) -> str | None:
    """Pobierz rendered HTML artykułu przez MediaWiki API (action=parse).

    Zwraca treść w formacie HTML (dla łatwego section split przez <h2>).
    """
    from urllib.parse import urlencode

    params = {
        "action": "parse",
        "page": title,
        "format": "json",
        "prop": "text|sections",
        "redirects": "1",
        "disablelimitreport": "true",
        "disableeditsection": "true",
        "disabletoc": "true",
    }
    url = WIKIPEDIA_API_BASE + "?" + urlencode(params)
    resp = fetcher.get(url)
    if resp is None:
        return None
    try:
        data = resp.json()
        return data.get("parse", {}).get("text", {}).get("*")
    except (ValueError, KeyError) as exc:
        logger.error("parse failure for %s: %s", title, exc)
        return None


def _clean_section_text(section_soup: BeautifulSoup) -> str:
    """Wytnij tabele, infoboxy, references, navboxes — zostaw tylko prose."""
    for sel in [
        ".infobox",
        ".navbox",
        ".reference",
        ".references",
        "ol.references",
        ".mw-editsection",
        ".thumb",
        ".gallery",
        "table",
        "sup.reference",
        "#toc",
        ".toc",
        ".hatnote",
        ".ambox",
        ".metadata",
    ]:
        for el in section_soup.select(sel):
            el.decompose()
    txt = section_soup.get_text(" ", strip=True)
    # Drop bracketed citation marks like [1], [2]
    txt = re.sub(r"\[\d+\]", "", txt)
    return normalize_pl(txt)


def split_into_sections(html: str, title: str, source_url: str) -> list[EncyclopedicChunk]:
    """Podziel artykuł na chunks per H2 section (lead = pierwszy chunk)."""
    soup = BeautifulSoup(html, "lxml")

    # The MediaWiki HTML has structure: <div class="mw-parser-output">
    # containing paragraphs, then <h2> sections.
    root = soup.select_one(".mw-parser-output") or soup

    chunks: list[EncyclopedicChunk] = []

    # Collect children sequentially, split on H2.
    current_section_name: str | None = None  # None = lead
    current_buffer: list = []

    def flush() -> None:
        nonlocal current_section_name, current_buffer
        if not current_buffer:
            return
        wrapper = BeautifulSoup("<div></div>", "lxml").div
        for el in current_buffer:
            wrapper.append(el)
        text = _clean_section_text(wrapper)
        # Skip "Przypisy" / "Bibliografia" / "Linki zewnętrzne" / "Zobacz też"
        sn = (current_section_name or "Lead").strip()
        skip_sections = {
            "Przypisy",
            "Bibliografia",
            "Linki zewnętrzne",
            "Zobacz też",
            "Uwagi",
        }
        if sn in skip_sections:
            current_buffer = []
            return
        if len(text) >= MIN_CHUNK_CHARS:
            slug = re.sub(r"\W+", "_", sn.lower()).strip("_")[:40] or "lead"
            title_slug = re.sub(r"\W+", "_", title.lower()).strip("_")[:50]
            chunk_id = f"wiki_pl_{title_slug}_{slug}"
            chunks.append(
                EncyclopedicChunk(
                    chunk_id=chunk_id,
                    source="pl.wikipedia.org",
                    source_url=source_url,
                    title=title.replace("_", " "),
                    section=sn,
                    tresc=text,
                    license=LICENSE,
                    scrape_date=TODAY,
                    metadata={
                        "cited_articles": extract_citations(text),
                    },
                )
            )
        current_buffer = []

    def is_h2_wrapper(el) -> bool:
        """Detect MediaWiki H2 wrapper (modern: div.mw-heading-mw-heading2; legacy: bare <h2>)."""
        if getattr(el, "name", None) == "h2":
            return True
        if getattr(el, "name", None) == "div":
            classes = el.get("class", []) or []
            if "mw-heading2" in classes:
                return True
        return False

    def heading_text(el) -> str:
        raw = el.get_text(" ", strip=True)
        return re.sub(r"\[\s*edytuj[^\]]*\]", "", raw).strip()

    for child in list(root.children):
        if is_h2_wrapper(child):
            flush()
            current_section_name = heading_text(child)
        else:
            current_buffer.append(child)
    flush()

    return chunks


def scrape_all(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher()
    all_chunks: list[EncyclopedicChunk] = []
    per_article_counts: dict[str, int] = {}

    for title in WIKIPEDIA_ARTICLES:
        source_url = WIKIPEDIA_PAGE_BASE + title
        logger.info("=== Wikipedia: %s ===", title)
        html = fetch_article_html(fetcher, title)
        if html is None:
            logger.warning("  skip %s (fetch failed)", title)
            continue
        chunks = split_into_sections(html, title, source_url)
        logger.info("  %d chunks extracted", len(chunks))
        per_article_counts[title] = len(chunks)
        all_chunks.extend(chunks)

    # Stats
    total_chars = sum(len(c.tresc) for c in all_chunks)
    with_cit = sum(1 for c in all_chunks if c.metadata.get("cited_articles"))
    stats = ScrapeStats(
        source="pl.wikipedia.org",
        scrape_date=TODAY,
        license=LICENSE,
        total_records=len(all_chunks),
        records_with_citations=with_cit,
        avg_text_length=round(total_chars / max(1, len(all_chunks)), 1),
        categories=per_article_counts,
        notes=(
            f"Kurated lista {len(WIKIPEDIA_ARTICLES)} artykułów; section-level chunking "
            f"przez H2, MIN_CHUNK_CHARS={MIN_CHUNK_CHARS}. Skipped: Przypisy, "
            "Bibliografia, Linki zewnętrzne, Zobacz też, Uwagi."
        ),
    )

    write_jsonl(all_chunks, output_dir / "wikipedia_consumer.jsonl")
    write_stats(stats, output_dir / "wikipedia_consumer_meta.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="Output directory")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    )
    scrape_all(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
