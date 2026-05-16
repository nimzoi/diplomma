"""Sąd Najwyższy "Baza orzeczeń" via Playwright (SharePoint form).

Bazuje na SharePoint backend `sn.pl/wyszukiwanie/SitePages/orzeczenia.aspx`
(199k orzeczeń SN łącznie). Strategia:

1. Wypełnij ``TextBoxTresc`` (full-text phrase) consumer-related query.
2. Wybierz Izba = "Izba Cywilna" (najbardziej relevantna dla consumer rights).
3. Submit (``ButtonSearch``) → SharePoint POST + result page.
4. Pobierz każdy wynik result page; ekstrahuj sygnaturę, datę, sentencję,
   uzasadnienie, powołane przepisy.

Output:

    data/raw/sn_orzeczenia_2026-05-16/
        sn_orzeczenia.jsonl          -- każdy rekord = full orzeczenie
        sn_<sygnatura>.meta.json     -- per-orzeczenie meta sidecar
        _snapshots/                  -- HTML snapshots (debug, gitignored)

License: urzędowe (Art. 4 ust. 2 PrAut).

Fallback gdy SharePoint zablokuje: spróbuj ``Najnowsze_orzeczenia.aspx?Izba=Cywilna``
listing (sprawdzony bez WAF).

Usage::

    uv run python -m src.scrape.playwright_sources.sn_orzeczenia \\
        --output ../data/raw/sn_orzeczenia_2026-05-16 \\
        --max-records 100
"""

from __future__ import annotations

import argparse
import contextlib
import logging
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from playwright.sync_api import Page

from .common import (
    LICENSE_URZEDOWE,
    SCRAPE_DATE,
    BrowserSession,
    ScrapeStats,
    count_words,
    extract_citations,
    normalize_pl,
    write_meta,
)

logger = logging.getLogger("sn_orzeczenia")

SEARCH_URL = "http://www.sn.pl/wyszukiwanie/SitePages/orzeczenia.aspx"
NAJNOWSZE_URL = "http://www.sn.pl/orzecznictwo/SitePages/Najnowsze_orzeczenia.aspx"

# Konsumencko-relewantne phrases.
DEFAULT_PHRASES = [
    "konsument",
    "rękojmia konsumencka",
    "klauzula niedozwolona",
    "kredyt konsumencki",
    "umowa konsumencka",
    "abuzywność postanowień",
    "frankowicze",  # produkty bankowe konsumenckie
    "niedozwolone postanowienia umowne",
]

MIN_DOCUMENT_WORDS = 100  # SN sentencje krótkie, niskie min


@dataclass
class SnOrzeczenie:
    """Pełne SN orzeczenie."""

    sn_id: str  # slug (np. "sn_I_CSK_500_24")
    sygnatura: str  # np. "I CSK 500/24"
    forma: str | None  # np. "wyrok SN" / "uchwała SN" / "postanowienie SN"
    izba: str | None  # np. "Izba Cywilna"
    data_wydania: str | None
    sklad: list[str] = field(default_factory=list)  # sędziowie
    przewodniczacy: str | None = None
    sprawozdawca: str | None = None
    teza: str = ""  # sentencja / teza
    uzasadnienie: str = ""  # body
    podstawy_prawne: list[str] = field(default_factory=list)
    citation_string: str = ""
    scrape_date: str = SCRAPE_DATE
    source_url: str = ""
    license: str = LICENSE_URZEDOWE
    metadata: dict[str, Any] = field(default_factory=dict)


_SYG_PARSE_RE = re.compile(
    r"^\s*([IVXC]+\s+[A-Za-z]+\s+\d+/\d+)", re.IGNORECASE
)

_FORM_FIELD_TRESC = "input[id*='TextBoxTresc']"
_FORM_FIELD_IZBA = "select[id*='DropDownListIzba']"
_FORM_BTN_SEARCH = "input[id*='ButtonSearch']"


