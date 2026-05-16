"""Gov.pl konsumencki content scraper.

Pobiera oficjalne strony konsumenckie z `gov.pl/web/gov/*` i
`gov.pl/web/sprawiedliwosc/dla-obywatela/*`. Lista kuratorska zidentyfikowana
podczas exploration 2026-05-16.

License: urzędowe (Art. 4 PrAut). Materiały rządowe.

Output: gov_pl_consumer.jsonl + meta.

Usage::

    uv run python -m src.scrape.extended.gov_pl_consumer \\
        --output ../data/raw/extended_consumer_2026-05-16
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scrape.extended.common import (
    TODAY,
    EncyclopedicChunk,
    Fetcher,
    ScrapeStats,
    extract_citations,
    normalize_pl,
    write_jsonl,
    write_stats,
)

logger = logging.getLogger("scrape.extended.gov_pl")

BASE = "https://www.gov.pl"

# Kurated lista — confirmed via WebFetch 2026-05-16. Wszystkie istnieją i mają
# substantywny konsumencki content.
GOV_PAGES: tuple[tuple[str, str], ...] = (
    ("Prawa konsumenta - portal informacyjny", "/web/gov/prawa-konsumenta-portal-informacyjny"),
    ("Pomoc dla konsumentów", "/web/gov/skorzystaj-z-pomocy-dla-konsumentow"),
    ("Mediacja w sporach", "/web/gov/rozwiaz-spor-przez-mediacje"),
    ("Darmowa pomoc prawna", "/web/gov/skorzystaj-z-darmowej-pomocy-prawnej"),
    (
        "Zawiadomienie o braku dostepnosci",
        "/web/gov/zloz-zawiadomienie-o-braku-dostepnosci-produktu-lub-uslugi",
    ),
)

LICENSE = "urzędowe — Art. 4 PrAut (gov.pl, materiały rządowe)"
MIN_BODY_CHARS = 200


def parse_page(
    html: str, source_url: str, title_fallback: str, idx: int
) -> EncyclopedicChunk | None:
    soup = BeautifulSoup(html, "lxml")
    for sel in ["nav", "footer", ".header", ".breadcrumbs", ".social", ".share", "header"]:
        for el in soup.select(sel):
            el.decompose()

    # H1
    h1 = soup.select_one("h1")
    title = normalize_pl(h1.get_text(" ", strip=True)) if h1 else title_fallback

    # Body — gov.pl uses .editor-content for actual article body. Stron typu
    # "wizard" mają wiele tabów (każdy = osobny .editor-content). Łączymy wszystkie.
    editor_blocks = soup.select(".editor-content")
    if not editor_blocks:
        intro = soup.select_one(".intro")
        if intro:
            editor_blocks = [intro]
    if not editor_blocks:
        return None

    parts: list[str] = []
    seen_para: set[str] = set()
    for block in editor_blocks:
        for el in block.select("p, li, h2, h3, h4"):
            txt = normalize_pl(el.get_text(" ", strip=True))
            if (
                len(txt) >= 15
                and txt not in seen_para
                and not txt.startswith(("Skopiuj", "Udostępnij"))
            ):
                parts.append(txt)
                seen_para.add(txt)

    body = "\n".join(parts)
    if len(body) < MIN_BODY_CHARS:
        return None

    # Heurystyka anti-homepage-redirect: gov.pl homepage zwiera "Załatwiaj sprawy urzędowe"
    if "Załatwiaj sprawy urzędowe" in body[:200] and "kupionym towarem" not in body:
        return None

    return EncyclopedicChunk(
        chunk_id=f"gov_pl_{idx:03d}_{source_url.rstrip('/').rsplit('/', 1)[-1][:40]}",
        source="gov.pl",
        source_url=source_url,
        title=title,
        section=None,
        tresc=body,
        license=LICENSE,
        scrape_date=TODAY,
        metadata={
            "cited_articles": extract_citations(body),
            "elements_count": len(parts),
        },
    )


def scrape_all(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fetcher = Fetcher()
    chunks: list[EncyclopedicChunk] = []
    failed = 0

    for idx, (label, path) in enumerate(GOV_PAGES, start=1):
        url = BASE + path
        logger.info("[%d/%d] %s -> %s", idx, len(GOV_PAGES), label, url)
        resp = fetcher.get(url)
        if resp is None:
            logger.warning("  fetch failed")
            failed += 1
            continue
        chunk = parse_page(resp.content.decode("utf-8", "replace"), url, label, idx)
        if chunk is None:
            logger.warning("  parse: too short")
            failed += 1
            continue
        chunks.append(chunk)

    total_chars = sum(len(c.tresc) for c in chunks)
    with_cit = sum(1 for c in chunks if c.metadata.get("cited_articles"))
    stats = ScrapeStats(
        source="gov.pl",
        scrape_date=TODAY,
        license=LICENSE,
        total_records=len(chunks),
        records_with_citations=with_cit,
        avg_text_length=round(total_chars / max(1, len(chunks)), 1),
        categories={"konsumencki_gov": len(chunks)},
        notes=(
            f"Kurated lista {len(GOV_PAGES)} stron rządowych konsumenckich; "
            f"{failed} failures. Strony krótkie (350-500 słów each) — "
            "supplementary do main UOKiK portal."
        ),
    )

    write_jsonl(chunks, output_dir / "gov_pl_consumer.jsonl")
    write_stats(stats, output_dir / "gov_pl_consumer_meta.json")


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
