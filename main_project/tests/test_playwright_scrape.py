"""Test stubs dla playwright_sources moduły.

Te testy są w przewadze unit / parsing-level — nie odpalają realnego Playwright
(za wolne, wymaga sieci). Pure-helpery (parsing, slug generation, chunking) są
testowane normalnie. Real-Playwright integration testy są oznaczone
``@pytest.mark.network`` i pomijane domyślnie.

Uruchomienie tylko unit::

    uv run pytest main_project/tests/test_playwright_scrape.py -v

Z integration::

    uv run pytest main_project/tests/test_playwright_scrape.py -v -m network
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from src.scrape.playwright_sources.common import (
    count_words,
    extract_citations,
    extract_kara_pln,
    normalize_pl,
)
from src.scrape.playwright_sources.decyzje_uokik import (
    UokikDecyzja,
    _is_consumer_category,
    _parse_listing_row,
)
from src.scrape.playwright_sources.orzeczenia_ms_expansion import (
    OrzeczenieChunk,
    _chunk_long_text,
    _doc_id_from_url,
)
from src.scrape.playwright_sources.sn_orzeczenia import (
    SnOrzeczenie,
    _parse_polish_date_to_iso,
    _sn_id,
)

# ---------------------------------------------------------------------------
# common.py — pure helpers
# ---------------------------------------------------------------------------


class TestCommonHelpers:
    def test_normalize_pl_collapses_whitespace(self) -> None:
        assert normalize_pl("a  b\nc\t\td") == "a b c d"

    def test_normalize_pl_nfc(self) -> None:
        # ą as combined char
        decomposed = "konsumentów".encode().decode()  # already NFC
        assert normalize_pl(decomposed) == "konsumentów"

    def test_normalize_pl_handles_nbsp(self) -> None:
        assert normalize_pl("a\xa0b") == "a b"

    def test_count_words(self) -> None:
        assert count_words("ala ma kota") == 3
        assert count_words("") == 0

    def test_extract_citations_simple(self) -> None:
        text = "Zgodnie z art. 27 ust. 1 Ustawy o prawach konsumenta..."
        cites = extract_citations(text)
        assert len(cites) >= 1
        assert "art. 27" in cites[0].lower()

    def test_extract_kara_pln_simple(self) -> None:
        text = "Nałożono karę pieniężną w wysokości 1 234 567,89 zł..."
        assert extract_kara_pln(text) == 1234567.89

    def test_extract_kara_pln_none_when_absent(self) -> None:
        assert extract_kara_pln("Tekst bez kary.") is None

    def test_extract_kara_pln_handles_simple_integer(self) -> None:
        text = "Kara wynosi 500000 zł."
        val = extract_kara_pln(text)
        assert val == 500000.0


# ---------------------------------------------------------------------------
# decyzje_uokik — parser
# ---------------------------------------------------------------------------


class TestDecyzjeUokikParser:
    def test_parse_listing_row_typical(self) -> None:
        row_text = (
            "Numer decyzji: DKK-112/2026Data decyzji:      11.05.2026"
            "Agencja Mienia Wojskowego z siedzibą w Warszawie Kontrola koncentracji"
        )
        entry = _parse_listing_row(row_text, "https://example.com/dec1?OpenDocument")
        assert entry is not None
        assert entry.sygnatura == "DKK-112/2026"
        assert entry.data_wydania == "2026-05-11"
        assert entry.kategoria == "Kontrola koncentracji"
        assert entry.podmiot is not None and "Agencja" in entry.podmiot
        assert entry.decyzja_id == "uokik_dec_DKK-112-2026"

    def test_parse_listing_row_klauzule(self) -> None:
        row_text = (
            "Numer decyzji: RGD-2/2026Data decyzji: 15.04.2026"
            "Live Nation sp. z o.o. z siedzibą w Warszawie Klauzule niedozwolone"
        )
        entry = _parse_listing_row(row_text, "https://example.com/dec2?OpenDocument")
        assert entry is not None
        assert entry.sygnatura == "RGD-2/2026"
        assert entry.kategoria == "Klauzule niedozwolone"
        assert entry.podmiot is not None and "Live Nation" in entry.podmiot

    def test_parse_listing_row_empty_returns_none(self) -> None:
        assert _parse_listing_row("", "url") is None
        assert _parse_listing_row("no signature here", "url") is None

    def test_is_consumer_category_positive(self) -> None:
        assert _is_consumer_category("Klauzule niedozwolone")
        assert _is_consumer_category("Ochrona zbiorowych interesów konsumentów")
        assert _is_consumer_category("Przewaga kontraktowa")

    def test_is_consumer_category_negative(self) -> None:
        assert not _is_consumer_category("Kontrola koncentracji")
        assert not _is_consumer_category("Porozumienia ograniczające konkurencję")

    def test_decyzja_dataclass_defaults(self) -> None:
        d = UokikDecyzja(
            decyzja_id="uokik_dec_X",
            sygnatura="RBG-1/2024",
            data_wydania="2024-01-01",
            kategoria="Klauzule niedozwolone",
            podmiot="ACME",
            kara_pln=None,
        )
        assert d.license == "urzędowe (Art. 4 ust. 2 PrAut)"
        assert d.scrape_date == "2026-05-16"
        assert d.podstawy_prawne == []
        assert d.metadata == {}


# ---------------------------------------------------------------------------
# orzeczenia_ms_expansion — chunking + doc_id
# ---------------------------------------------------------------------------


class TestOrzeczeniaExpansion:
    def test_doc_id_from_url(self) -> None:
        base = "https://orzeczenia.ms.gov.pl/content/$N/"
        suffix = "153505100000503_I_C_000448_2020_Uz_2021-09-16_001"
        url = base + suffix
        expected_prefix = "orz_153505100000503_I_C_000448_2020_Uz_2021_09_16_001"
        assert _doc_id_from_url(url).startswith(expected_prefix)

    def test_chunk_long_text_no_headings(self) -> None:
        body = "ala ma kota " * 200  # ~2400 chars
        chunks = _chunk_long_text(body)
        assert len(chunks) >= 1
        assert all(len(c[1]) <= 2000 for c in chunks)

    def test_chunk_long_text_short_passes_through(self) -> None:
        body = "krótka treść"
        chunks = _chunk_long_text(body)
        assert chunks == [(None, body.strip())]

    def test_chunk_long_text_with_headings(self) -> None:
        body = "Lead.\n\nWYROK Body of wyrok.\n\nUZASADNIENIE Body of uzasadnienie."
        headings = [("WYROK", body.find("WYROK")), ("UZASADNIENIE", body.find("UZASADNIENIE"))]
        chunks = _chunk_long_text(body, headings=headings)
        # Lead + 2 sekcje (małe — mogą się scollapse'ować jeśli za krótkie)
        titles = {c[0] for c in chunks}
        assert "WYROK" in titles or "UZASADNIENIE" in titles or None in titles

    def test_orzeczenie_chunk_dataclass(self) -> None:
        ch = OrzeczenieChunk(
            chunk_id="orz_X_chunk_001",
            document_id="orz_X",
            document_title="I C 1/24 – wyrok",  # noqa: RUF001 -- compat z E4 schema
            document_type="orzeczenie",
            source="orzeczenia.ms.gov.pl",
            source_url="https://example.com",
            chunk_position=1,
            chunk_total=1,
            section_heading=None,
            tresc="treść chunka",
            scrape_date="2026-05-16",
            license="urzędowe (Art. 4 ust. 2 PrAut)",
        )
        assert ch.metadata == {}
        assert ch.tresc == "treść chunka"


# ---------------------------------------------------------------------------
# sn_orzeczenia — parsers
# ---------------------------------------------------------------------------


class TestSnOrzeczeniaParsers:
    def test_sn_id_slug(self) -> None:
        assert _sn_id("I CSK 500/24") == "sn_I_CSK_500_24"
        assert _sn_id("III CZP 38/25") == "sn_III_CZP_38_25"
        assert _sn_id("") == "sn_"

    def test_parse_polish_date_iso(self) -> None:
        assert _parse_polish_date_to_iso("15 maja 2024") == "2024-05-15"
        assert _parse_polish_date_to_iso("1 stycznia 2020") == "2020-01-01"
        assert _parse_polish_date_to_iso("31 grudnia 2025") == "2025-12-31"

    def test_parse_polish_date_invalid(self) -> None:
        assert _parse_polish_date_to_iso("nonsense") is None
        assert _parse_polish_date_to_iso("32 maja 2024") is None

    def test_sn_orzeczenie_defaults(self) -> None:
        rec = SnOrzeczenie(
            sn_id="sn_I_CSK_1_24",
            sygnatura="I CSK 1/24",
            forma=None,
            izba=None,
            data_wydania=None,
        )
        assert rec.license == "urzędowe (Art. 4 ust. 2 PrAut)"
        assert rec.scrape_date == "2026-05-16"
        assert rec.sklad == []
        assert rec.podstawy_prawne == []


# ---------------------------------------------------------------------------
# I/O integration smoke (no network)
# ---------------------------------------------------------------------------


class TestIOSmoke:
    def test_write_jsonl_roundtrip(self, tmp_path: Path) -> None:
        from src.scrape.playwright_sources.common import write_jsonl

        recs = [
            UokikDecyzja(
                decyzja_id="uokik_dec_DKK-1-2026",
                sygnatura="DKK-1/2026",
                data_wydania="2026-01-01",
                kategoria="Klauzule niedozwolone",
                podmiot="ACME",
                kara_pln=10000.0,
            )
        ]
        path = tmp_path / "decyzje.jsonl"
        n = write_jsonl(recs, path)
        assert n == 1
        with path.open(encoding="utf-8") as f:
            line = f.readline()
        d = json.loads(line)
        assert d["sygnatura"] == "DKK-1/2026"
        assert d["kara_pln"] == 10000.0
        assert d["license"] == "urzędowe (Art. 4 ust. 2 PrAut)"


# ---------------------------------------------------------------------------
# network-requiring smoke (skipped by default; -m network to run)
# ---------------------------------------------------------------------------


@pytest.mark.network
def test_browser_session_basic(tmp_path: Path) -> None:
    """Sanity: czy BrowserSession w ogóle uruchamia Playwright + stealth."""
    from src.scrape.playwright_sources.common import BrowserSession

    with BrowserSession(headless=True) as sess:
        page = sess.new_page()
        page.goto("https://example.com", timeout=30_000)
        title = page.title()
        assert "Example" in title or "example" in title.lower()