def _sn_id(sygnatura: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "_", sygnatura).strip("_")
    return f"sn_{slug[:80]}"


def _search_sn(
    page: Page, phrase: str, *, izba: str = "Izba Cywilna", max_pages: int = 5
) -> list[str]:
    """Wypełnij formularz + iteruj wyniki.

    Returns: lista URLi orzeczeń.
    """
    logger.info("SN search phrase=%r izba=%r", phrase, izba)
    if not page.goto(SEARCH_URL, timeout=60_000):
        return []
    with contextlib.suppress(Exception):
        page.wait_for_load_state("networkidle", timeout=15_000)
    page.wait_for_timeout(2_000)

    # Fill phrase.
    try:
        page.fill(_FORM_FIELD_TRESC, phrase, timeout=15_000)
    except Exception as exc:
        logger.warning("  fill phrase failed: %s", exc)
        return []

    # Select Izba.
    try:
        # ASPxClientCombo lub plain select.
        sel = page.query_selector(_FORM_FIELD_IZBA)
        if sel:
            page.select_option(_FORM_FIELD_IZBA, label=izba, timeout=10_000)
    except Exception as exc:
        logger.warning("  select izba failed: %s (continuing without filter)", exc)

    # Submit.
    try:
        page.click(_FORM_BTN_SEARCH, timeout=15_000)
    except Exception as exc:
        logger.warning("  submit failed: %s", exc)
        return []
    with contextlib.suppress(Exception):
        page.wait_for_load_state("networkidle", timeout=30_000)
    page.wait_for_timeout(3_000)

    urls: set[str] = set()
    for pg in range(max_pages):
        # SN result links typically are "/orzeczenia/SitePages/orzeczenia.aspx?ItemSID=..."
        # albo "/sites/orzecznictwo/..." z ItemSID.
        page_urls = page.eval_on_selector_all(
            "a[href*='ItemSID']",
            "els => Array.from(new Set(els.map(e => e.href)))",
        )
        for u in page_urls:
            urls.add(u)

        # Próbuj kliknąć "Następna" pagination button (SharePoint pagination).
        clicked = False
        for sel in [
            "a:has-text('Następna')",
            "a:has-text('Next')",
            "a[title*='Następna']",
            "img[alt*='Następna']",
            "input[value*='Następna']",
        ]:
            try:
                btn = page.query_selector(sel)
                if btn:
                    btn.click(timeout=10_000)
                    with contextlib.suppress(Exception):
                        page.wait_for_load_state("networkidle", timeout=15_000)
                    page.wait_for_timeout(2_000)
                    clicked = True
                    break
            except Exception:
                continue
        if not clicked:
            logger.info("  no next page button, stopping at page %d", pg + 1)
            break

    result = sorted(urls)
    logger.info("  SN search → %d unique URLs", len(result))
    return result


def _harvest_najnowsze(page: Page, izba: str = "Cywilna", max_items: int = 200) -> list[str]:
    """Fallback: SN Najnowsze orzeczenia dla wybranej Izby.

    Bezformularzowe — direct URL z parametrem.
    """
    url = f"{NAJNOWSZE_URL}?Izba={izba}"
    logger.info("SN najnowsze GET %s", url)
    if not page.goto(url, timeout=60_000):
        return []
    with contextlib.suppress(Exception):
        page.wait_for_load_state("networkidle", timeout=15_000)
    page.wait_for_timeout(3_000)
    items = page.eval_on_selector_all(
        "a[href*='ItemSID']",
        "els => Array.from(new Set(els.map(e => e.href)))",
    )
    return items[:max_items]


