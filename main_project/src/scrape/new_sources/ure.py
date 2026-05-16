"""URE — Urząd Regulacji Energetyki, sekcja Konsumenci.

Discovery: kategorie pod /pl/konsumenci/* — walk + page extraction.

License: urzędowe (Art. 4 ust. 2 PrAut).
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
    LICENSE_URZEDOWE,
    SCRAPE_DATE,
    ArticleRecord,
    Fetcher,
    ScrapeSummary,
    archive_size_mb,
    clean_soup,
    detect_pubdate,
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

logger = logging.getLogger("scrape.new_sources.ure")

BASE = "https://www.ure.gov.pl"
SOURCE_NAME = "ure.gov.pl"

# Entry points - walked recursively up to depth 2.
ENTRY_PATHS = [
    "/pl/konsumenci",
    "/pl/konsumenci/faq-czesto-zadawane-py",
    "/pl/konsumenci/zbior-praw-konsumenta",
    "/pl/konsumenci/poradnik-odbiorcy",
    "/pl/konsumenci/warto-wiedziec-poradnik",
    "/pl/konsumenci/spory-i-skargi-informacje-dla",
    "/pl/konsumenci/masz-wybor",
    "/pl/konsumenci/ostrzezenia-konsumencki",
    "/pl/konsumenci/punkt-informacyjny-dla",
    "/pl/konsumenci/rachunki-pod-kontrola-konsumen",
    "/pl/konsumenci/nieetyczne-praktyki-spr",
    "/pl/konsumenci/koordynator",
    "/pl/edukacja",
    "/pl/edukacja/poradniki",
]


def discover_article_urls(fetcher: Fetcher) -> list[str]:
    seen: set[str] = set()
    queue: list[str] = [urljoin(BASE, p) for p in ENTRY_PATHS]
    # Level walk — start from entries; only collect leaf article-like URLs
    # (those with depth >= 3 in path).
    depth = {u: 0 for u in queue}

    while queue:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        resp = fetcher.get(url)
        if resp is None or resp.status_code != 200:
            continue
        text = resp.content.decode("utf-8", "replace")
        # Find /pl/konsumenci/...-NNNNNNNNNNNNNNN (or any sub-link)
        for href in re.findall(r'href="(/pl/[^"#?]+)"', text):
            # only keep URE-internal consumer paths
            if not (
                href.startswith("/pl/konsumenci")
                or href.startswith("/pl/edukacja")
            ):
                continue
            full = urljoin(BASE, href)
            if full not in seen and depth.get(url, 0) < 2:
                queue.append(full)
                depth[full] = depth.get(url, 0) + 1
    # Filter to plausible article URLs: depth > 2 OR ends with very specific path
    return sorted(seen)


def parse_article(html: str, url: str, idx: int) -> ArticleRecord | None:
    soup = BeautifulSoup(html, "lxml")
    clean_soup(soup)
    title = extract_title(soup)
    body = extract_main_text(soup)
    if len(body) < 250:
        return None
    pubdate = detect_pubdate(soup, html)
    subtitle = extract_subtitle(soup)
    cites = extract_citations(body)

    slug = slug_from_title(title, 50)
    aid = f"ure_{idx:04d}_{slug}"
    return ArticleRecord(
        article_id=aid,
        source=SOURCE_NAME,
        source_url=url,
        title=title,
        subtitle=subtitle,
        author=None,
        publication_date=pubdate,
        tresc=body,
        category="konsumenci_energia",
        tags=["konsumenci", "energia"],
        extracted_citations=cites,
        license=LICENSE_URZEDOWE,
        scrape_date=SCRAPE_DATE,
        metadata={"char_count": len(body)},
    )


def scrape(output_dir: Path, max_articles: int | None) -> ScrapeSummary:
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = output_dir / "_archive"
    fetcher = Fetcher(rate_limit_sec=0.8)

    urls = discover_article_urls(fetcher)
    logger.info("discovered %d URLs", len(urls))
    if max_articles:
        urls = urls[:max_articles]

    records: list[ArticleRecord] = []
    manifest: list[dict] = []
    failed: list[tuple[str, str]] = []
    summary = ScrapeSummary(
        source=SOURCE_NAME, license=LICENSE_URZEDOWE, discovered_urls=len(urls)
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
    summary.notes = f"BFS walk od {len(ENTRY_PATHS)} entry paths, depth max 2."

    write_jsonl_articles(records, output_dir / "articles.jsonl")
    write_manifest(manifest, output_dir / "_manifest.json")
    write_summary(summary, output_dir / "_summary.json")
    write_failed_log(failed, output_dir / "_failed.log")
    write_readme(
        output_dir,
        SOURCE_NAME,
        f"{BASE}/pl/konsumenci",
        LICENSE_URZEDOWE,
        "BFS walk konsumenci + edukacja path tree",
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
