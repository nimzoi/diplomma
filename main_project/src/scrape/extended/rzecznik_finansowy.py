"""Rzecznik Finansowy (rf.gov.pl) FAQ scraper.

Pobiera Q&A z 23 kategorii FAQ na rf.gov.pl/edukacja/baza-wiedzy/.../faq/.
Każda strona to Bootstrap accordion (`.accordion > .accordion-item >
.accordion-header + .accordion-collapse`).

License: rf.gov.pl jest urzędem państwowym (państwowa osoba prawna).
Materiały urzędowe są wyłączone z prawa autorskiego (Art. 4 PrAut),
więc treść FAQ traktujemy jako public-domain-equivalent dla research use.

Output: rzecznik_finansowy_faq.jsonl + meta.

Usage::

    uv run python -m src.scrape.extended.rzecznik_finansowy \\
        --output ../data/raw/extended_consumer_2026-05-16
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

from scrape.extended.common import (  # noqa: E402
    TODAY,
    Fetcher,
    QARecord,
    ScrapeStats,
    extract_citations,
    normalize_pl,
    write_jsonl,
    write_stats,
)

logger = logging.getLogger("scrape.extended.rf")

BASE = "https://rf.gov.pl"
FAQ_INDEX_URL = f"{BASE}/edukacja/baza-wiedzy/najczestsze-pytania-i-odpowiedzi-faq/"

# Pre-discovered FAQ category slugs (od WebFetch eksploracji 2026-05-16).
# Te jako alternatywa jeśli auto-discovery z indexu zawodzi.
FALLBACK_FAQ_SLUGS: tuple[str, ...] = (
    "transakcje-nieautoryzowane",
    "spor-frankowy-droga-sadowa-i-mediacyjna",
    "postepowanie-egzekucyjne",
    "wczesniejsza-splata-kredytow-w-pytaniach-i-odpowiedziach",
    "wakacje-kredytowe-20222023",
    "wakacje-kredytowe-2024-r",
    "rachunek-darmowy-jako-moje-prawo",
    "konto-mieszkaniowe",
    "bezpieczny-kredyt-2",
    "umowy-cesji-w-sprawach-ubezpieczeniowych",
    "ubezpieczenie-turystyczne-w-pytaniach-i-odpowiedziach",
    "ubezpieczenia-szkolne-pytania-i-odpowiedzi",
    "ubezpieczenia-dla-motocyklistow",
    "21529-2",  # rowerowe — niestandardowy slug
    "nnw-dla-studentow-i-inne-ubezpieczenia-dla-mlodziezy-akademickiej",
    "podstawowe-wskazowki-po-szkodzie-pozarowej",
    "odszkodowanie-po-wichurach",
    "odszkodowania-po-powodziach-i-podtopieniach",
    "poszkodowani-w-wypadkach-drogowych-i-ich-bliscy",
    "upadlosc-gnb-informacje-dotyczace-zglaszania-wierzytelnosci",
    "malzenstwo-a-finanse",
    "dziecko-a-pieniadze",
    "finanse-po-smierci-czlonka-rodziny",
    "seniorzy-a-pieniadze",
    "bledny-przelew",
)

LICENSE = "urzędowe — Art. 4 PrAut (Rzecznik Finansowy, państwowa osoba prawna)"


def discover_faq_pages(fetcher: Fetcher) -> dict[str, str]:
    """Wyłuskaj wszystkie linki do podstron FAQ z głównego indexu."""
    resp = fetcher.get(FAQ_INDEX_URL)
    if resp is None:
        logger.warning("FAQ index fetch failed — using fallback list")
        return {slug: f"{FAQ_INDEX_URL}{slug}/" for slug in FALLBACK_FAQ_SLUGS}

    soup = BeautifulSoup(resp.content, "lxml")
    pages: dict[str, str] = {}
    for a in soup.select("a"):
        href = a.get("href", "")
        text = normalize_pl(a.get_text(" ", strip=True))
        if not href.startswith(FAQ_INDEX_URL):
            continue
        if href == FAQ_INDEX_URL:
            continue
        # Strip trailing slash for slug
        slug = href.rstrip("/").rsplit("/", 1)[-1]
        if slug and slug not in pages and text:
            pages[slug] = href

    if not pages:
        logger.warning("FAQ auto-discovery empty — using fallback list")
        return {slug: f"{FAQ_INDEX_URL}{slug}/" for slug in FALLBACK_FAQ_SLUGS}
    return pages


def parse_faq_page(
    html: str, category_slug: str, source_url: str
) -> list[QARecord]:
    """Wyciągnij Q&A pairs z accordion na stronie FAQ."""
    soup = BeautifulSoup(html, "lxml")
    pairs: list[QARecord] = []

    # Category title (z H1)
    h1 = soup.select_one("h1")
    category_title = normalize_pl(h1.get_text(" ", strip=True)) if h1 else category_slug

    # Look for accordion items
    items = soup.select(".accordion .accordion-item")
    if not items:
        # Fallback: try other selectors
        items = soup.select(".elementor-accordion-item, .toggle-item, .qa-item")

    for idx, item in enumerate(items, start=1):
        header = item.select_one(".accordion-header") or item.select_one("h3") or item.select_one(".toggle-title")
        body = item.select_one(".accordion-collapse") or item.select_one(".accordion-body") or item.select_one(".toggle-content")
        if not header or not body:
            continue
        q = normalize_pl(header.get_text(" ", strip=True))
        # Strip leading "N. " enumeration
        q = re.sub(r"^\d+\.\s*", "", q)
        a = normalize_pl(body.get_text(" ", strip=True))
        if len(q) < 5 or len(a) < 20:
            continue

        cit = extract_citations(a)
        qa_id = f"rf_faq_{category_slug}_{idx:03d}"
        pairs.append(
            QARecord(
                qa_id=qa_id,
                question=q,
                answer=a,
                cited_articles=cit,
                category=category_title,
                source="rf.gov.pl",
                source_url=source_url,
                license=LICENSE,
                scrape_date=TODAY,
                metadata={"category_slug": category_slug},
            )
        )

    return pairs


def scrape_all(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher()

    pages = discover_faq_pages(fetcher)
    logger.info("discovered %d FAQ category pages", len(pages))

    all_pairs: list[QARecord] = []
    per_cat: dict[str, int] = {}

    for slug, url in pages.items():
        logger.info("=== %s -> %s", slug, url)
        resp = fetcher.get(url)
        if resp is None:
            continue
        pairs = parse_faq_page(resp.content.decode("utf-8", "replace"), slug, url)
        logger.info("  %d Q&A pairs", len(pairs))
        if pairs:
            per_cat[pairs[0].category] = len(pairs)
            all_pairs.extend(pairs)

    total_chars = sum(len(p.answer) for p in all_pairs)
    with_cit = sum(1 for p in all_pairs if p.cited_articles)
    stats = ScrapeStats(
        source="rf.gov.pl",
        scrape_date=TODAY,
        license=LICENSE,
        total_records=len(all_pairs),
        records_with_citations=with_cit,
        avg_text_length=round(total_chars / max(1, len(all_pairs)), 1),
        categories=per_cat,
        notes=(
            f"{len(pages)} kategorii FAQ; accordion parsing (.accordion .accordion-item). "
            "Content urzędowy (Art. 4 PrAut). UWAGA: zakres tematyczny RF to finanse "
            "(banki, ubezpieczenia, kredyty), NIE klasyczne prawo konsumenta — "
            "uznawane za consumer-adjacent."
        ),
    )

    write_jsonl(all_pairs, output_dir / "rzecznik_finansowy_faq.jsonl")
    write_stats(stats, output_dir / "rzecznik_finansowy_faq_meta.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
    )
    scrape_all(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
