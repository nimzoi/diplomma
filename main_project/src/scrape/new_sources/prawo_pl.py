"""Prawo.pl — LexisNexis Polska, sekcja konsumenci-i-handel (oraz powiązane).

Discovery: sitemap articles_pl_*.xml (kilkadziesiąt tysięcy URLs across sekcji).
Filter:
  - URL prefix /biznes/ (sekcja prawo konsumenckie)
  - Albo URL contains consumer keywords w slug
  - Plus listing /prawo/konsumenci-i-handel,21,k.html jeśli paginacja zadziała

License: fair-use Art. 29 PrAut (research). Public articles only — paywall
articles wykluczone (oznaczone meta tag `requires_subscription`).
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
    parse_sitemap,
    persist_raw_html,
    slug_from_title,
    write_failed_log,
    write_jsonl_articles,
    write_manifest,
    write_readme,
    write_summary,
)

logger = logging.getLogger("scrape.new_sources.prawo_pl")

BASE = "https://www.prawo.pl"
SOURCE_NAME = "prawo.pl"
SITEMAP_INDEX = f"{BASE}/sitemap.xml"

CONSUMER_KEYWORDS = (
    "konsument",
    "reklamacj",
    "rekojm",
    "rękojm",
    "gwarancj",
    "kredyt-konsument",
    "kredyt-",
    "uokik",
    "odstapieni",
    "odstąpieni",
    "klauzul-niedozwol",
    "klauzule-niedozwol",
    "zwrot-towar",
    "abonament",
    "umow-konsumenck",
    "ustaw-konsumenck",
    "prawa-konsument",
    "ochron-konsument",
    "frankow",
    "sankcja-kredyt-darmow",
    "wibor",
    "polisol",
    "sklep-intern",
    "zakup-przez-internet",
    "naruszen-praw-konsument",
)

# Article URL must end with NNNN.html and be in /biznes/ or have consumer kw
ARTICLE_RE = re.compile(r"^https://www\.prawo\.pl/[\w-]+/[\w-]+,\d{4,}\.html$")


def discover_article_urls(fetcher: Fetcher, max_collect: int = 800) -> list[str]:
    """Walk articles_pl_*.xml chunks, filter by /biznes/ prefix + keywords."""
    resp = fetcher.get(SITEMAP_INDEX)
    if resp is None or resp.status_code != 200:
        logger.warning("sitemap index unavailable")
        return []
    sm_urls = parse_sitemap(resp.content)
    article_sitemaps = [u for u in sm_urls if "articles_pl_" in u]
    logger.info("discovered %d article sitemap chunks", len(article_sitemaps))

    out: list[str] = []
    seen: set[str] = set()
    for sm_url in article_sitemaps:
        if len(out) >= max_collect:
            break
        resp = fetcher.get(sm_url)
        if resp is None:
            continue
        urls = parse_sitemap(resp.content)
        for u in urls:
            if not ARTICLE_RE.match(u):
                continue
            slug_part = u.split("/")[-1].lower()
            url_lower = u.lower()
            # Accept if /biznes/ (konsumenci sub) OR matches a consumer keyword.
            is_biznes = "/biznes/" in url_lower
            kw_match = any(kw in slug_part for kw in CONSUMER_KEYWORDS)
            if not (is_biznes or kw_match):
                continue
            if u in seen:
                continue
            seen.add(u)
            out.append(u)
            if len(out) >= max_collect:
                break
        logger.info("scan %s -> total %d kept", sm_url.split("/")[-1], len(out))
    return out


def parse_article(html: str, url: str, idx: int) -> ArticleRecord | None:
    soup = BeautifulSoup(html, "lxml")
    # Detect paywall — prawo.pl uses gating div / data attributes.
    if "Pełna treść dostępna" in html or "premium-content" in html.lower()[:5000]:
        return None
    clean_soup(soup)
    title = extract_title(soup)
    body = extract_main_text(soup)
    if len(body) < 400:
        return None
    pubdate = detect_pubdate(soup, html)
    author = extract_author(soup)
    subtitle = extract_subtitle(soup)
    cites = extract_citations(body)

    m = re.match(r"https://www\.prawo\.pl/([\w-]+)/", url)
    section = m.group(1) if m else "ogolne"

    slug = slug_from_title(title, 50)
    aid = f"prawo_pl_{idx:04d}_{slug}"
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
        tags=[section],
        extracted_citations=cites,
        license=LICENSE_FAIR_USE,
        scrape_date=SCRAPE_DATE,
        metadata={"char_count": len(body), "section": section},
    )


def scrape(output_dir: Path, max_articles: int | None) -> ScrapeSummary:
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = output_dir / "_archive"
    fetcher = Fetcher(rate_limit_sec=1.0)

    cap = max_articles or 600
    urls = discover_article_urls(fetcher, max_collect=cap * 2)
    logger.info("collected %d candidate URLs", len(urls))
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
            failed.append((url, "too_short_or_paywall"))
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
        "Sitemap articles_pl_*.xml walk, filter: /biznes/ prefix LUB consumer keyword "
        "w slug. Paywall articles wykluczone (Pełna treść dostępna marker)."
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
        "Sitemap walk + consumer keyword filter",
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
