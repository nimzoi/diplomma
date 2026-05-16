"""KNF — Komisja Nadzoru Finansowego, sekcja konsument finansowy.

Discovery: BFS walk od /dla_konsumenta + /co_robimy/edukacja_finansowa.
(Note: KNF nie ma standard sitemap.xml — endpoint zwraca search HTML.)

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

from urllib.parse import urljoin

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

logger = logging.getLogger("scrape.new_sources.knf")

BASE = "https://www.knf.gov.pl"
SOURCE_NAME = "knf.gov.pl"

ENTRY_PATHS = [
    "/dla_konsumenta",
    "/dla_konsumenta/Ochrona_klienta_na_rynku_uslug_finansowych",
    "/dla_konsumenta/gdzie_szukac_pomocy_w_przypadku_sporu_z_instytucja_finansowa",
    "/dla_konsumenta/Informacja_dotyczaca_otwartych_funduszy_emerytalnych",
    "/dla_konsumenta/kampanie_informacyjne",
    "/co_robimy/edukacja_finansowa",
    "/co_robimy/edukacja_finansowa/Global_Money_Week",
    "/co_robimy/edukacja_finansowa/WIW",
    "/co_robimy/edukacja_finansowa/seminaria_cedur",
    "/dla_konsumenta/Lista_ostrzezen_publicznych_KNF",
    "/dla_konsumenta/Ochrona_klienta_na_rynku_uslug_finansowych/Reklamacje",
]
MAX_DEPTH = 4


def discover_article_urls(fetcher: Fetcher) -> list[str]:
    """BFS walk od /dla_konsumenta + edukacja paths."""
    seen: set[str] = set()
    queue: list[tuple[str, int]] = [(urljoin(BASE, p), 0) for p in ENTRY_PATHS]
    while queue:
        url, depth = queue.pop(0)
        if url in seen or depth >= MAX_DEPTH:
            continue
        seen.add(url)
        resp = fetcher.get(url)
        if resp is None or resp.status_code != 200:
            continue
        text = resp.content.decode("utf-8", "replace")
        for href in re.findall(r'href="(/[^"#?]+)"', text):
            # KNF internal consumer-relevant paths
            if not (
                href.startswith("/dla_konsumenta")
                or href.startswith("/co_robimy/edukacja_finansowa")
                or href.startswith("/aktualnosci")
            ):
                continue
            full = urljoin(BASE, href)
            if full not in seen:
                queue.append((full, depth + 1))
    return sorted(seen)


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
        f"BFS walk od {len(ENTRY_PATHS)} entry paths konsument-relevant, depth max {MAX_DEPTH}."
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
