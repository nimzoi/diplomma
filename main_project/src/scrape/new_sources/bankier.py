"""Bankier.pl — sekcja Prawo (wiadomości prawno-podatkowe).

Discovery: kategorie /wiadomosci/prawo + /wiadomosci/prawo-i-podatki + pagination
(/N). Artykuły: pattern ``/wiadomosc/SLUG-NNNNNN.html``.

License: fair-use Art. 29 PrAut (research, attribution preserved).
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

from scrape.new_sources.common import (  # noqa: E402
    LICENSE_FAIR_USE,
    SCRAPE_DATE,
    ArticleRecord,
    Fetcher,
    ScrapeSummary,
    archive_size_mb,
    clean_soup,
    detect_pubdate,
    extract_author,
    extract_citations,
    extract_main_text,
    extract_subtitle,
    extract_title,
    persist_raw_html,
    slug_from_title,
    write_failed_log,
    write_jsonl_articles,
    write_manifest,
    write_readme,
    write_summary,
)

logger = logging.getLogger("scrape.new_sources.bankier")

BASE = "https://www.bankier.pl"
SOURCE_NAME = "bankier.pl"

# Listing pages — pagination via /N suffix. Bankier endpoints:
# - /wiadomosci (lista, redirects to /wiadomosc/)
# - /wiadomosc/N — pagination strona N
LISTING_PAGES = [
    "/wiadomosci",  # initial → /wiadomosc/
    "/wiadomosc/2",
    "/wiadomosc/3",
    "/wiadomosc/4",
    "/wiadomosc/5",
    "/wiadomosc/6",
    "/wiadomosc/7",
    "/wiadomosc/8",
    "/wiadomosc/9",
    "/wiadomosc/10",
    "/wiadomosc/15",
    "/wiadomosc/20",
    "/wiadomosc/30",
    "/wiadomosc/40",
    "/wiadomosc/50",
]
MAX_PAGES_PER_LISTING = 1  # każda LISTING_PAGE = jedna strona

ARTICLE_RE = re.compile(r"/wiadomosc/[\w\-%]+-\d+\.html")

# Filter slugs that look consumer-relevant. Conservative — keep all that match
# wiadomosci/prawo pattern, ale tagujemy heurystycznie konsument relevance.
KONSUMENT_KEYWORDS = (
    "konsument",
    "reklamacj",
    "kredyt",
    "uokik",
    "gwarancj",
    "rękojm",
    "rekojm",
    "ochron",
    "umow",
    "kara",
    "praw konsument",
    "biznes",
    "podatek",
    "kupna",
    "sprzedaż",
    "abonament",
)


def discover_article_urls(fetcher: Fetcher) -> list[str]:
    seen: set[str] = set()
    for path in LISTING_PAGES:
        url = f"{BASE}{path}"
        resp = fetcher.get(url)
        if resp is None or resp.status_code != 200:
            logger.warning("listing %s skipped", path)
            continue
        text = resp.content.decode("utf-8", "replace")
        found = ARTICLE_RE.findall(text)
        new = 0
        for href in found:
            full = urljoin(BASE, href)
            if full not in seen:
                seen.add(full)
                new += 1
        logger.info("%s: +%d (total %d)", path, new, len(seen))
    return sorted(seen)


def parse_article(html: str, url: str, idx: int) -> ArticleRecord | None:
    soup = BeautifulSoup(html, "lxml")
    clean_soup(soup)
    title = extract_title(soup)
    body = extract_main_text(soup)
    if len(body) < 300:
        return None
    pubdate = detect_pubdate(soup, html)
    author = extract_author(soup)
    subtitle = extract_subtitle(soup)
    cites = extract_citations(body)

    body_lower = body.lower() + " " + title.lower()
    relevance_match = any(kw in body_lower for kw in KONSUMENT_KEYWORDS)

    slug = slug_from_title(title, 50)
    aid = f"bankier_{idx:04d}_{slug}"
    return ArticleRecord(
        article_id=aid,
        source=SOURCE_NAME,
        source_url=url,
        title=title,
        subtitle=subtitle,
        author=author,
        publication_date=pubdate,
        tresc=body,
        category="prawo / wiadomości",
        tags=["consumer-relevant"] if relevance_match else ["general-law"],
        extracted_citations=cites,
        license=LICENSE_FAIR_USE,
        scrape_date=SCRAPE_DATE,
        metadata={"char_count": len(body)},
    )


def scrape(output_dir: Path, max_articles: int | None) -> ScrapeSummary:
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = output_dir / "_archive"
    fetcher = Fetcher(rate_limit_sec=1.0)

    urls = discover_article_urls(fetcher)
    logger.info("discovered %d articles", len(urls))
    if max_articles:
        urls = urls[:max_articles]

    records: list[ArticleRecord] = []
    manifest: list[dict] = []
    failed: list[tuple[str, str]] = []
    summary = ScrapeSummary(
        source=SOURCE_NAME, license=LICENSE_FAIR_USE, discovered_urls=len(urls)
    )

    for idx, url in enumerate(urls, start=1):
        logger.info("[%d/%d] %s", idx, len(urls), url[:90])
        resp = fetcher.get(url)
        if resp is None or resp.status_code != 200:
            failed.append((url, f"http_{resp.status_code if resp else 'none'}"))
            summary.failed_urls += 1
            continue
        rec = parse_article(resp.content.decode("utf-8", "replace"), url, idx)
        if rec is None:
            summary.skipped_too_short += 1
            failed.append((url, "too_short"))
            continue
        records.append(rec)
        persist_raw_html(archive_dir, rec.article_id, resp.content, url, resp.status_code)
        manifest.append(
            {
                "article_id": rec.article_id,
                "url": url,
                "status": resp.status_code,
                "title": rec.title[:120],
                "char_count": len(rec.tresc),
            }
        )
        summary.successful_articles += 1
        summary.total_chars += len(rec.tresc)

    if records:
        summary.avg_chars_per_article = round(summary.total_chars / len(records), 1)
    summary.archive_mb = archive_size_mb(archive_dir)
    summary.notes = (
        f"Walk {len(LISTING_PAGES)} kategorii × {MAX_PAGES_PER_LISTING} stron "
        f"paginacji. Article URL pattern: /wiadomosc/SLUG-NNNNNN.html. Tagging "
        "heurystyczny: consumer-relevant vs general-law."
    )

    write_jsonl_articles(records, output_dir / "articles.jsonl")
    write_manifest(manifest, output_dir / "_manifest.json")
    write_summary(summary, output_dir / "_summary.json")
    write_failed_log(failed, output_dir / "_failed.log")
    write_readme(
        output_dir,
        SOURCE_NAME,
        BASE,
        LICENSE_FAIR_USE,
        f"{len(LISTING_PAGES)} kategorii listing + paginacja",
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-articles", type=int, default=None)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    )
    summary = scrape(args.output.resolve(), args.max_articles)
    logger.info("done: %s", summary.as_dict())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
