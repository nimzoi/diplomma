"""Scraper Decyzji Prezesa UOKiK przez Playwright (F5 WAF bypass).

Bazuje on Lotus Notes endpoint `decyzje.uokik.gov.pl/bp/dec_prez.nsf` —
``OpenView`` widoki paginowane + per-decyzja ``OpenDocument`` page z linkiem
do PDF (``$FILE``).

Strategia:

1. Iterujemy paginowany widok ``decyzje?OpenView&Start=N`` (chunks po 30 rows).
2. Z każdego wiersza wyciągamy: numer decyzji (DKK/DOK/RBG/RKR/...), datę,
   podmiot, kategorię (z TR tekstu po dacie), URL do dokumentu.
3. Open document page → wyciąga link do PDF ``$FILE``.
4. PDF pobierany przez page.request (Playwright HTTP client — używa tej
   samej WAF cookies session) i parsowany ``pdfplumber``.

Output:

    data/raw/uokik_decyzje_2026-05-16/
        decyzje.jsonl              -- wszystkie decyzje
        <decyzja_id>.meta.json     -- per-decyzja meta
        _snapshots/                -- HTML/PDF dla debug (gitignored)
        scrape_summary.json

Filter kategorii (consumer-focused): "Klauzule niedozwolone", "Ochrona
zbiorowych interesów konsumentów", "Przewaga kontraktowa". Reszta (kontrola
koncentracji, kartele) — skipped chyba że ``--no-filter``.

License: urzędowe (Art. 4 ust. 2 PrAut).

Usage::

    uv run python -m src.scrape.playwright_sources.decyzje_uokik \\
        --output ../data/raw/uokik_decyzje_2026-05-16 \\
        --max-records 500
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from io import BytesIO
from pathlib import Path
from typing import Any

import pdfplumber
from playwright.sync_api import Page

# in-package imports
from .common import (
    LICENSE_URZEDOWE,
    SCRAPE_DATE,
    BrowserSession,
    ScrapeStats,
    count_words,
    extract_citations,
    extract_kara_pln,
    normalize_pl,
    save_snapshot,
    write_jsonl,
    write_meta,
)

logger = logging.getLogger("decyzje_uokik")

BASE_URL = "https://decyzje.uokik.gov.pl/bp/dec_prez.nsf/decyzje"
ROWS_PER_PAGE = 30  # Lotus Notes default
MIN_DOCUMENT_WORDS = 200  # ~jedna strona — krótkie decyzje też się liczą

# Kategorie konsumenckie (zawiera substring w TR tekście).
CONSUMER_CATEGORIES = (
    "Klauzule niedozwolone",
    "Ochrona zbiorowych interesów konsumentów",
    "Ochrona zbiorowych interes",  # NFC variant
    "Przewaga kontraktowa",
    "Ogólne bezpieczeństwo produktów",
    "System oceny zgodności",
    "Jakość paliw",  # konsumencki kontekst — fuel quality
)


# ---------------------------------------------------------------------------
# data model
# ---------------------------------------------------------------------------


@dataclass
class UokikDecyzja:
    """Pełna decyzja UOKiK (URL → PDF metadata + content)."""

    decyzja_id: str  # np. "DKK-112-2026" (slug ze sygnatury)
    sygnatura: str  # np. "DKK-112/2026"
    data_wydania: str | None  # ISO date YYYY-MM-DD lub None
    kategoria: str  # human-readable, np. "Klauzule niedozwolone"
    podmiot: str | None  # nazwa ukaranego/strony postępowania
    kara_pln: float | None
    podstawy_prawne: list[str] = field(default_factory=list)  # extracted citations
    tresc: str = ""  # NFC normalized PDF text
    citation_string: str = ""
    scrape_date: str = SCRAPE_DATE
    source_url: str = ""
    pdf_url: str | None = None
    license: str = LICENSE_URZEDOWE
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class _DecyzjaListEntry:
    """Wewnętrzne — wiersz z OpenView listing."""

    decyzja_id: str
    sygnatura: str
    data_wydania: str | None
    kategoria: str
    podmiot: str | None
    document_url: str


# ---------------------------------------------------------------------------
# parsing helpers
# ---------------------------------------------------------------------------

_SYGN_RE = re.compile(r"Numer\s*decyzji:\s*([A-ZĄĆĘŁŃÓŚŹŻ-]+-\d+/\d{2,4})", re.IGNORECASE)
_DATE_RE = re.compile(r"Data\s*decyzji:\s*(\d{2}\.\d{2}\.\d{4})", re.IGNORECASE)


def _parse_listing_row(row_text: str, doc_href: str) -> _DecyzjaListEntry | None:
    """Sparsuj wiersz Lotus Notes z listing.

    Format::

        "Numer decyzji: DKK-112/2026Data decyzji:      11.05.2026<Podmiot> <Kategoria>"

    Returns None jeśli puste / nie ma sygnatury.
    """
    text = normalize_pl(row_text)
    syg_m = _SYGN_RE.search(text)
    if not syg_m:
        return None
    sygnatura = syg_m.group(1)
    date_m = _DATE_RE.search(text)
    data_iso: str | None = None
    if date_m:
        try:
            data_iso = datetime.strptime(date_m.group(1), "%d.%m.%Y").date().isoformat()
        except ValueError:
            data_iso = None

    # Wycinamy podmiot + kategorię — po dacie decyzji.
    tail = text
    if date_m:
        tail = text[date_m.end() :].strip()
    elif syg_m:
        tail = text[syg_m.end() :].strip()

    # Kategoria: szukamy ostatniego matche'a z CONSUMER_CATEGORIES albo ogólne
    # kategorie UOKiK (kontrola koncentracji, kartele, etc.).
    all_categories = (
        "Klauzule niedozwolone",
        "Ochrona zbiorowych interesów konsumentów",
        "Przewaga kontraktowa",
        "Ogólne bezpieczeństwo produktów",
        "System oceny zgodności",
        "Jakość paliw",
        "Kontrola koncentracji",
        "Nadużywanie pozycji dominującej",
        "Porozumienia ograniczające konkurencję",
        "Zatory Płatnicze",
        "Pozostałe",
    )
    kategoria = "Pozostałe"
    podmiot: str | None = None
    for cat in all_categories:
        if cat in tail:
            idx = tail.rfind(cat)
            kategoria = cat
            podmiot_raw = tail[:idx].strip().rstrip(",;: ")
            podmiot = podmiot_raw or None
            break
    if podmiot is None and tail:
        # Brak kategorii w TR — całość tail = podmiot.
        podmiot = tail.strip() or None

    # Slug ID: replace / with -.
    slug = sygnatura.replace("/", "-").replace(" ", "_")
    decyzja_id = f"uokik_dec_{slug}"

    return _DecyzjaListEntry(
        decyzja_id=decyzja_id,
        sygnatura=sygnatura,
        data_wydania=data_iso,
        kategoria=kategoria,
        podmiot=podmiot,
        document_url=doc_href,
    )


def _is_consumer_category(category: str) -> bool:
    return any(cat in category for cat in CONSUMER_CATEGORIES)


# ---------------------------------------------------------------------------
# scraping logic
# ---------------------------------------------------------------------------


def _harvest_listing_page(page: Page, start: int) -> list[_DecyzjaListEntry]:
    """Otwiera ``decyzje?OpenView&Start=N`` i zwraca listę wpisów."""
    url = f"{BASE_URL}?OpenView&Start={start}"
    logger.info("listing GET start=%d", start)
    if not page.goto(url, timeout=60_000):
        logger.warning("  listing failed at start=%d", start)
        return []
    # Networkidle nie zawsze działa (WAF JS spins forever); użyj timeout.
    try:
        page.wait_for_load_state("networkidle", timeout=15_000)
    except Exception:
        pass
    page.wait_for_timeout(2_000)
    # Wszystkie OpenDocument linki w TR.
    items: list[dict[str, str]] = page.eval_on_selector_all(
        "tr a[href*='OpenDocument']",
        """els => els.map(e => ({
            href: e.href,
            tr_text: e.closest('tr')?.textContent?.trim() || ''
        }))""",
    )
    # Dedup po URL (każdy TR ma kilka linków).
    seen_urls: set[str] = set()
    rows: list[_DecyzjaListEntry] = []
    for it in items:
        href = it["href"]
        if href in seen_urls:
            continue
        seen_urls.add(href)
        entry = _parse_listing_row(it["tr_text"], href)
        if entry is None:
            continue
        rows.append(entry)
    logger.info("  -> %d valid rows", len(rows))
    return rows


def _fetch_document_pdf_url(page: Page, doc_url: str) -> str | None:
    """Otwiera dokument page → zwraca pierwsze ``$FILE/*.pdf`` link."""
    try:
        if not page.goto(doc_url, timeout=60_000):
            return None
        page.wait_for_timeout(2_000)
        pdf_links: list[str] = page.eval_on_selector_all(
            "a[href*='$FILE'], a[href*='.pdf'], a[href*='$File']",
            "els => els.map(e => e.href).filter(h => h.toLowerCase().endsWith('.pdf'))",
        )
        if not pdf_links:
            # Some decyzje mają attachments bez .pdf extension — bierzemy pierwszy $FILE.
            pdf_links = page.eval_on_selector_all(
                "a[href*='$FILE'], a[href*='$File']",
                "els => els.map(e => e.href)",
            )
        return pdf_links[0] if pdf_links else None
    except Exception as exc:
        logger.warning("  fetch_document_pdf_url failed: %s", exc)
        return None


def _download_pdf(page: Page, pdf_url: str) -> bytes | None:
    """Pobierz PDF bytes używając ``page.request`` (zachowuje session/cookies)."""
    try:
        resp = page.request.get(pdf_url, timeout=120_000)
        if resp.status != 200:
            logger.warning("  PDF status %d for %s", resp.status, pdf_url)
            return None
        body = resp.body()
        if not body.startswith(b"%PDF"):
            logger.warning("  not a PDF (first bytes=%r)", body[:8])
            return None
        return body
    except Exception as exc:
        logger.warning("  PDF download failed: %s", exc)
        return None


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    """pdfplumber → NFC normalized text."""
    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
        full = "\n\n".join(pages)
    except Exception as exc:
        logger.warning("  pdfplumber failed: %s", exc)
        return ""
    return normalize_pl(full)


def _build_citation_string(sygnatura: str, data_wydania: str | None, kategoria: str) -> str:
    parts = [f"Decyzja Prezesa UOKiK sygn. {sygnatura}"]
    if data_wydania:
        parts.append(f"z dnia {data_wydania}")
    parts.append(f"({kategoria})")
    return ", ".join(parts) + "."


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


def scrape_decyzje_uokik(
    output_dir: Path,
    *,
    max_records: int = 500,
    rows_per_page: int = ROWS_PER_PAGE,
    max_pages: int = 50,
    consumer_filter: bool = True,
    headless: bool = True,
    skip_existing: bool = True,
) -> ScrapeStats:
    """Main scraper.

    Args:
        output_dir: docelowy katalog (musi istnieć).
        max_records: kap na liczbę decyzji do scrape'owania.
        rows_per_page: rozmiar paginacji Lotus Notes (zwykle 30).
        max_pages: cap na liczbę stron listing (anti-runaway).
        consumer_filter: jeśli True — bierze tylko ``CONSUMER_CATEGORIES``.
        headless: czy headless browser.
        skip_existing: nie pobieraj ponownie meta jeśli już istnieje.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir = output_dir / "_snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)
    decyzje_records: list[UokikDecyzja] = []
    stats = ScrapeStats(source="decyzje.uokik.gov.pl", license=LICENSE_URZEDOWE)

    with BrowserSession(headless=headless) as sess:
        page = sess.new_page()

        # Step 1 — odkrywamy entries z listingu.
        entries: list[_DecyzjaListEntry] = []
        for page_idx in range(max_pages):
            start = 1 + page_idx * rows_per_page
            sess.throttle()
            page_entries = _harvest_listing_page(page, start)
            if not page_entries:
                logger.info("empty page at start=%d, stopping listing", start)
                break
            entries.extend(page_entries)
            stats.attempted += len(page_entries)
            if len(entries) >= max_records * 2:  # buffer dla consumer filter
                logger.info("collected enough entries (%d), stopping listing", len(entries))
                break

        logger.info("listing complete: %d total entries", len(entries))

        # Step 2 — filter consumer + download.
        if consumer_filter:
            filtered = [e for e in entries if _is_consumer_category(e.kategoria)]
            stats.notes += (
                f"consumer filter: {len(entries)} → {len(filtered)} ({100*len(filtered)/max(len(entries),1):.1f}%); "
            )
            entries = filtered
        # Hard cap.
        entries = entries[:max_records]

        for entry in entries:
            meta_path = output_dir / f"{entry.decyzja_id}.meta.json"
            if skip_existing and meta_path.exists():
                logger.info("skip existing %s", entry.decyzja_id)
                stats.skipped += 1
                stats.skip_reasons["already_exists"] = stats.skip_reasons.get("already_exists", 0) + 1
                continue

            sess.throttle()
            pdf_url = _fetch_document_pdf_url(page, entry.document_url)
            if not pdf_url:
                logger.warning("  no PDF link for %s", entry.sygnatura)
                stats.failed += 1
                stats.skip_reasons["no_pdf_link"] = stats.skip_reasons.get("no_pdf_link", 0) + 1
                continue

            pdf_bytes = _download_pdf(page, pdf_url)
            if pdf_bytes is None:
                stats.failed += 1
                stats.skip_reasons["pdf_download_failed"] = (
                    stats.skip_reasons.get("pdf_download_failed", 0) + 1
                )
                continue

            text = _extract_pdf_text(pdf_bytes)
            words = count_words(text)
            if words < MIN_DOCUMENT_WORDS:
                logger.warning("  too short (%d words) %s", words, entry.sygnatura)
                stats.skipped += 1
                stats.skip_reasons["too_short"] = stats.skip_reasons.get("too_short", 0) + 1
                continue

            podstawy = extract_citations(text)
            kara = extract_kara_pln(text)

            rec = UokikDecyzja(
                decyzja_id=entry.decyzja_id,
                sygnatura=entry.sygnatura,
                data_wydania=entry.data_wydania,
                kategoria=entry.kategoria,
                podmiot=entry.podmiot,
                kara_pln=kara,
                podstawy_prawne=podstawy[:50],  # limit
                tresc=text,
                citation_string=_build_citation_string(
                    entry.sygnatura, entry.data_wydania, entry.kategoria
                ),
                source_url=entry.document_url,
                pdf_url=pdf_url,
                metadata={
                    "pdf_size_bytes": len(pdf_bytes),
                    "word_count": words,
                    "extracted_citation_count": len(podstawy),
                },
            )
            decyzje_records.append(rec)
            write_meta(meta_path, rec)
            stats.succeeded += 1
            stats.total_words += words
            logger.info(
                "  scraped %s [%s, %d words, %d citations, kara=%s]",
                entry.sygnatura,
                entry.kategoria,
                words,
                len(podstawy),
                f"{kara:,.0f} PLN" if kara else "n/a",
            )

    # Append-write głównego JSONL (replace if existed).
    jsonl_path = output_dir / "decyzje.jsonl"
    n = write_jsonl(decyzje_records, jsonl_path)
    logger.info("wrote %d records → %s", n, jsonl_path)
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-records", type=int, default=500)
    parser.add_argument("--max-pages", type=int, default=50)
    parser.add_argument(
        "--no-filter",
        action="store_true",
        help="Wyłącz consumer category filter (default: only consumer-relevant).",
    )
    parser.add_argument(
        "--headed", action="store_true", help="Show browser (debugging only)."
    )
    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Re-download nawet jeśli meta.json istnieje.",
    )
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
        stream=sys.stderr,
    )

    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    stats = scrape_decyzje_uokik(
        output_dir,
        max_records=args.max_records,
        max_pages=args.max_pages,
        consumer_filter=not args.no_filter,
        headless=not args.headed,
        skip_existing=not args.no_skip_existing,
    )

    summary_path = output_dir / "scrape_summary.json"
    import json

    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(stats.as_dict(), f, ensure_ascii=False, indent=2)
    logger.info("=== DONE === %s", stats.as_dict())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
