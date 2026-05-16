"""Banki — regulaminy konsumenckie (top 3 banki PKO, mBank, ING).

Status realny:
- PKO BP: blocked WAF (403) na regulaminy. Skip + record reason.
- mBank: blocked WAF (404 na regulaminy/, captcha). Skip + record reason.
- ING: dostęp do /regulaminy + /indywidualni/tabele-i-regulaminy ✓.

License: T&C bank regulaminy są publicznie dostępne; fair-use Art. 29 PrAut
research (legitymne dla academic NLP).
"""

from __future__ import annotations

import argparse
import json
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

logger = logging.getLogger("scrape.new_sources.banki")

SOURCE_NAME = "banki-consumer (ING + blocked log: PKO/mBank)"

# Banks i ich entrance paths
ING_BASE = "https://www.ing.pl"
ING_ENTRY_PATHS = [
    "/regulaminy",
    "/indywidualni/tabele-i-regulaminy",
    "/indywidualni/tabele-i-regulaminy/regulacje",
    "/indywidualni/tabele-i-regulaminy/regulacje/ochrona-danych-osobowych",
    "/indywidualni/tabele-i-regulaminy/regulacje/polityka-plikow-cookie",
    "/regulamin-serwisu",
    "/dokumenty-fis-i-korporacji/regulaminy-i-komunikaty",
    "/dokumenty-fis-i-korporacji/tabela-oplat-prowizji",
]

PKO_BLOCKED_REASON = "WAF 403 — PKO blocks bot UA; would need Playwright + interactive CAPTCHA"
MBANK_BLOCKED_REASON = "WAF 404 — mBank blocks /regulaminy paths via bot detection"


def discover_ing_urls(fetcher: Fetcher) -> list[str]:
    seen: set[str] = set()
    queue: list[tuple[str, int]] = [(urljoin(ING_BASE, p), 0) for p in ING_ENTRY_PATHS]
    while queue:
        url, depth = queue.pop(0)
        if url in seen or depth >= 3:
            continue
        seen.add(url)
        resp = fetcher.get(url)
        if resp is None or resp.status_code != 200:
            continue
        text = resp.content.decode("utf-8", "replace")
        for href in re.findall(r'href="([^"#?]+)"', text):
            href_clean = href.strip()
            if href_clean.startswith("/"):
                full = urljoin(ING_BASE, href_clean)
            elif href_clean.startswith(ING_BASE):
                full = href_clean
            else:
                continue
            # Only consumer-relevant paths
            path = full[len(ING_BASE):]
            if any(
                kw in path.lower()
                for kw in (
                    "regulamin",
                    "tabel",
                    "klient",
                    "dla-klient",
                    "indywidualn",
                    "polityka",
                    "umowa",
                    "wzor",
                    "reklamacj",
                )
            ):
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

    slug = slug_from_title(title, 50)
    aid = f"ing_{idx:04d}_{slug}"
    return ArticleRecord(
        article_id=aid,
        source="ing.pl",
        source_url=url,
        title=title,
        subtitle=subtitle,
        author=None,
        publication_date=pubdate,
        tresc=body,
        category="bank-regulaminy",
        tags=["bank", "regulamin", "ing"],
        extracted_citations=cites,
        license=LICENSE_FAIR_USE,
        scrape_date=SCRAPE_DATE,
        metadata={"char_count": len(body), "bank": "ING"},
    )


def scrape(output_dir: Path, max_articles: int | None) -> ScrapeSummary:
    output_dir.mkdir(parents=True, exist_ok=True)
    archive_dir = output_dir / "_archive"
    fetcher = Fetcher(rate_limit_sec=1.5)

    urls = discover_ing_urls(fetcher)
    logger.info("ING discovered %d URLs", len(urls))
    if max_articles:
        urls = urls[:max_articles]

    records: list[ArticleRecord] = []
    manifest: list[dict] = []
    failed: list[tuple[str, str]] = [
        ("https://www.pkobp.pl/klienci-indywidualni/regulaminy/", PKO_BLOCKED_REASON),
        ("https://www.mbank.pl/regulaminy/", MBANK_BLOCKED_REASON),
    ]
    summary = ScrapeSummary(
        source=SOURCE_NAME,
        license=LICENSE_FAIR_USE,
        discovered_urls=len(urls),
        notes=(
            "ING accessible (8 entry paths + BFS depth 3). PKO BP blocked WAF 403. "
            "mBank blocked WAF 404. Tylko ING zostaje w corpus."
        ),
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

    # Save also blocked.json for transparency
    blocked = {
        "pko_bp": {
            "url": "https://www.pkobp.pl/klienci-indywidualni/",
            "reason": PKO_BLOCKED_REASON,
            "notes": (
                "WAF blokuje bot UA. Workaround wymagałby Playwright headful + "
                "manual CAPTCHA solve. Skip per academic time budget."
            ),
        },
        "mbank": {
            "url": "https://www.mbank.pl/regulaminy/",
            "reason": MBANK_BLOCKED_REASON,
            "notes": (
                "mBank regulaminy URLs returning 404 dla bot UA. Same workaround."
            ),
        },
    }
    (output_dir / "blocked.json").write_text(
        json.dumps(blocked, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    write_jsonl_articles(records, output_dir / "articles.jsonl")
    write_manifest(manifest, output_dir / "_manifest.json")
    write_summary(summary, output_dir / "_summary.json")
    write_failed_log(failed, output_dir / "_failed.log")
    write_readme(
        output_dir,
        SOURCE_NAME,
        ING_BASE,
        LICENSE_FAIR_USE,
        "ING BFS walk regulaminy + blocked.json dla PKO/mBank",
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
