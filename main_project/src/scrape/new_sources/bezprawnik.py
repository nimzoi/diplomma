"""Bezprawnik.pl — porady prawnicze z humorystyczną nutą.

Source: <https://bezprawnik.pl/>. Discovery przez RSS feed + tag pagination
(`/tag/prawa-konsumenta/`, `/tag/konsument/`, etc.). Ograniczamy się do
artykułów oznaczonych tagiem konsumenckim.

License: fair-use (research, Art. 29 PrAut). Comment z `source_url`.

Usage::

    uv run python -m scrape.new_sources.bezprawnik \\
        --output ../data/raw/bezprawnik_pl_2026-05-16 \\
        --max-articles 300
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
    already_archived,
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

logger = logging.getLogger("scrape.new_sources.bezprawnik")

BASE = "https://bezprawnik.pl"
SOURCE_NAME = "bezprawnik.pl"

# Tag pages walked dla discovery. Pagination /tag/<slug>/N/.
TAG_PAGES = [
    "/tag/prawa-konsumenta/",
    "/tag/konsument/",
    "/tag/reklamacja/",
    "/tag/odstapienie-od-umowy/",
    "/tag/gwarancja/",
    "/tag/rekojmia/",
    "/tag/zakupy-w-internecie/",
    "/tag/kredyt-konsumencki/",
    "/tag/uokik/",
    "/tag/zwrot-towaru/",
]

MAX_PAGES_PER_TAG = 5  # 5 stron pagination per tag (każda ~10 artykułów)


def discover_article_urls(fetcher: Fetcher) -> list[str]:
    """Walk tag pages + RSS feed → list of unique article URLs."""
    seen: set[str] = set()

    # 1) RSS feed
    resp = fetcher.get(f"{BASE}/feed/")
    if resp and resp.status_code == 200:
        for m in re.finditer(
            r"<link>(https?://bezprawnik\.pl/[^<]+)</link>", resp.text
        ):
            url = m.group(1).strip()
            if url == BASE or url == BASE + "/":
                continue
            seen.add(url)
        logger.info("RSS feed: %d URLs", len(seen))

    # 2) Tag pages + pagination
    for tag in TAG_PAGES:
        for pg in range(1, MAX_PAGES_PER_TAG + 1):
            url = f"{BASE}{tag}" if pg == 1 else f"{BASE}{tag}{pg}/"
            resp = fetcher.get(url)
            if resp is None or resp.status_code != 200:
                break
            # Extract article links from grid — bezprawnik uses /slug/ paths.
            text = resp.text
            new_count = 0
            for href in re.findall(r'href="(/[^"#?]+/?)"', text):
                if href.count("/") < 2:
                    continue
                if any(
                    href.startswith(p)
                    for p in (
                        "/tag/",
                        "/tagi/",
                        "/kategorie/",
                        "/category/",
                        "/author/",
                        "/strona/",
                        "/wp-",
                        "/_next/",
                    )
                ):
                    continue
                if not re.match(r"^/[a-z0-9][a-z0-9-]+/?$", href):
                    continue
                full = urljoin(BASE, href)
                if full not in seen:
                    seen.add(full)
                    new_count += 1
            logger.info("tag %s page %d: +%d (total %d)", tag, pg, new_count, len(seen))
            if new_count == 0:
                break

    return sorted(seen)


def parse_article(html: str, url: str, idx: int) -> ArticleRecord | None:
    soup = BeautifulSoup(html, "lxml")
    # Bezprawnik uses Next.js — article body is in __NEXT_DATA__ JSON sometimes,
    # but also rendered to HTML article tag.
    clean_soup(soup)

    title = extract_title(soup)
    body = extract_main_text(soup)
    if len(body) < 250:
        return None
    subtitle = extract_subtitle(soup)
    pubdate = detect_pubdate(soup, html)
    author = extract_author(soup)
    cites = extract_citations(body)

    slug = slug_from_title(title, 50)
    aid = f"bezprawnik_{idx:04d}_{slug}"
    return ArticleRecord(
        article_id=aid,
        source=SOURCE_NAME,
        source_url=url,
        title=title,
        subtitle=subtitle,
        author=author,
        publication_date=pubdate,
        tresc=body,
        category="prawo konsumenckie",
        tags=[],
        extracted_citations=cites,
        license=LICENSE_FAIR_USE,
        scrape_date=SCRAPE_DATE,
        metadata={"char_count": len(body)},
    )


def scrape(output_dir: Path, max_articles: int | None) -> ScrapeSummary:
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = output_dir / "_archive"
    fetcher = Fetcher(rate_limit_sec=1.0, verify_ssl=True)

    urls = discover_article_urls(fetcher)
    logger.info("discovered %d article URLs", len(urls))
    if max_articles:
        urls = urls[:max_articles]

    records: list[ArticleRecord] = []
    manifest: list[dict] = []
    failed: list[tuple[str, str]] = []
    summary = ScrapeSummary(
        source=SOURCE_NAME,
        license=LICENSE_FAIR_USE,
        discovered_urls=len(urls),
    )

    for idx, url in enumerate(urls, start=1):
        title_slug_preview = url.rstrip("/").split("/")[-1][:50]
        article_id_preview = f"bezprawnik_{idx:04d}_{title_slug_preview}"
        # Idempotency check — skip if already in archive (under any title).
        # We can't recompute final id pre-parse, but we cache by url-hash.
        url_hash_id = f"bezprawnik_url_{idx:04d}"
        if already_archived(archive_dir, url_hash_id):
            summary.skipped_duplicate += 1
            continue

        logger.info("[%d/%d] %s", idx, len(urls), url[:90])
        resp = fetcher.get(url)
        if resp is None or resp.status_code != 200:
            failed.append((url, f"http_{resp.status_code if resp else 'none'}"))
            summary.failed_urls += 1
            continue
        rec = parse_article(resp.text, url, idx)
        if rec is None:
            summary.skipped_too_short += 1
            failed.append((url, "too_short_or_no_content"))
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
        f"RSS feed + {len(TAG_PAGES)} tag pages walked, "
        f"{MAX_PAGES_PER_TAG} pages each. Next.js SPA content extracted z HTML."
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
        "RSS feed + 10 tag pages walked (z paginacją 5 stron każdy)",
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