def _scrape_sn_orzeczenie_page(page: Page, url: str) -> SnOrzeczenie | None:
    """Pobierz pojedyncze SN orzeczenie + parse meta + tezę + uzasadnienie.

    Strategia:
    1. Fetch metadata page (``orzeczenia.aspx?ItemSID=...``).
    2. Wykryj "pobierz treść orzeczenia w wersji HTML" link → fetch HTML
       (export z DOCX) zawierający pełną treść wyroku/postanowienia.
    3. Jeśli HTML nie istnieje — fallback do tekstu z metadata page.
    """
    if not page.goto(url, timeout=60_000):
        return None
    with contextlib.suppress(Exception):
        page.wait_for_load_state("networkidle", timeout=15_000)
    page.wait_for_timeout(2_000)

    # Metadata text z aktualnej strony (przyda się na sygnaturę/datę/etc.).
    meta_text = ""
    try:
        for sel in [
            "#contentBox",
            "#WebPartWPQ2",
            "#contentRow",
            "main",
            ".ms-rtestate-field",
            "table.ms-rteTableEvenRow-default",
        ]:
            node = page.query_selector(sel)
            if node:
                txt = normalize_pl(node.inner_text() or "")
                if len(txt) > len(meta_text):
                    meta_text = txt
        if not meta_text:
            meta_text = normalize_pl(page.locator("body").inner_text())
    except Exception as exc:
        logger.warning("  meta extract failed for %s: %s", url, exc)
        try:
            meta_text = normalize_pl(page.locator("body").inner_text())
        except Exception:
            return None

    # Spróbuj znaleźć HTML treść link i pobrać pełną zawartość.
    html_text = ""
    try:
        html_links: list[str] = page.eval_on_selector_all(
            "a[href*='OrzeczeniaHTML'], a[href*='.docx.html'], a[href$='.html']",
            "els => els.map(e => e.href)",
        )
        for link in html_links:
            if "OrzeczeniaHTML" in link or link.endswith(".docx.html"):
                # Open w new page (lekkie — sekwencyjne).
                try:
                    sub_resp = page.request.get(link, timeout=60_000)
                    if sub_resp.status == 200:
                        html_body = sub_resp.text()
                        # Wyciągnij text z HTML-DOCX export'u (zwykły HTML
                        # zachowuje strukturę paragrafów). Użyj prostego
                        # stripper'a — chcemy raw text wyroku.
                        import re as _re

                        text = _re.sub(r"<[^>]+>", " ", html_body)
                        text = normalize_pl(text)
                        if len(text) > len(html_text):
                            html_text = text
                            break
                except Exception as exc:
                    logger.debug("  html fetch failed for %s: %s", link, exc)
    except Exception as exc:
        logger.debug("  html link discovery failed: %s", exc)

    # Wybierz dłuższy text jako body_text (preferuje HTML jeśli > 500 chars).
    body_text = html_text if len(html_text) > max(500, len(meta_text)) else meta_text
    if not body_text or len(body_text) < 100:
        return None

    # Sygnatura — szukamy w h1/h2/title/meta i body.
    title = ""
    with contextlib.suppress(Exception):
        title = normalize_pl(page.title())
    sygnatura = ""
    for sel in ("h1", "h2", "h3"):
        h_node = page.query_selector(sel)
        if h_node:
            h_text = normalize_pl(h_node.inner_text() or "")
            m = _SYG_PARSE_RE.search(h_text)
            if m:
                sygnatura = m.group(1).strip()
                break
    if not sygnatura:
        # Wyciągnij z tytułu strony.
        m = re.search(r"\b([IVXC]+\s+[A-Za-z]+(?:\s*[a-z]+)?\s+\d+/\d+)\b", title)
        if m:
            sygnatura = m.group(1)
    if not sygnatura:
        # Z meta_text (sekcja "Sygnatura sprawy w Sądzie Najwyższym X").
        m = re.search(
            r"Sygnatura\s+sprawy\s+w\s+Sądzie\s+Najwyższym\s+([IVXC]+\s+[A-Za-z]+(?:\s*[a-z]+)?\s+\d+/\d+)",
            meta_text,
        )
        if m:
            sygnatura = m.group(1).strip()
    if not sygnatura:
        # Z body_text (HTML treść może zawierać sygnaturę na top).
        m = re.search(r"\b([IVXC]+\s+[A-Za-z]+(?:\s*[a-z]+)?\s+\d+/\d+)\b", body_text[:1000])
        if m:
            sygnatura = m.group(1).strip()
    if not sygnatura:
        # Z HTML link path: "i csk 5489-22.docx.html" → "I CSK 5489/22"
        try:
            for h in page.eval_on_selector_all(
                "a[href*='OrzeczeniaHTML']", "els => els.map(e => e.href)"
            ):
                m = re.search(
                    r"/([A-Za-z]+[%20\s]+[A-Za-z]+[%20\s]+\d+-\d+)\.docx?\.html",
                    h,
                )
                if m:
                    raw = m.group(1).replace("%20", " ").upper().replace("-", "/")
                    sygnatura = re.sub(r"\s+", " ", raw).strip()
                    break
        except Exception:
            pass
    if not sygnatura:
        # Z URL — fallback (ItemSID).
        sygnatura = url.split("ItemSID=")[-1].split("&")[0][:40]

    # Forma + Izba + data — heurystycznie.
    forma_match = re.search(
        r"\b(wyrok|uchwała|postanowienie|zarządzenie)\s+(?:SN|Sądu\s+Najwyższego)\b",
        body_text[:1000],
        re.IGNORECASE,
    )
    forma = forma_match.group(0) if forma_match else None
    izba_match = re.search(
        r"Izba\s+(Cywilna|Karna|Pracy|Wojskowa|Administracyjna|Dyscyplinarna"
        r"|Kontroli\s+Nadzwyczajnej|Odpowiedzialności\s+Zawodowej)",
        body_text[:2000],
    )
    izba = ("Izba " + izba_match.group(1)) if izba_match else None
    date_match = re.search(
        r"\b(\d{1,2}\s+(?:stycznia|lutego|marca|kwietnia|maja|czerwca|lipca"
        r"|sierpnia|września|października|listopada|grudnia)\s+\d{4})",
        body_text[:2000],
    )
    data_wydania: str | None = None
    if date_match:
        # spróbuj sparsować na ISO; ale ostrożnie — może w body być wiele dat.
        data_wydania = _parse_polish_date_to_iso(date_match.group(1))
    if not data_wydania:
        date_match2 = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", body_text[:2000])
        if date_match2:
            data_wydania = date_match2.group(1)

    # Skład / przewodniczący / sprawozdawca — opcjonalne pattern matche.
    name_chars = r"A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż\s.-"
    sklad: list[str] = []
    for label in ("Przewodniczący", "Sprawozdawca", "Sędziowie", "SSN"):
        regex = rf"{label}[:\s]+([A-ZĄĆĘŁŃÓŚŹŻ][{name_chars}]+?)(?:[\n,;]|\s{{2,}})"
        for m in re.finditer(regex, body_text[:3000]):
            name = m.group(1).strip()
            if 5 < len(name) < 60 and name not in sklad:
                sklad.append(name)
    przewodniczacy_m = re.search(
        rf"Przewodnicz[aą]cy[:\s]+([A-ZĄĆĘŁŃÓŚŹŻ][{name_chars}]{{4,40}})",
        body_text[:2000],
    )
    przewodniczacy = przewodniczacy_m.group(1).strip() if przewodniczacy_m else None
    sprawozdawca_m = re.search(
        rf"Sprawozdawca[:\s]+([A-ZĄĆĘŁŃÓŚŹŻ][{name_chars}]{{4,40}})",
        body_text[:2000],
    )
    sprawozdawca = sprawozdawca_m.group(1).strip() if sprawozdawca_m else None

    # Teza vs uzasadnienie — szukamy headerów.
    teza, uzasadnienie = "", ""
    teza_match = re.search(
        r"(Teza|TEZA|Sentencja|SENTENCJA)\s*:?\s*(.+?)(?=UZASADNIENIE|Uzasadnienie|\Z)",
        body_text,
        re.IGNORECASE | re.DOTALL,
    )
    if teza_match:
        teza = teza_match.group(2).strip()[:5000]
    uz_match = re.search(
        r"(UZASADNIENIE|Uzasadnienie)\s*:?\s*(.+)$",
        body_text,
        re.IGNORECASE | re.DOTALL,
    )
    if uz_match:
        uzasadnienie = uz_match.group(2).strip()
    if not teza and not uzasadnienie:
        # No structure found — całość jako uzasadnienie (treść).
        uzasadnienie = body_text

    podstawy = extract_citations(body_text)

    sn_id = _sn_id(sygnatura)
    citation_str = (
        f"Sąd Najwyższy, {forma or 'orzeczenie'} z dnia "
        f"{data_wydania or 'n.d.'}, sygn. {sygnatura}. {url}"
    )

    return SnOrzeczenie(
        sn_id=sn_id,
        sygnatura=sygnatura,
        forma=forma,
        izba=izba,
        data_wydania=data_wydania,
        sklad=sklad[:10],
        przewodniczacy=przewodniczacy,
        sprawozdawca=sprawozdawca,
        teza=normalize_pl(teza),
        uzasadnienie=normalize_pl(uzasadnienie),
        podstawy_prawne=podstawy[:50],
        citation_string=citation_str,
        source_url=url,
        metadata={
            "word_count": count_words(body_text),
            "extracted_citation_count": len(podstawy),
        },
    )


