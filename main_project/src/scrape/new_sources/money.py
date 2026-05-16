"""Money.pl — sekcja Prawo (porady konsumenckie).

Discovery: sekcja /sekcja/prawo/ + pagination + RSS feed /rss/rss.xml.
Article URL: ``/<section>/SLUG-NNNN.html`` (numerical suffix).

License: fair-use Art. 29 PrAut (research).
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

logger = logging.getLogger("scrape.new_sources.money")

BASE = "https://www.money.pl"
SOURCE_NAME = "money.pl"

# Money.pl section listings — consumer-relevant
LISTING_PAGES = [
    "/sekcja/prawo/",
    "/sekcja/gospodarka/",
    "/sekcja/finanse/",
    "/sekcja/firma/",
    "/sekcja/biznes/",
]
MAX_PAGES = 10

# article URL: /<section>/<slug>-NNNN(NNNNNNNNNN)a.html or v.html  e.g. /pieniadze/ma-31-lat-i-firme...7285846272128065v.html
ARTICLE_RE = re.compile(r"/[a-z][a-z-]+/[a-z][\w-]+-\d{10,}[av]\.html")
RSS_URL = f"{BASE}/rss/rss.xml"

KONSUMENT_KEYWORDS = (
    "konsument",
    "reklamacj",
    "kredyt",
    "uokik",
    "gwarancj",
    "rękojm",
    "rekojm",
    "umowa",
    "prawo",
    "kupna",
    "sprzedaż",
    "abonament",
    "bank",
    "ubezpieczen",
    "energia",
    "uslugi",
    "konto",
)


def discover_article_urls(fetcher: Fetcher) -> list[str]:
    seen: set[str] = set()
    # 1) RSS feed
    resp = fetcher.get(RSS_URL)
    if resp and resp.status_code == 200:
        for m in re.finditer(r"<link>(https?://www\.money\.pl/[^<]+)</link>", resp.content.decode("utf-8", "replace")):
            url = m.group(1).strip()
            if url.endswith(".html"):
                seen.add(url)
        logger.info("RSS: %d URLs", len(seen))
    # 2) Section pagination
    for path in LISTING_PAGES:
        for pg in range(1, MAX_PAGES + 1):
            url = f"{BASE}{path}" if pg == 1 else f"{BASE}{path}{pg}/"
            resp = fetcher.get(url)
            if resp is None or resp.status_code != 200:
                break
            text = resp.content.decode("utf-8", "replace")
            found = ARTICLE_RE.findall(text)
            new = 0
            for href in found:
                full = urljoin(BASE, href)
                if full not in seen:
                    seen.add(full)
                    new += 1
            logger.info("%s page %d: +%d (total %d)", path, pg, new, len(seen))
            if new == 0 and pg > 1:
                break
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
    relevance = sum(1 for kw in KONSUMENT_KEYWORDS if kw in body_lower)

    # Section from URL
    m = re.match(r"https?://www\.money\.pl/([a-z][a-z-]+)/", url)
    section = m.group(1) if m else "ogolne"

    slug = slug_from_title(title, 50)
    aid = f"money_{idx:04d}_{slug}"
    return ArticleRecord(
        article_id=aid,
        source=SOURCE_NAME,
        source_url=url,
        title=title,
        subtitle=subtitle,
        author=author,
        publication_date=pubdate,
        tresc=body,
        category=section,
        tags=["consumer-relevant"] if relevance >= 2 else ["general"],
        extracted_citations=cites,
        license=LICENSE_FAIR_USE,
        scrape_date=SCRAPE_DATE,
        metadata={"char_count": len(body), "section": section, "kw_hits": relevance},
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
    cat_counter: dict[str, int] = {}

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
        if rec.category:
            cat_counter[rec.category] = cat_counter.get(rec.category, 0) + 1

    if records:
        summary.avg_chars_per_article = round(summary.total_chars / len(records), 1)
    summary.archive_mb = archive_size_mb(archive_dir)
    summary.categories = cat_counter
    summary.notes = (
        f"RSS feed + {len(LISTING_PAGES)} sekcji × {MAX_PAGES} paginacji. "
        "Tagging consumer-relevant vs general po keywordach (≥2 = consumer)."
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
        "RSS + listing pagination",
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
