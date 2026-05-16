"""Federacja Konsumentów porady scraper.

Pobiera artykuły z `federacja-konsumentow.org.pl/Strefa konsumenta/`. Tree-walk
od top-level category pages (Sprzedaż konsumencka, Usługi, Moje finanse, etc.)
do individual articles (URL pattern: `n,<parent>,<id>,100,1,<slug>.html`).

License: site nie eksponuje explicit CC license — treść Federacji Konsumentów
(stowarzyszenie konsumenckie, NGO). Używamy fair-use research framing
(Art. 29 PrAut "prawo cytatu") dla research dataset. Long-form chunks
trzymamy w original form ale tagujemy ``license="research-fair-use"``.

Output: federacja_konsumentow.jsonl + meta.

Usage::

    uv run python -m src.scrape.extended.federacja_konsumentow \\
        --output ../data/raw/extended_consumer_2026-05-16 \\
        --max-articles 200
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
    EncyclopedicChunk,
    Fetcher,
    ScrapeStats,
    extract_citations,
    normalize_pl,
    write_jsonl,
    write_stats,
)

logger = logging.getLogger("scrape.extended.federacja")

BASE = "https://www.federacja-konsumentow.org.pl"

# Top-level category pages w "Strefa konsumenta" — manually curated z exploration.
# Każda zawiera linki do podstron z poradami (URL pattern: NNN,slug.html lub
# n,NNN,NNN,100,1,slug.html dla articles).
TOP_CATEGORIES: dict[str, str] = {
    "Strefa konsumenta": "/31,strefa-konsumenta.html",
    "Moje finanse": "/161,moje-finanse.html",
    "Umowa": "/173,umowa.html",
    "Rachunek bankowy": "/169,rachunek-bankowy.html",
    "Polisolokaty": "/165,polisolokaty.html",
    "Upadłość konsumencka": "/167,upadlosc-konsumencka.html",
    "Windykacja": "/168,windykacja.html",
    "Ubezpieczenia (moje finanse)": "/199,ubezpieczenia.html",
    "Sprzedaż konsumencka": "/39,sprzedaz-konsumencka.html",
    "Warto wiedzieć": "/195,warto-wiedziec.html",
    "Rękojmia, jak korzystać": "/196,rekojmia-jak-korzystac.html",
    "Reklamacja - i co dalej": "/197,reklamacja--i-co-dalej.html",
    "Gwarancja": "/198,gwarancja.html",
    "Usługi": "/41,uslugi.html",
    "Tryb dochodzenia roszczeń": "/40,tryb-dochodzenia-roszczen.html",
    "Usługi finansowe": "/38,uslugi-finansowe.html",
    "Ubezpieczenia": "/50,ubezpieczenia.html",
    "Telefon, Internet, telewizja": "/46,telefon-internet-telewizja.html",
    "Sprzedaż poza lokalem przedsiębiorstwa": "/42,sprzedaz-poza-lokalem-przedsiebiorstwa.html",
    "Sprzedaż na odległość": "/43,sprzedaz-na-odleglosc.html",
    "Zakupy w Internecie": "/45,zakupy-w-internecie.html",
    "Sprzedaż wysyłkowa": "/44,sprzedaz-wysylkowa.html",
    "Usługi turystyczne": "/49,uslugi-turystyczne.html",
    "Rynek energii": "/186,energia-elektryczna-i-gaz.html",
    "Dane osobowe": "/226,dane-osobowe.html",
    "Artykuły spożywcze": "/51,artykuly-spozywcze.html",
    "Bezpieczny produkt": "/48,bezpieczny-produkt.html",
    "Dzieci": "/47,dzieci.html",
}

# Article URL pattern: starts with "n," (article) or NNN,slug.html (subcategory).
ARTICLE_RE = re.compile(r"^n,\d+,\d+,\d+,\d+,[\w-]+\.html$")
SUBCATEGORY_RE = re.compile(r"^\d+,[\w-]+\.html$")

LICENSE = "fair-use research (Federacja Konsumentów porady — NGO, attribution preserved)"

MIN_ARTICLE_CHARS = 200


def discover_article_links(fetcher: Fetcher) -> list[tuple[str, str, str]]:
    """Walk category pages, return [(category_label, article_url, link_text)].

    BFS — one level deep z TOP_CATEGORIES. Article pages mają linki w div#content.
    """
    seen_urls: set[str] = set()
    results: list[tuple[str, str, str]] = []

    for label, path in TOP_CATEGORIES.items():
        url = BASE + path
        logger.info("category: %s -> %s", label, url)
        resp = fetcher.get(url)
        if resp is None:
            logger.warning("  fetch failed")
            continue
        soup = BeautifulSoup(resp.content, "lxml")
        content = soup.select_one("div#content")
        if content is None:
            logger.warning("  no #content div")
            continue

        for a in content.select("a"):
            href = a.get("href", "").strip()
            text = normalize_pl(a.get_text(" ", strip=True))
            if not href or href == "#" or href.startswith("http"):
                continue
            # Strip leading slash
            href_clean = href.lstrip("/")
            full_url = urljoin(BASE + "/", href_clean)
            # Only accept article-pattern URLs (n,...) — subcategories pomijamy
            # bo i tak są w TOP_CATEGORIES albo discovered via parent.
            if not ARTICLE_RE.match(href_clean):
                continue
            if full_url in seen_urls:
                continue
            seen_urls.add(full_url)
            results.append((label, full_url, text or "(no text)"))

    logger.info("discovered %d unique article URLs across %d categories", len(results), len(TOP_CATEGORIES))
    return results


def parse_article(html: str, source_url: str, category: str, article_idx: int) -> EncyclopedicChunk | None:
    """Wyciągnij title + body z artykułu Federacji."""
    soup = BeautifulSoup(html, "lxml")
    content = soup.select_one("div#content")
    if content is None:
        return None

    # Title — pierwszy h1/h2 w content. Strip breadcrumb prefix.
    title_el = content.select_one("h1, h2")
    title = normalize_pl(title_el.get_text(" ", strip=True)) if title_el else "(no title)"

    # Remove breadcrumb nav and "Opublikowano:" meta
    for sel in [".breadcrumb", ".breadcrumbs", "nav", ".meta"]:
        for el in content.select(sel):
            el.decompose()

    # Pull paragraphs only — ignore navigation lists at bottom.
    paragraphs = []
    for p in content.select("p"):
        txt = normalize_pl(p.get_text(" ", strip=True))
        if txt and len(txt) > 20:
            paragraphs.append(txt)
    body = "\n".join(paragraphs)

    if len(body) < MIN_ARTICLE_CHARS:
        return None

    # Slug
    slug = re.sub(r"\W+", "_", title.lower()).strip("_")[:60] or "untitled"
    chunk_id = f"fed_kons_{article_idx:04d}_{slug}"

    return EncyclopedicChunk(
        chunk_id=chunk_id,
        source="federacja-konsumentow.org.pl",
        source_url=source_url,
        title=title,
        section=category,
        tresc=body,
        license=LICENSE,
        scrape_date=TODAY,
        metadata={
            "cited_articles": extract_citations(body),
            "paragraphs_count": len(paragraphs),
        },
    )


def scrape_all(output_dir: Path, max_articles: int | None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher()

    article_links = discover_article_links(fetcher)
    if max_articles:
        logger.info("limiting to first %d articles", max_articles)
        article_links = article_links[:max_articles]

    chunks: list[EncyclopedicChunk] = []
    per_category: dict[str, int] = {}
    failed = 0

    for idx, (cat, url, text) in enumerate(article_links, start=1):
        logger.info("[%d/%d] %s | %s", idx, len(article_links), cat, text[:60])
        resp = fetcher.get(url)
        if resp is None:
            failed += 1
            continue
        chunk = parse_article(resp.content.decode("utf-8", "replace"), url, cat, idx)
        if chunk is None:
            logger.warning("  parse: too short / no content")
            failed += 1
            continue
        chunks.append(chunk)
        per_category[cat] = per_category.get(cat, 0) + 1

    total_chars = sum(len(c.tresc) for c in chunks)
    with_cit = sum(1 for c in chunks if c.metadata.get("cited_articles"))
    stats = ScrapeStats(
        source="federacja-konsumentow.org.pl",
        scrape_date=TODAY,
        license=LICENSE,
        total_records=len(chunks),
        records_with_citations=with_cit,
        avg_text_length=round(total_chars / max(1, len(chunks)), 1),
        categories=per_category,
        notes=(
            f"Tree-walk od {len(TOP_CATEGORIES)} top categories; {len(article_links)} "
            f"discovered article URLs; {failed} failures. License: brak explicit CC; "
            "framing: research/fair-use, attribution w source_url + metadata."
        ),
    )

    write_jsonl(chunks, output_dir / "federacja_konsumentow.jsonl")
    write_stats(stats, output_dir / "federacja_konsumentow_meta.json")


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
    scrape_all(args.output.resolve(), args.max_articles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
