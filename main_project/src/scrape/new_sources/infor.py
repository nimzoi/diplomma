"""Infor.pl — porady konsument (sekcja prawo).

Discovery: kategorie /prawo/prawa-konsumenta/<sub>/ + pagination (/2/, /3/, ...).
Artykuły pattern: ``/prawo/prawa-konsumenta/<sub>/NNNNNN,SLUG.html``.

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

logger = logging.getLogger("scrape.new_sources.infor")

BASE = "https://www.infor.pl"
SOURCE_NAME = "infor.pl"

# Sub-categories pod /prawo/prawa-konsumenta/. Wszystkie z faktycznej struktury site.
SUBCATS = [
    "reklamacja",
    "gwarancja",
    "rekojmia",
    "umowa-sprzedazy",
    "umowa-konsumencka",
    "odpowiedzialnosc-sprzedawcy",
    "zwrot-towaru",
    "praktyki-rynkowe",
    "kredyt-konsumencki",
    "uslugi-finansowe",
    "ochrona-konsumentow",
    "sprzedaz-internetowa",
    "telefon-internet",
    "uslugi-bankowe",
    "energia",
    "ubezpieczenia",
    "uslugi-turystyczne",
    "sprzedaz-poza-lokalem",
    "klauzule-niedozwolone",
    "umowy-konsumenckie",
]
MAX_PAGES = 8

# Article URL pattern: /prawo/prawa-konsumenta/<sub>/<id>,<slug>.html
ARTICLE_RE = re.compile(
    r"/prawo/prawa-konsumenta/[\w-]+/\d+,[\w-]+\.html"
)


def discover_article_urls(fetcher: Fetcher) -> list[str]:
    seen: set[str] = set()
    for sub in SUBCATS:
        for pg in range(1, MAX_PAGES + 1):
            url = f"{BASE}/prawo/prawa-konsumenta/{sub}/" if pg == 1 else f"{BASE}/prawo/prawa-konsumenta/{sub}/{pg}/"
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
            logger.info("sub=%s page=%d: +%d (total %d)", sub, pg, new, len(seen))
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

    # Extract subcategory from URL
    m = re.search(r"/prawo/prawa-konsumenta/([\w-]+)/", url)
    sub = m.group(1) if m else "ogolne"

    slug = slug_from_title(title, 50)
    aid = f"infor_{idx:04d}_{slug}"
    return ArticleRecord(
        article_id=aid,
        source=SOURCE_NAME,
        source_url=url,
        title=title,
        subtitle=subtitle,
        author=author,
        publication_date=pubdate,
        tresc=body,
        category=f"prawa-konsumenta/{sub}",
        tags=[sub],
        extracted_citations=cites,
        license=LICENSE_FAIR_USE,
        scrape_date=SCRAPE_DATE,
        metadata={"char_count": len(body), "subcategory": sub},
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
        f"Walk {len(SUBCATS)} podkategorii prawa-konsumenta × {MAX_PAGES} stron. "
        f"Article URL pattern: /prawo/prawa-konsumenta/<sub>/NNNNNN,SLUG.html"
    )

    write_jsonl_articles(records, output_dir / "articles.jsonl")
    write_manifest(manifest, output_dir / "_manifest.json")
    write_summary(summary, output_dir / "_summary.json")
    write_failed_log(failed, output_dir / "_failed.log")
    write_readme(
        output_dir,
        SOURCE_NAME,
        f"{BASE}/prawo/prawa-konsumenta/",
        LICENSE_FAIR_USE,
        f"{len(SUBCATS)} podkategorii + paginacja",
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
