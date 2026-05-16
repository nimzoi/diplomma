"""Scrape consumer-rights questions from Polish legal Q&A fora.

Three adapters:
  - e-prawnik.pl       — forum threads from selected categories (paginated)
  - forumprawne.org    — `prawa-konsumenta` subforum (paginated)
  - eporady24.pl       — paid lawyers Q&A under "Ochrona konsumenta" + adjacent categories

Output: one JSONL per source under
  data/raw/consumer_questions_polish_2026-05-16/

Schema (per line):
  {
    "question_id":           "<source>_<NNN>",
    "question":              "<concise question (title or meta description)>",
    "context":               "<optional original-poster body, if scraped>",
    "source":                "<domain>",
    "source_url":            "<canonical thread/page URL>",
    "category":              "<source category slug>",
    "thread_responses_count": <int|null>,
    "scrape_date":           "YYYY-MM-DD",
    "extracted_topics":      ["zwrot", "reklamacja", ...]
  }

We capture only the question (initial post + title). Answers from random users
are noisy and we do not want them as ground truth — for hallucination eval we
will generate our own Bielik answers and judge them.

Polish encoding: NFC normalized; user names anonymized when stored.

Usage (PowerShell):
  uv run python -m scrape.legal_fora.scrape `
      --source e-prawnik `
      --categories prawo-cywilne-1,prawo-cywilne `
      --max-pages 20 `
      --output ../data/raw/consumer_questions_polish_2026-05-16/e_prawnik_consumer.jsonl

  uv run python -m scrape.legal_fora.scrape `
      --source forumprawne `
      --max-pages 50 `
      --output ../data/raw/consumer_questions_polish_2026-05-16/forumprawne_consumer.jsonl

  uv run python -m scrape.legal_fora.scrape `
      --source eporady24 `
      --max-pages 20 `
      --output ../data/raw/consumer_questions_polish_2026-05-16/legal_other_polish.jsonl
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
import unicodedata
from collections.abc import Iterable, Iterator
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup, Tag

logger = logging.getLogger("scrape.legal_fora")
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 "
    "(PJATK thesis - polish consumer questions - magmarsochacka@gmail.com)"
)
REQUEST_TIMEOUT_SEC = 25.0
RATE_LIMIT_SEC = 1.0
TODAY = datetime.now().strftime("%Y-%m-%d")

# Topic keywords for tagging (used by all adapters).
# Stems are normalized: substring match on lowercased text.
TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    "zwrot": ("zwrot", "zwracam", "zwróć", "odstąpienie od umowy"),
    "reklamacja": ("reklamac", "wadliw", "wady towaru", "uszkodz"),
    "gwarancja": ("gwarancj",),
    "rękojmia": ("rękojm", "rekojmi"),
    "umowa-na-odleglosc": (
        "na odległość",
        "umowa zawart",
        "sklep internet",
        "zakup online",
        "zakup przez internet",
    ),
    "sklep": ("sklep", "sprzedawca", "sprzedawc"),
    "allegro": ("allegro",),
    "olx": ("olx",),
    "vinted": ("vinted",),
    "kurier-paczka": ("kurier", "paczk", "przesyłk", "przesylk", "dpd", "inpost"),
    "telekomunikacja": (
        "operator",
        "abonament",
        "orange",
        "t-mobile",
        "play s.a",
        "plus s.a",
    ),
    "energia-gaz": ("prąd", "energia elektr", "tauron", "pgnig"),
    "bank-kredyt": ("kredyt", "pożyczk", "pozyczk", "lokat"),
    "ubezpieczenie": ("ubezpiecz",),
    "uokik": ("uokik",),
    "rzecznik": ("rzecznik konsument",),
    "termin-14-30-dni": ("14 dni", "30 dni"),
    "naprawa-serwis": ("naprawa", "serwis", "warsztat"),
    "pojazd-auto": (
        "samoch",
        "auto",
    ),
    "elektronika": ("telewizor", "laptop", "smartfon", "pralka", "lodówk"),
    "meble": ("mebl", "kanapa", "szafa", "łóżk"),
    "dostawa": ("dostawa", "dostarczen", "dostarczy", "wysyłk", "wysylk"),
    "cena-przedplata": ("zaliczk", "przedpłat", "przedplat"),
    "niezgodnosc": ("niezgodn",),
    "odszkodowanie": ("odszkodow",),
    "klauzule-niedozwolone": ("klauzul niedozw",),
    "nieuczciwe-praktyki": ("nieuczciw",),
    "towar": ("towar",),
}

# Stricter relevance gate for e-prawnik: thread title must have one of these
# substrings to count as "consumer" (vs. just "civil law"). Without this, the
# umbrella `umowa` keyword pulls in rental/employment threads.
EPRAWNIK_RELEVANCE_KEYWORDS: tuple[str, ...] = (
    "konsument",
    "konsumen",
    "reklamac",
    "rękojm",
    "rekojmi",
    "gwarancj",
    "zwrot towar",
    "zwrot pien",
    "zwrot zaliczk",
    "zwrotu towar",
    "odstąpienie od umowy",
    "wadliw",
    "uszkodzon",
    "wad towaru",
    "wad ukryt",
    "allegro",
    "olx",
    "vinted",
    "amazon",
    "ebay",
    "sklep",
    "sprzedawca",
    "uokik",
    "rzecznik konsumen",
    "klauzul niedozw",
    "nieuczciw",
    "niezgodn",
    "zakup online",
    "zakup przez internet",
    "sklep internet",
    "kurier",
    "paczk",
    "inpost",
    "dpd",
    "operator komór",
    "abonament",
    "telekom",
    "play s.a",
    "ubezpieczyciel",
    "polisa",
    "kredyt konsum",
    "pożyczka",
    "rata kredyt",
    "umowa o świadcz",
    "umowa kupna",
    "umowa sprzed",
    "zaliczk",
    "przedpłat",
    "odszkodow",
)


def normalize_pl(text: str) -> str:
    """NFC normalize and collapse whitespace."""
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def anonymize(text: str) -> str:
    """Remove obvious email/phone leaks from question text."""
    text = re.sub(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", "[EMAIL]", text)
    text = re.sub(r"\+?\d[\d \-]{7,}\d", "[PHONE]", text)
    return text


def extract_topics(*texts: str) -> list[str]:
    """Tag question with topic keywords (multi-label, simple substring match)."""
    blob = " ".join(t.lower() for t in texts if t)
    hits: list[str] = []
    for tag, kws in TOPIC_KEYWORDS.items():
        if any(kw in blob for kw in kws):
            hits.append(tag)
    return hits


@dataclass
class QuestionRecord:
    question_id: str
    question: str
    context: str
    source: str
    source_url: str
    category: str
    thread_responses_count: int | None
    scrape_date: str = TODAY
    extracted_topics: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class Fetcher:
    """Polite HTTP client with rate limit + retries."""

    def __init__(self, rate_limit_sec: float = RATE_LIMIT_SEC) -> None:
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.rate_limit_sec = rate_limit_sec
        self._last_fetch = 0.0

    def get(self, url: str, *, retries: int = 2) -> requests.Response | None:
        wait = self.rate_limit_sec - (time.monotonic() - self._last_fetch)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(retries + 1):
            try:
                resp = self.session.get(
                    url, timeout=REQUEST_TIMEOUT_SEC, allow_redirects=True
                )
                self._last_fetch = time.monotonic()
                if resp.status_code == 200:
                    return resp
                logger.warning(
                    "GET %s -> %d (attempt %d)", url, resp.status_code, attempt + 1
                )
            except requests.RequestException as exc:
                logger.warning("GET %s ERR %s (attempt %d)", url, exc, attempt + 1)
            time.sleep(2.0 * (attempt + 1))
        return None


# ---------------------------------------------------------------------------
# e-prawnik.pl adapter
# ---------------------------------------------------------------------------

EPRAWNIK_BASE = "https://e-prawnik.pl"
EPRAWNIK_CONSUMER_CATEGORIES: tuple[str, ...] = (
    # Forum has no dedicated "ochrona-konsumenta" but consumer threads live in:
    "domowy/prawo-cywilne-1",  # ~6050 threads (121 pages * 50)
    "biznes/prawo-cywilne",
    "biznes/prawo-bankowe",
    "biznes/windykacja-naleznosci",
    "domowy/ubezpieczenia-zdrowotne",
    "domowy/ubezpieczenia-majatkowe",
)


def eprawnik_list_threads(fetcher: Fetcher, category: str, page: int) -> list[dict]:
    """Return [{href, title, replies}] for a category listing page."""
    url = f"{EPRAWNIK_BASE}/forum/{category}/{page}"
    resp = fetcher.get(url)
    if resp is None:
        return []
    soup = BeautifulSoup(resp.content, "lxml")
    threads: dict[str, dict] = {}
    for a in soup.find_all("a", href=True):
        href: str = a["href"]
        text = a.get_text(strip=True)
        if not href.endswith(".html"):
            continue
        if "/forum/" not in href:
            continue
        # Skip admin/static pages
        if "/inne/" in href or "/zasob" in href or "/akty" in href:
            continue
        full = href if href.startswith("http") else f"{EPRAWNIK_BASE}{href}"
        slug = full.split("/")[-1].replace(".html", "")
        # The same href appears 3x (title + "Zobacz wątek" + replies count).
        rec = threads.setdefault(slug, {"href": full, "title": "", "replies": None})
        if (
            text
            and text != "Zobacz wątek"
            and not re.match(r"\d+\s+odp", text)
            and len(text) > 3
            and len(rec["title"]) < len(text)
        ):
            rec["title"] = text
        m = re.match(r"(\d+)\s+odp", text)
        if m:
            rec["replies"] = int(m.group(1))
    out = [t for t in threads.values() if t["title"]]
    logger.info("e-prawnik %s page=%d -> %d threads", category, page, len(out))
    return out


def eprawnik_parse_thread(
    fetcher: Fetcher, url: str
) -> tuple[str, str] | tuple[None, None]:
    """Return (title, original_post_body) for thread; None on failure."""
    resp = fetcher.get(url)
    if resp is None:
        return (None, None)
    soup = BeautifulSoup(resp.content, "lxml")
    h1 = soup.find("h1")
    title = (
        normalize_pl(h1.get_text(strip=True).removesuffix(" - forum prawne"))
        if h1
        else ""
    )
    # Original post body: typically the first message div on the page. Looking at
    # raw page these are inside the post listing — the very first content text
    # right after the title block.
    body_text = ""
    # First, try standard "post" classes
    candidates: list[Tag] = []
    for div in soup.find_all("div"):
        cls = " ".join(div.get("class", [])).lower()
        if "tresc" in cls or "post-body" in cls or "messagecontent" in cls:
            candidates.append(div)
    if candidates:
        body_text = normalize_pl(candidates[0].get_text(separator=" ", strip=True))
    if not body_text:
        # Fallback — extract from the main article element; strip nav clutter.
        main = soup.find("main") or soup.find("body")
        if main:
            # Drop nav/menu/footer
            for tag in main.find_all(["nav", "footer", "aside", "script", "style"]):
                tag.decompose()
            text = main.get_text(separator=" ", strip=True)
            # The first ~500 chars are nav residue; pick the chunk after the H1.
            idx = text.find(title) if title else -1
            if idx > 0:
                body_text = normalize_pl(
                    text[idx + len(title) : idx + len(title) + 1500]
                )
    return (title or None, anonymize(body_text)[:2000])


def eprawnik_iter(fetcher: Fetcher, max_pages_per_cat: int) -> Iterator[QuestionRecord]:
    counter = 0
    seen_urls: set[str] = set()
    for category in EPRAWNIK_CONSUMER_CATEGORIES:
        for page in range(1, max_pages_per_cat + 1):
            threads = eprawnik_list_threads(fetcher, category, page)
            if not threads:
                break
            for t in threads:
                if t["href"] in seen_urls:
                    continue
                seen_urls.add(t["href"])
                title = normalize_pl(t["title"])
                if not title:
                    continue
                # Stricter consumer relevance gate (not just any topic kw — the
                # forum is generic civil-law, dominated by employment/rental).
                low = title.lower()
                if not any(kw in low for kw in EPRAWNIK_RELEVANCE_KEYWORDS):
                    continue
                topics = extract_topics(title)
                counter += 1
                yield QuestionRecord(
                    question_id=f"eprawnik_{counter:05d}",
                    question=title,
                    context="",  # initial post body fetched on-demand only if needed
                    source="e-prawnik.pl",
                    source_url=t["href"],
                    category=category,
                    thread_responses_count=t.get("replies"),
                    extracted_topics=topics,
                )


# ---------------------------------------------------------------------------
# forumprawne.org adapter
# ---------------------------------------------------------------------------

FORUMPRAWNE_BASE = "https://forumprawne.org"
FORUMPRAWNE_CONSUMER_FORUM = "prawa-konsumenta.33"


def forumprawne_list_threads(fetcher: Fetcher, page: int) -> list[dict]:
    """Return [{href, title}] from a forum listing page."""
    if page == 1:
        url = f"{FORUMPRAWNE_BASE}/forum/{FORUMPRAWNE_CONSUMER_FORUM}/"
    else:
        url = f"{FORUMPRAWNE_BASE}/forum/{FORUMPRAWNE_CONSUMER_FORUM}/page-{page}"
    resp = fetcher.get(url)
    if resp is None:
        return []
    soup = BeautifulSoup(resp.content, "lxml")
    out: dict[str, str] = {}
    for a in soup.find_all("a", href=True):
        h: str = a["href"]
        m = re.match(r"^/watek/[^/]+\.\d+/?$", h)
        if not m:
            continue
        title = a.get_text(strip=True)
        if not title or len(title) < 8:
            continue
        full = f"{FORUMPRAWNE_BASE}{h.rstrip('/')}/"
        # Multiple anchors per thread; keep longest title.
        if full not in out or len(title) > len(out[full]):
            out[full] = title
    threads = [{"href": k, "title": v} for k, v in out.items()]
    logger.info("forumprawne page=%d -> %d threads", page, len(threads))
    return threads


def forumprawne_parse_thread(
    fetcher: Fetcher, url: str
) -> tuple[str, str, int | None] | tuple[None, None, None]:
    """Return (title, first_post_body, replies_count) or Nones."""
    resp = fetcher.get(url)
    if resp is None:
        return (None, None, None)
    soup = BeautifulSoup(resp.content, "lxml")
    h1 = soup.find("h1")
    title = normalize_pl(h1.get_text(strip=True)) if h1 else ""
    articles = soup.find_all(
        "article", class_=lambda c: c and "message" in str(c).lower()
    )
    if not articles:
        return (title or None, "", None)
    first = articles[0]
    body = first.find(
        "div",
        class_=lambda c: (
            c and ("bbWrapper" in str(c) or "message-body" in str(c).lower())
        ),
    )
    body_text = normalize_pl(body.get_text(separator=" ", strip=True)) if body else ""
    # Replies = total posts on this page minus the OP (capped — multi-page threads
    # under-counted, but we don't paginate per-thread).
    replies = max(0, len(articles) - 1)
    return (title or None, anonymize(body_text)[:2000], replies)


def forumprawne_iter(
    fetcher: Fetcher, max_pages: int, fetch_bodies: bool = True
) -> Iterator[QuestionRecord]:
    counter = 0
    seen_urls: set[str] = set()
    for page in range(1, max_pages + 1):
        threads = forumprawne_list_threads(fetcher, page)
        if not threads:
            break
        for t in threads:
            if t["href"] in seen_urls:
                continue
            seen_urls.add(t["href"])
            title = normalize_pl(t["title"])
            body, replies = "", None
            if fetch_bodies:
                title2, body, replies = forumprawne_parse_thread(fetcher, t["href"])
                if title2:
                    title = title2
            if not title:
                continue
            counter += 1
            yield QuestionRecord(
                question_id=f"forumprawne_{counter:05d}",
                question=title,
                context=body or "",
                source="forumprawne.org",
                source_url=t["href"],
                category="prawa-konsumenta",
                thread_responses_count=replies,
                extracted_topics=extract_topics(title, body or ""),
            )


# ---------------------------------------------------------------------------
# eporady24.pl adapter (bonus "legal_other_polish")
# ---------------------------------------------------------------------------

EPORADY24_BASE = "https://www.eporady24.pl"
EPORADY24_CATEGORIES: tuple[tuple[str, str, str], ...] = (
    # (slug, kategoria_id, podkategoria_id)
    ("Ochrona_konsumenta", "4", "54"),
    ("Aukcje_internetowe", "17", "82"),
    ("swiadczenie_uslug_droga_elektroniczna", "17", "110"),
    ("umowy", "4", "47"),
)


def eporady24_listing_url(slug: str, kat: str, pkat: str, page: int) -> str:
    if page == 1:
        return f"{EPORADY24_BASE}/{slug}-podkategoria-{kat}-{pkat}.html"
    return f"{EPORADY24_BASE}/{slug}-podkategoria-pytania-{kat}-{pkat}-{page}.html"


def eporady24_list_questions(
    fetcher: Fetcher, slug: str, kat: str, pkat: str, page: int
) -> list[dict]:
    url = eporady24_listing_url(slug, kat, pkat, page)
    resp = fetcher.get(url)
    if resp is None:
        return []
    soup = BeautifulSoup(resp.content, "lxml")
    # Each question's link uses pattern `/{slug},pytania,{kat},{pkat},{id}.html`.
    out: list[dict] = []
    seen_local: set[str] = set()
    for a in soup.find_all("a", href=True):
        href: str = a["href"]
        m = re.search(r",pytania,\d+,\d+,(\d+)\.html$", href)
        if not m:
            continue
        title = a.get_text(strip=True).lstrip("▶").strip()
        if not title or len(title) < 8:
            continue
        full = href if href.startswith("http") else f"{EPORADY24_BASE}{href}"
        if full in seen_local:
            continue
        seen_local.add(full)
        out.append({"href": full, "title": title, "qid": m.group(1)})
    logger.info("eporady24 %s/%s page=%d -> %d questions", slug, pkat, page, len(out))
    return out


def eporady24_parse_question(
    fetcher: Fetcher, url: str
) -> tuple[str, str] | tuple[None, None]:
    """Return (title, body_of_question) using meta description (the OP question)."""
    resp = fetcher.get(url)
    if resp is None:
        return (None, None)
    soup = BeautifulSoup(resp.content, "lxml")
    h1 = soup.find("h1")
    title = normalize_pl(h1.get_text(strip=True)) if h1 else ""
    body = ""
    desc = soup.find("meta", attrs={"name": "description"})
    if desc and desc.get("content"):
        body = normalize_pl(desc["content"])
    if not body:
        og = soup.find("meta", attrs={"property": "og:description"})
        if og and og.get("content"):
            body = normalize_pl(og["content"])
    return (title or None, anonymize(body)[:1500])


def eporady24_iter(
    fetcher: Fetcher, max_pages_per_cat: int
) -> Iterator[QuestionRecord]:
    counter = 0
    seen_urls: set[str] = set()
    for slug, kat, pkat in EPORADY24_CATEGORIES:
        for page in range(1, max_pages_per_cat + 1):
            items = eporady24_list_questions(fetcher, slug, kat, pkat, page)
            if not items:
                break
            for it in items:
                if it["href"] in seen_urls:
                    continue
                seen_urls.add(it["href"])
                title, body = eporady24_parse_question(fetcher, it["href"])
                if not title:
                    continue
                counter += 1
                yield QuestionRecord(
                    question_id=f"eporady24_{counter:05d}",
                    question=title,
                    context=body or "",
                    source="eporady24.pl",
                    source_url=it["href"],
                    category=f"{slug}/{pkat}",
                    thread_responses_count=1,  # one lawyer answer per question
                    extracted_topics=extract_topics(title, body or ""),
                )


# ---------------------------------------------------------------------------
# Main / CLI
# ---------------------------------------------------------------------------


def write_jsonl(records: Iterable[QuestionRecord], output: Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with output.open("w", encoding="utf-8") as fh:
        for rec in records:
            fh.write(json.dumps(rec.as_dict(), ensure_ascii=False) + "\n")
            fh.flush()
            n += 1
    return n


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        required=True,
        choices=["e-prawnik", "forumprawne", "eporady24"],
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Path to output .jsonl file.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Max listing pages per category (default 10).",
    )
    parser.add_argument(
        "--categories",
        type=str,
        default="",
        help="(e-prawnik) Comma-separated list of categories to override defaults.",
    )
    parser.add_argument(
        "--rate-limit-sec",
        type=float,
        default=RATE_LIMIT_SEC,
        help="Politeness delay between HTTP requests (default 1.0s).",
    )
    parser.add_argument(
        "--no-bodies",
        action="store_true",
        help="(forumprawne) Skip fetching per-thread bodies (faster, title-only).",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    fetcher = Fetcher(rate_limit_sec=args.rate_limit_sec)

    if args.source == "e-prawnik":
        if args.categories:
            global EPRAWNIK_CONSUMER_CATEGORIES
            EPRAWNIK_CONSUMER_CATEGORIES = tuple(
                c.strip() for c in args.categories.split(",") if c.strip()
            )
        records = eprawnik_iter(fetcher, args.max_pages)
    elif args.source == "forumprawne":
        records = forumprawne_iter(
            fetcher, args.max_pages, fetch_bodies=not args.no_bodies
        )
    elif args.source == "eporady24":
        records = eporady24_iter(fetcher, args.max_pages)
    else:
        raise SystemExit(f"Unknown source: {args.source}")

    n = write_jsonl(records, args.output)
    logger.info("Wrote %d records -> %s", n, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
