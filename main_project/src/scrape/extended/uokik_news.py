"""UOKiK aktualności (news / komunikaty) scraper — extended beyond Q&A FAQ.

Pobiera artykuły z `uokik.gov.pl/aktualnosci?page=N` (37 pages, ~12 articles
each => ~450 max). Każdy article ma URL formy `uokik.gov.pl/<slug>`.

License: urzędowe (Art. 4 PrAut). UOKiK = polski urząd państwowy.

Filtry:
- date_from: opcjonalne, drop articles starsze niż (np. tylko 2024+)
- max_pages: limit dla testowego rate-limiting

Output: uokik_news.jsonl + meta.

Usage::

    uv run python -m src.scrape.extended.uokik_news \\
        --output ../data/raw/extended_consumer_2026-05-16 \\
        --max-pages 15
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scrape.extended.common import (
    TODAY,
    EncyclopedicChunk,
    Fetcher,
    ScrapeStats,
    extract_citations,
    normalize_pl,
    write_jsonl,
    write_stats,
)

logger = logging.getLogger("scrape.extended.uokik_news")

BASE = "https://uokik.gov.pl"
NEWS_INDEX = f"{BASE}/aktualnosci?page="

LICENSE = "urzędowe — Art. 4 PrAut (UOKiK, organ administracji państwowej)"
MIN_ARTICLE_CHARS = 200

DATE_RE = re.compile(r"\b(\d{2}\.\d{2}\.\d{4})\b")


def discover_articles_on_page(html: str) -> list[tuple[str, str, str]]:
    """Wyłuskaj [(date_str, title, full_url)] z indexowej strony aktualności."""
    soup = BeautifulSoup(html, "lxml")
    out: list[tuple[str, str, str]] = []
    seen: set[str] = set()

    for art in soup.select("article"):
        # Title z H2/H3 wewnątrz article (link text jest pusty)
        h = art.find(["h2", "h3"])
        if not h:
            continue
        title = normalize_pl(h.get_text(" ", strip=True))
        if not title:
            continue
        # URL — pierwszy <a> z href który NIE jest aktualnosci?... ani BASE
        url = None
        for a in art.find_all("a", href=True):
            full = urljoin(BASE, a["href"])
            if "aktualnosci?" in full or full.rstrip("/") == BASE or "newsletter" in full:
                continue
            url = full
            break
        if not url or url in seen:
            continue
        seen.add(url)
        # Date z article text (DD.MM.YYYY na początku)
        art_text = normalize_pl(art.get_text(" ", strip=True))
        m = DATE_RE.search(art_text[:30])
        date_s = m.group(1) if m else ""
        out.append((date_s, title, url))
    return out


def parse_article(
    html: str, source_url: str, list_title: str, list_date: str, idx: int
) -> EncyclopedicChunk | None:
    """Wyciągnij body artykułu UOKiK."""
    soup = BeautifulSoup(html, "lxml")
    # Wytnij niepotrzebne: nav, footer, sidebar
    for sel in [
        "nav",
        "footer",
        ".sidebar",
        ".breadcrumb",
        ".social",
        ".share",
        ".gallery",
        ".pliki",
        ".attachments",
    ]:
        for el in soup.select(sel):
            el.decompose()

    art = soup.select_one("article") or soup.select_one(".article-body") or soup.select_one("main")
    if art is None:
        return None

    # Title — h1 z artykułu lub fallback z listy
    h1 = art.select_one("h1")
    title = normalize_pl(h1.get_text(" ", strip=True)) if h1 else list_title
    if not title:
        title = list_title

    # Body — paragraphs only, skip image captions / "Podziel się"
    paragraphs: list[str] = []
    for p in art.select("p"):
        txt = normalize_pl(p.get_text(" ", strip=True))
        # Skip nav noise
        if not txt or len(txt) < 20:
            continue
        if any(
            x in txt
            for x in ["Podziel się", "Pliki do pobrania", "Następne zdjęcie", "Poprzednie zdjęcie"]
        ):
            continue
        paragraphs.append(txt)

    body = "\n".join(paragraphs)
    if len(body) < MIN_ARTICLE_CHARS:
        return None

    slug_src = source_url.rstrip("/").rsplit("/", 1)[-1]
    chunk_id = f"uokik_news_{idx:04d}_{slug_src[:50]}"

    return EncyclopedicChunk(
        chunk_id=chunk_id,
        source="uokik.gov.pl",
        source_url=source_url,
        title=title,
        section=list_date or None,  # zostaw date w "section" field
        tresc=body,
        license=LICENSE,
        scrape_date=TODAY,
        metadata={
            "cited_articles": extract_citations(body),
            "published_date": list_date,
            "paragraphs_count": len(paragraphs),
        },
    )


def scrape_all(output_dir: Path, max_pages: int) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher()

    all_listings: list[tuple[str, str, str]] = []
    for page in range(1, max_pages + 1):
        url = NEWS_INDEX + str(page)
        logger.info("INDEX page %d -> %s", page, url)
        resp = fetcher.get(url)
        if resp is None:
            break
        listings = discover_articles_on_page(resp.content.decode("utf-8", "replace"))
        if not listings:
            logger.info("  empty — stopping")
            break
        logger.info("  %d article links", len(listings))
        all_listings.extend(listings)

    # Dedupe
    seen: set[str] = set()
    uniq: list[tuple[str, str, str]] = []
    for d, t, u in all_listings:
        if u in seen:
            continue
        seen.add(u)
        uniq.append((d, t, u))

    logger.info("==> %d unique article URLs", len(uniq))

    chunks: list[EncyclopedicChunk] = []
    per_year: dict[str, int] = {}

    for idx, (date_s, title, url) in enumerate(uniq, start=1):
        logger.info("[%d/%d] %s | %s", idx, len(uniq), date_s, title[:60])
        resp = fetcher.get(url)
        if resp is None:
            continue
        chunk = parse_article(resp.content.decode("utf-8", "replace"), url, title, date_s, idx)
        if chunk is None:
            logger.warning("  parse: too short / no content")
            continue
        chunks.append(chunk)
        year = date_s[-4:] if date_s else "unknown"
        per_year[year] = per_year.get(year, 0) + 1

    total_chars = sum(len(c.tresc) for c in chunks)
    with_cit = sum(1 for c in chunks if c.metadata.get("cited_articles"))
    stats = ScrapeStats(
        source="uokik.gov.pl/aktualnosci",
        scrape_date=TODAY,
        license=LICENSE,
        total_records=len(chunks),
        records_with_citations=with_cit,
        avg_text_length=round(total_chars / max(1, len(chunks)), 1),
        categories=per_year,
        notes=(
            f"{max_pages} pages indexed, {len(uniq)} unique articles. UOKiK news "
            "format: krótkie reporty + decyzje + komunikaty kontrolne. "
            "Heterogeneous content — niektóre artykuły mają explicit citations, "
            "większość to journalistic style."
        ),
    )

    write_jsonl(chunks, output_dir / "uokik_news.jsonl")
    write_stats(stats, output_dir / "uokik_news_meta.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-pages", type=int, default=15)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    )
    scrape_all(args.output.resolve(), args.max_pages)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
