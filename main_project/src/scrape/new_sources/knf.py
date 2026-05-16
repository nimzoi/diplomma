"""KNF — Komisja Nadzoru Finansowego, sekcja konsument finansowy.

Discovery: sitemap (sitemap.xml index 380KB+). Filter na URLs zawierające
``/dla_konsumenta`` lub ``/konsument`` lub ``/dla_rynku/...`` slot consumer-relevant.

License: urzędowe (Art. 4 ust. 2 PrAut — KNF organ państwowy).
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from pathlib import Path

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
    fetch_sitemap_urls,
    persist_raw_html,
    slug_from_title,
    write_failed_log,
    write_jsonl_articles,
    write_manifest,
    write_readme,
    write_summary,
)

logger = logging.getLogger("scrape.new_sources.knf")

BASE = "https://www.knf.gov.pl"
SOURCE_NAME = "knf.gov.pl"
SITEMAP = f"{BASE}/sitemap.xml"

CONSUMER_PATH_PREFIXES = (
    "/dla_konsumenta",
    "/dla_rynku/przeciwdzialanie_naduzyciom_na_rynku_finansowym",
    "/dla_rynku/edukacja",
    "/knf/edukacja",
    "/aktualnosci",
)


def discover_article_urls(fetcher: Fetcher) -> list[str]:
    urls = fetch_sitemap_urls(fetcher, SITEMAP)
    keep = []
    seen = set()
    for u in urls:
        if not u.startswith(BASE):
            continue
        # Keep all KNF pages — KNF is small enough that filtering może być zbyt
        # restrictive. Ale skip clearly non-consumer (np. /publikacje/biuletyn-statystyczny).
        if u in seen:
            continue
        seen.add(u)
        path = u[len(BASE):]
        # Prefer consumer-prefixed paths
        if any(path.startswith(p) for p in CONSUMER_PATH_PREFIXES):
            keep.append(u)
        elif any(kw in path.lower() for kw in ("konsument", "edukac", "ostrzezen", "lista_ostrzezen")):
            keep.append(u)
    return keep


def parse_article(html: str, url: str, idx: int) -> ArticleRecord | None:
    soup = BeautifulSoup(html, "lxml")
    clean_soup(soup)
    title = extract_title(soup)
    body = extract_main_text(soup)
    if len(body) < 200:
        return None
    pubdate = detect_pubdate(soup, html)
    subtitle = extract_subtitle(soup)
    cites = extract_citations(body)

    m = re.match(r"https://www\.knf\.gov\.pl/([\w-]+)", url)
    section = m.group(1) if m else "ogolne"

    slug = slug_from_title(title, 50)
    aid = f"knf_{idx:04d}_{slug}"
    return ArticleRecord(
        article_id=aid,
        source=SOURCE_NAME,
        source_url=url,
        title=title,
        subtitle=subtitle,
        author=None,
        publication_date=pubdate,
        tresc=body,
        category=section,
        tags=[section],
        extracted_citations=cites,
        license=LICENSE_URZEDOWE,
        scrape_date=SCRAPE_DATE,
        metadata={"char_count": len(body), "section": section},
    )


def scrape(output_dir: Path, max_articles: int | None) -> ScrapeSummary:
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = output_dir / "_archive"
    fetcher = Fetcher(rate_limit_sec=0.8)

    urls = discover_article_urls(fetcher)
    logger.info("discovered %d consumer-relevant URLs", len(urls))
    if max_articles:
        urls = urls[:max_articles]

    records: list[ArticleRecord] = []
    manifest: list[dict] = []
    failed: list[tuple[str, str]] = []
    summary = ScrapeSummary(
        source=SOURCE_NAME, license=LICENSE_URZEDOWE, discovered_urls=len(urls)
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
        f"Sitemap walk z filter na {len(CONSUMER_PATH_PREFIXES)} path prefixes konsument-relevant."
    )

    write_jsonl_articles(records, output_dir / "articles.jsonl")
    write_manifest(manifest, output_dir / "_manifest.json")
    write_summary(summary, output_dir / "_summary.json")
    write_failed_log(failed, output_dir / "_failed.log")
    write_readme(
        output_dir,
        SOURCE_NAME,
        BASE,
        LICENSE_URZEDOWE,
        "Sitemap walk + filter consumer/edukacja paths",
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