_POLISH_MONTHS = {
    "stycznia": 1, "lutego": 2, "marca": 3, "kwietnia": 4, "maja": 5,
    "czerwca": 6, "lipca": 7, "sierpnia": 8, "września": 9, "wrzesnia": 9,
    "października": 10, "pazdziernika": 10, "listopada": 11, "grudnia": 12,
}


def _parse_polish_date_to_iso(s: str) -> str | None:
    s = s.lower().strip()
    m = re.match(r"(\d{1,2})\s+([a-ząćęłńóśźż]+)\s+(\d{4})", s)
    if not m:
        return None
    day = int(m.group(1))
    month_name = m.group(2)
    year = int(m.group(3))
    month = _POLISH_MONTHS.get(month_name)
    if not month:
        return None
    try:
        from datetime import date

        return date(year, month, day).isoformat()
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# main entry
# ---------------------------------------------------------------------------


def scrape_sn_orzeczenia(
    output_dir: Path,
    *,
    phrases: list[str] | None = None,
    max_records: int = 100,
    max_per_phrase: int = 30,
    max_pages_per_phrase: int = 5,
    headless: bool = True,
    use_fallback: bool = True,
    skip_existing: bool = True,
) -> ScrapeStats:
    """Główny entry point."""
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshots_dir = output_dir / "_snapshots"
    snapshots_dir.mkdir(parents=True, exist_ok=True)

    phrases = phrases or DEFAULT_PHRASES
    stats = ScrapeStats(source="sn.pl", license=LICENSE_URZEDOWE)
    records: list[SnOrzeczenie] = []
    seen_urls: set[str] = set()
    existing_ids: set[str] = set()
    if skip_existing:
        existing_ids = {p.stem for p in output_dir.glob("sn_*.meta.json")}
        logger.info("pre-existing SN docs: %d", len(existing_ids))

    with BrowserSession(headless=headless) as sess:
        page = sess.new_page()

        url_pool: list[str] = []
        # Phase 1a — formularz search.
        for phrase in phrases:
            sess.throttle()
            try:
                phrase_urls = _search_sn(page, phrase, max_pages=max_pages_per_phrase)
            except Exception as exc:
                logger.warning("phrase search failed: %s", exc)
                phrase_urls = []
            for u in phrase_urls[:max_per_phrase]:
                if u not in seen_urls:
                    seen_urls.add(u)
                    url_pool.append(u)

        # Phase 1b — fallback listing if puste.
        if use_fallback and len(url_pool) < 10:
            logger.info("URL pool small (%d); using Najnowsze Cywilna fallback", len(url_pool))
            sess.throttle()
            try:
                fb = _harvest_najnowsze(page, izba="Cywilna", max_items=max_records)
                for u in fb:
                    if u not in seen_urls:
                        seen_urls.add(u)
                        url_pool.append(u)
            except Exception as exc:
                logger.warning("najnowsze fallback failed: %s", exc)

        # Hard cap.
        url_pool = url_pool[:max_records]
        stats.attempted = len(url_pool)
        logger.info("scraping %d SN URLs", len(url_pool))

        # Phase 2 — scrape per-orzeczenie.
        for url in url_pool:
            sess.throttle()
            try:
                rec = _scrape_sn_orzeczenie_page(page, url)
            except Exception as exc:
                logger.warning("SN page parse failed for %s: %s", url, exc)
                stats.failed += 1
                stats.parse_errors += 1
                continue
            if rec is None or not (rec.teza or rec.uzasadnienie):
                stats.failed += 1
                stats.skip_reasons["empty"] = stats.skip_reasons.get("empty", 0) + 1
                continue
            if rec.sn_id in existing_ids:
                stats.skipped += 1
                stats.skip_reasons["already_exists"] = (
                    stats.skip_reasons.get("already_exists", 0) + 1
                )
                continue
            words = count_words(rec.uzasadnienie + " " + rec.teza)
            if words < MIN_DOCUMENT_WORDS:
                stats.skipped += 1
                stats.skip_reasons["too_short"] = stats.skip_reasons.get("too_short", 0) + 1
                continue
            records.append(rec)
            write_meta(output_dir / f"{rec.sn_id}.meta.json", rec)
            stats.succeeded += 1
            stats.total_words += words
            logger.info(
                "  scraped SN %s (%s, %s, %d words, %d citations)",
                rec.sn_id,
                rec.sygnatura,
                rec.izba or "?",
                words,
                len(rec.podstawy_prawne),
            )

    # Idempotent merge: read existing jsonl + sidecar meta.json files + new records.
    jsonl_path = output_dir / "sn_orzeczenia.jsonl"
    import dataclasses as _dc
    import json as _json

    merged: dict[str, dict[str, Any]] = {}
    if jsonl_path.exists():
        with jsonl_path.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = _json.loads(line)
                    merged[d["sn_id"]] = d
                except Exception:
                    continue
    for rec in records:
        merged[rec.sn_id] = _dc.asdict(rec)
    for meta_file in output_dir.glob("sn_*.meta.json"):
        with meta_file.open(encoding="utf-8") as f:
            try:
                d = _json.load(f)
                merged.setdefault(d["sn_id"], d)
            except Exception:
                continue
    with jsonl_path.open("w", encoding="utf-8") as f:
        for d in merged.values():
            f.write(_json.dumps(d, ensure_ascii=False, default=str) + "\n")
    logger.info(
        "wrote %d SN records → %s (new this run: %d, total inc existing: %d)",
        len(merged),
        jsonl_path,
        len(records),
        len(merged),
    )
    stats.notes += f"jsonl_total_records={len(merged)}; new_this_run={len(records)}; "
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-records", type=int, default=100)
    parser.add_argument("--max-per-phrase", type=int, default=30)
    parser.add_argument("--max-pages-per-phrase", type=int, default=5)
    parser.add_argument("--phrases", nargs="*", default=None)
    parser.add_argument("--no-fallback", action="store_true")
    parser.add_argument("--no-skip-existing", action="store_true")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s | %(message)s",
        stream=sys.stderr,
    )

    output_dir = args.output.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    stats = scrape_sn_orzeczenia(
        output_dir,
        phrases=args.phrases,
        max_records=args.max_records,
        max_per_phrase=args.max_per_phrase,
        max_pages_per_phrase=args.max_pages_per_phrase,
        headless=not args.headed,
        use_fallback=not args.no_fallback,
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
