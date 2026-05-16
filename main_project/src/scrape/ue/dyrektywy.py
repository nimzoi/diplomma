"""Scrape UE dyrektyw konsumenckich z EUR-Lex (polska wersja jezykowa).

Pokrycie (8 dyrektyw, defense argument: pelen consumer law stack):

  1. 32011L0083  — Consumer Rights Directive (CRD) — podstawa polskiej UPK
  2. 32019L0770  — Digital Content Directive (DCD)
  3. 32019L0771  — Sale of Goods Directive (SGD)
  4. 32019L2161  — Omnibus Directive (modernization 4 dyrektyw)
  5. 31993L0013  — Unfair Contract Terms Directive (UCT)
  6. 32005L0029  — Unfair Commercial Practices Directive (UCPD)
  7. 32008L0048  — Consumer Credit Directive (CCD I)
  8. 32023L2225  — CCD II (zastepuje 2008/48)

Strategia ekstraktu:
  - URL HTML: https://eur-lex.europa.eu/legal-content/PL/TXT/HTML/?uri=CELEX:{id}
  - Parser: BeautifulSoup4. Struktura HTML EUR-Lex:
      <p class="oj-ti-art">Artykul N</p>       — naglowek artykulu
      <p class="oj-sti-art">{tytul}</p>        — tytul artykulu (opcjonalny)
      <div id="00X.00Y"> — pojemnik ustepu (X=art, Y=ust)
      <p class="oj-normal">1.   tekst...</p>   — ustep (inline-numbered)
      <table>...<p>a)</p>...<p>tekst lit.</p></table>  — litera
  - Preambula: <p class="oj-normal">(N) tekst...</p>    — motyw

Chunkowanie (analog ELI):
  - Atom = najglebsza tekstowa jednostka (lit / ust / art).
  - Motyw preambuly = osobny chunk (motyw=N, art=None).

License: (c) UE, free reuse per Decyzja 2011/833/UE — attribution required.

Usage::

    uv run python -m src.scrape.ue.dyrektywy           # wszystkie 8
    uv run python -m src.scrape.ue.dyrektywy --celex 32011L0083
    uv run python -m src.scrape.ue.dyrektywy --output ../data/raw/ue_dyrektywy_2026-05-16
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup
from bs4.element import Tag

# Setup PYTHONPATH for direct module execution.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scrape.ue.common import (  # noqa: E402
    LICENSE_EURLEX,
    TODAY,
    EurLexFormats,
    Fetcher,
    ScrapeStats,
    build_citation_directive,
    normalize_inline,
    write_json,
    write_jsonl,
)

logger = logging.getLogger("scrape.ue.dyrektywy")


# === Configuration ===


@dataclass(frozen=True)
class DyrektywaConfig:
    """Per-dyrektywa metadata."""

    celex_id: str  # "32011L0083"
    direktywa_id: str  # "2011/83/UE" — short citation form
    title_pl: str  # for fallback if HTML doesn't expose it cleanly
    data_publikacji: str  # ISO date (Dziennik Urzedowy publication)
    data_wejscia_w_zycie: str  # ISO date
    data_implementacji: str | None  # transposition deadline (None for direct-effect)
    polska_implementacja: str | None  # ELI ID, np. "DU/2014/827"
    notes: str = ""


# 8 dyrektyw konsumenckich (per task brief).
# Daty z EUR-Lex metadata + polska implementacja z ISAP cross-reference.
DYREKTYWY: tuple[DyrektywaConfig, ...] = (
    DyrektywaConfig(
        celex_id="32011L0083",
        direktywa_id="2011/83/UE",
        title_pl=(
            "Dyrektywa Parlamentu Europejskiego i Rady 2011/83/UE z dnia 25 pazdziernika "
            "2011 r. w sprawie praw konsumentow"
        ),
        data_publikacji="2011-11-22",
        data_wejscia_w_zycie="2011-12-12",
        data_implementacji="2013-12-13",
        polska_implementacja="DU/2014/827",
        notes="CRD — Consumer Rights Directive, podstawa polskiej Ustawy o prawach konsumenta",
    ),
    DyrektywaConfig(
        celex_id="32019L0770",
        direktywa_id="2019/770/UE",
        title_pl=(
            "Dyrektywa Parlamentu Europejskiego i Rady (UE) 2019/770 z dnia 20 maja 2019 r. "
            "w sprawie niektorych aspektow umow o dostarczanie tresci cyfrowych i uslug cyfrowych"
        ),
        data_publikacji="2019-05-22",
        data_wejscia_w_zycie="2019-06-11",
        data_implementacji="2021-07-01",
        polska_implementacja="DU/2022/2337",
        notes="DCD — Digital Content Directive, implementowana przez nowelizacje UPK (DU/2022/2337)",
    ),
    DyrektywaConfig(
        celex_id="32019L0771",
        direktywa_id="2019/771/UE",
        title_pl=(
            "Dyrektywa Parlamentu Europejskiego i Rady (UE) 2019/771 z dnia 20 maja 2019 r. "
            "w sprawie niektorych aspektow umow sprzedazy towarow"
        ),
        data_publikacji="2019-05-22",
        data_wejscia_w_zycie="2019-06-11",
        data_implementacji="2021-07-01",
        polska_implementacja="DU/2022/2337",
        notes="SGD — Sale of Goods Directive, implementowana przez nowelizacje UPK (DU/2022/2337)",
    ),
    DyrektywaConfig(
        celex_id="32019L2161",
        direktywa_id="2019/2161/UE",
        title_pl=(
            "Dyrektywa Parlamentu Europejskiego i Rady (UE) 2019/2161 z dnia 27 listopada 2019 r. "
            "zmieniajaca dyrektywe Rady 93/13/EWG i dyrektywy Parlamentu Europejskiego i Rady "
            "98/6/WE, 2005/29/WE oraz 2011/83/UE"
        ),
        data_publikacji="2019-12-18",
        data_wejscia_w_zycie="2020-01-07",
        data_implementacji="2021-11-28",
        polska_implementacja="DU/2022/2581",
        notes=(
            "Omnibus — modernization of 4 directives (93/13, 98/6, 2005/29, 2011/83); "
            "implementowana m.in. przez DU/2022/2581"
        ),
    ),
    DyrektywaConfig(
        celex_id="31993L0013",
        direktywa_id="93/13/EWG",
        title_pl=(
            "Dyrektywa Rady 93/13/EWG z dnia 5 kwietnia 1993 r. w sprawie nieuczciwych warunkow "
            "w umowach konsumenckich"
        ),
        data_publikacji="1993-04-21",
        data_wejscia_w_zycie="1993-04-21",
        data_implementacji="1994-12-31",
        polska_implementacja="DU/1964/93",
        notes=(
            "UCT — Unfair Contract Terms, transponowana do polskiego KC (art. 385^1 i nast.) "
            "ustawa DU/2000/443 wprowadzajaca; centralna w orzecznictwie TSUE (Dziubak, Kasler)"
        ),
    ),
    DyrektywaConfig(
        celex_id="32005L0029",
        direktywa_id="2005/29/WE",
        title_pl=(
            "Dyrektywa 2005/29/WE Parlamentu Europejskiego i Rady z dnia 11 maja 2005 r. "
            "dotyczaca nieuczciwych praktyk handlowych stosowanych przez przedsiebiorstwa "
            "wobec konsumentow na rynku wewnetrznym"
        ),
        data_publikacji="2005-06-11",
        data_wejscia_w_zycie="2005-06-12",
        data_implementacji="2007-06-12",
        polska_implementacja="DU/2007/1206",
        notes="UCPD — Unfair Commercial Practices Directive, transponowana przez DU/2007/1206",
    ),
    DyrektywaConfig(
        celex_id="32008L0048",
        direktywa_id="2008/48/WE",
        title_pl=(
            "Dyrektywa Parlamentu Europejskiego i Rady 2008/48/WE z dnia 23 kwietnia 2008 r. "
            "w sprawie umow o kredyt konsumencki"
        ),
        data_publikacji="2008-05-22",
        data_wejscia_w_zycie="2008-06-11",
        data_implementacji="2010-06-11",
        polska_implementacja="DU/2011/126",
        notes="CCD I — Consumer Credit Directive (zastapiona przez 2023/2225), DU/2011/126",
    ),
    DyrektywaConfig(
        celex_id="32023L2225",
        direktywa_id="2023/2225/UE",
        title_pl=(
            "Dyrektywa Parlamentu Europejskiego i Rady (UE) 2023/2225 z dnia 18 pazdziernika "
            "2023 r. w sprawie umow o kredyt konsumencki oraz uchylajaca dyrektywe 2008/48/WE"
        ),
        data_publikacji="2023-10-30",
        data_wejscia_w_zycie="2023-11-19",
        data_implementacji="2025-11-20",
        polska_implementacja=None,
        notes="CCD II — nowa CCD, transposition deadline 20 list. 2025, polska ustawa w toku",
    ),
)


# === Schema (mirrors halu.schemas.UEDyrektywa) ===


@dataclass
class UEChunk:
    """Single chunk from UE directive (matches Pydantic UEDyrektywa)."""

    chunk_id: str
    celex_id: str
    direktywa_id: str
    direktywa_title_pl: str
    art: str | None
    ust: str | None
    pkt: str | None
    lit: str | None
    motyw: str | None
    tresc: str
    citation_string: str
    license: str
    scrape_date: str
    source_url: str
    metadata: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "celex_id": self.celex_id,
            "direktywa_id": self.direktywa_id,
            "direktywa_title_pl": self.direktywa_title_pl,
            "art": self.art,
            "ust": self.ust,
            "pkt": self.pkt,
            "lit": self.lit,
            "motyw": self.motyw,
            "tresc": self.tresc,
            "citation_string": self.citation_string,
            "license": self.license,
            "scrape_date": self.scrape_date,
            "source_url": self.source_url,
            "metadata": self.metadata,
        }


# === Parser ===


# Pattern for ustep number at start of <p class="oj-normal">: "1.   tekst..." or "1. tekst"
UST_LEAD_RE = re.compile(r"^(\d+[a-z]?)\.\s+(.+)$", re.DOTALL)
# Pattern for motyw preambuly: "(13)" or "(13) "
MOTYW_LEAD_RE = re.compile(r"^\(\s*(\d+[a-z]?)\s*\)\s*(.+)$", re.DOTALL)
# Letter pattern (a) (b) ... or "a)" "b)" (always at start of cell)
LIT_LEAD_RE = re.compile(r"^\(?([a-z]{1,3})\)\s*(.*)$", re.DOTALL)
# Numbered point pattern "1)" "2)" "i)" "ii)" "iii)" (Roman) for sub-list inside lit
PKT_LEAD_RE = re.compile(r"^(\d+|i{1,3}v?|iv|v|vi{1,3}|ix|x)\)\s*(.*)$", re.DOTALL)


def parse_directive_html_legacy(
    html: str, cfg: DyrektywaConfig, source_url: str
) -> list[UEChunk]:
    """Fallback parser dla starych dyrektyw (pre-2004) z TXT_TE flat <p> structure.

    Algorytm:
      1. Strip header (banner/Dziennik Urzedowy info)
      2. Find <p>Artykuł N</p> markers
      3. Between Artykuł markers, collect <p> texts as article body
         - Detect ustep prefix "1.   text" or "1. text"
         - Detect litery "a)" / "(a)" at <p> start
    """
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Get TXT_TE content if available, otherwise fallback to body
    txt_te = soup.find("txt_te")  # legacy element
    if txt_te is None:
        txt_te = soup.find("div", id="TexteOnly")
    if txt_te is None:
        txt_te = soup.body or soup

    # Collect all <p> tags in document order
    paragraphs = txt_te.find_all("p")

    chunks: list[UEChunk] = []
    current_art: str | None = None
    current_ust: str | None = None
    current_ust_lead: str = ""

    # Buffer for non-numbered article body
    buffer: list[str] = []

    art_header_re = re.compile(r"^Artyku(?:l|ł)\s+(\d+[a-z]?)$")
    art_inline_re = re.compile(r"^Artyku(?:l|ł)\s+(\d+[a-z]?)\b")
    motyw_seen: set[str] = set()
    saw_first_art = False

    def emit_buffer() -> None:
        nonlocal buffer, current_art, current_ust, current_ust_lead
        if not buffer or current_art is None:
            buffer = []
            return
        tresc = " ".join(buffer).strip()
        if not tresc or len(tresc) < 10:
            buffer = []
            return
        chunk = _build_chunk(
            art=current_art,
            ust=current_ust,
            pkt=None,
            lit=None,
            motyw=None,
            tresc=tresc,
            cfg=cfg,
            source_url=source_url,
            extra_meta={"ust_lead": current_ust_lead} if current_ust_lead else {},
        )
        chunks.append(chunk)
        buffer = []

    for p in paragraphs:
        text = normalize_inline(p.get_text(" ", strip=True))
        if not text:
            continue

        # Article header (whole-paragraph)
        m = art_header_re.match(text)
        if m:
            emit_buffer()
            current_art = m.group(1)
            current_ust = None
            current_ust_lead = ""
            saw_first_art = True
            continue

        # Skip if before first article (preambula) — try motyw extraction inline
        if not saw_first_art:
            # In legacy old dyrektywa, preambula motywy are paragraphs without numbers,
            # which is too noisy to chunk. Skip (will become meta).
            continue

        # Ustep prefix
        m = UST_LEAD_RE.match(text)
        if m and current_art is not None:
            emit_buffer()
            current_ust = m.group(1)
            current_ust_lead = m.group(2).strip()
            # Some old dyrektyw store ust as standalone chunk
            buffer.append(current_ust_lead)
            continue

        # Otherwise append to buffer
        buffer.append(text)

    emit_buffer()
    return chunks


def parse_directive_html(
    html: str, cfg: DyrektywaConfig, source_url: str
) -> tuple[list[UEChunk], str | None]:
    """Parse EUR-Lex HTML i wytwarz liste UEChunk.

    Zwraca (chunks, observed_title_pl). Title from <p class="doc-ti"> if present,
    fallback to cfg.title_pl.

    Algorithm:
      1. Find <p class="oj-ti-art"> = article header.
      2. Within article, find <div id="NNN.MMM"> = ustep container.
      3. Within ustep:
          - Lead <p class="oj-normal">: extract ustep number from "N. text"
          - Following <table>: each row = a lit. (letter) chunk
            (col 1 = "a)", col 2 = text)
          - Nested table inside lit text = pkt sub-list (rarely needed)
      4. If article has no <div id="NNN.MMM">, treat whole article body as a single
         chunk (ust=None, lit=None).
      5. Preambula motywy: <p class="oj-normal"> z prefixem "(N)" = motyw N.
    """
    soup = BeautifulSoup(html, "html.parser")
    # Strip script/style noise (rare in EUR-Lex but defensive)
    for tag in soup(["script", "style"]):
        tag.decompose()

    chunks: list[UEChunk] = []

    # Extract observed title from <p class="doc-ti"> if present
    title_tag = soup.find("p", class_="doc-ti")
    observed_title = (
        normalize_inline(title_tag.get_text(" ", strip=True)) if title_tag else None
    )

    # === Legacy detection — for old directives (pre-2004) ===
    # If no oj-ti-art class exists, fall back to flat <p> parser.
    if not soup.find("p", class_="oj-ti-art"):
        logger.info("Using legacy parser (no oj-ti-art class) for %s", cfg.celex_id)
        legacy_chunks = parse_directive_html_legacy(html, cfg, source_url)
        return legacy_chunks, observed_title

    # === Preambula motywy ===
    # Motywy są PRZED pierwszym Artykul, w 2-kolumnowej tabeli:
    #   <td><p class="oj-normal">(N)</p></td>
    #   <td><p class="oj-normal">tekst motywu...</p></td>
    # Walk all tables before first oj-ti-art and extract motyw rows.
    first_art = soup.find("p", class_="oj-ti-art")
    motyw_seen: set[str] = set()
    if first_art is not None:
        # Find all tables that precede the first art header in document order
        for table in soup.find_all("table"):
            # Check ordering using sourceline (or by appearance)
            if first_art.sourceline and table.sourceline and table.sourceline >= first_art.sourceline:
                break
            for row in table.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) != 2:
                    continue
                marker = normalize_inline(cells[0].get_text(" ", strip=True))
                body = normalize_inline(cells[1].get_text(" ", strip=True))
                m = re.match(r"^\(\s*(\d+[a-z]?)\s*\)$", marker)
                if not m or len(body) < 10:
                    continue
                motyw_num = m.group(1)
                if motyw_num in motyw_seen:
                    continue
                motyw_seen.add(motyw_num)
                chunk = _build_motyw_chunk(motyw_num, body, cfg, source_url)
                chunks.append(chunk)

    # === Articles ===
    for art_header in soup.find_all("p", class_="oj-ti-art"):
        art_text = normalize_inline(art_header.get_text(" ", strip=True))
        # Extract number from "Artykul N" (or "Artykuł N")
        m = re.match(r"Artyku(?:l|ł)\s+(\d+[a-z]?)", art_text)
        if not m:
            continue
        art_num = m.group(1)

        # Find article container (parent div with id="art_N")
        art_container = art_header.find_parent("div", id=re.compile(r"^art_\d"))
        if art_container is None:
            # Fallback: walk siblings until next article header
            art_container = _collect_article_content_via_siblings(art_header)
            if art_container is None:
                continue

        # Article title (sub-title)
        sti = art_container.find("p", class_="oj-sti-art")
        art_subtitle = (
            normalize_inline(sti.get_text(" ", strip=True)) if sti else None
        )

        # Find all <div id="NNN.MMM"> = ustep containers
        ust_containers = art_container.find_all(
            "div", id=re.compile(r"^\d{3}\.\d{3}$")
        )

        if ust_containers:
            for ust_div in ust_containers:
                _parse_ustep(
                    ust_div, art_num, cfg, source_url, art_subtitle, chunks
                )
        else:
            # Article without numbered ustep — extract single text chunk
            paragraphs = art_container.find_all("p", class_="oj-normal")
            text_parts = []
            for p in paragraphs:
                # Skip the article header itself
                if "oj-ti-art" in (p.get("class") or []):
                    continue
                text_parts.append(normalize_inline(p.get_text(" ", strip=True)))
            tresc = " ".join(text_parts).strip()
            if tresc:
                chunk = _build_chunk(
                    art=art_num,
                    ust=None,
                    pkt=None,
                    lit=None,
                    motyw=None,
                    tresc=tresc,
                    cfg=cfg,
                    source_url=source_url,
                    extra_meta={"art_subtitle": art_subtitle} if art_subtitle else {},
                )
                chunks.append(chunk)

    return chunks, observed_title


def _collect_article_content_via_siblings(art_header: Tag) -> Tag | None:
    """Fallback when article header is not wrapped in <div id='art_N'>.

    Returns a synthetic Tag-like wrapper with everything until next oj-ti-art.
    Not implemented — EUR-Lex always wraps. Return None to signal skip.
    """
    return None


def _parse_ustep(
    ust_div: Tag,
    art_num: str,
    cfg: DyrektywaConfig,
    source_url: str,
    art_subtitle: str | None,
    chunks: list[UEChunk],
) -> None:
    """Parse <div id='NNN.MMM'> = pojedynczy ustep."""
    # First <p class="oj-normal"> = ust lead (with "N." prefix)
    first_p = ust_div.find("p", class_="oj-normal", recursive=False)
    if first_p is None:
        # Sometimes nested in <div>
        first_p = ust_div.find("p", class_="oj-normal")

    ust_num: str | None = None
    ust_lead_text: str = ""
    if first_p is not None:
        text = normalize_inline(first_p.get_text(" ", strip=True))
        m = UST_LEAD_RE.match(text)
        if m:
            ust_num = m.group(1)
            ust_lead_text = m.group(2).strip()
        else:
            # No numbered lead — treat as full ust=None content
            ust_lead_text = text

    # Collect all tables (each row = a lit chunk) within ust_div
    lit_tables = ust_div.find_all("table", recursive=False)
    if not lit_tables:
        # Sometimes tables are 2-3 levels deep
        lit_tables = ust_div.find_all("table")

    lit_records: list[tuple[str, str]] = []  # (lit_letter, text)
    for table in lit_tables:
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) != 2:
                continue
            marker = normalize_inline(cells[0].get_text(" ", strip=True))
            body = normalize_inline(cells[1].get_text(" ", strip=True))
            if not marker or not body:
                continue
            # Marker could be "a)", "(a)", "1)", "i)" — extract just the letter/number
            m_lit = re.match(r"^\(?([a-z]{1,3}|\d+|[ivxIVX]{1,4})\)?$", marker)
            if m_lit:
                lit_records.append((m_lit.group(1).lower(), body))

    # === Emit chunks ===
    if lit_records:
        # Each letter = its own chunk. Lead text becomes lead-in (metadata).
        for lit_letter, lit_text in lit_records:
            chunk = _build_chunk(
                art=art_num,
                ust=ust_num,
                pkt=None,
                lit=lit_letter,
                motyw=None,
                tresc=lit_text,
                cfg=cfg,
                source_url=source_url,
                extra_meta={
                    "ust_lead": ust_lead_text if ust_lead_text else None,
                    "art_subtitle": art_subtitle,
                },
            )
            chunks.append(chunk)
    elif ust_lead_text:
        # No letters — ust lead text itself is the chunk
        chunk = _build_chunk(
            art=art_num,
            ust=ust_num,
            pkt=None,
            lit=None,
            motyw=None,
            tresc=ust_lead_text,
            cfg=cfg,
            source_url=source_url,
            extra_meta={"art_subtitle": art_subtitle} if art_subtitle else {},
        )
        chunks.append(chunk)


def _build_motyw_chunk(
    motyw_num: str, motyw_text: str, cfg: DyrektywaConfig, source_url: str
) -> UEChunk:
    """Construct a UEChunk for preambula motyw."""
    safe_id = (
        f"celex_{cfg.celex_id}_motyw_{motyw_num}"
    )
    citation = build_citation_directive(cfg.direktywa_id, motyw=motyw_num)
    return UEChunk(
        chunk_id=safe_id,
        celex_id=cfg.celex_id,
        direktywa_id=cfg.direktywa_id,
        direktywa_title_pl=cfg.title_pl,
        art=None,
        ust=None,
        pkt=None,
        lit=None,
        motyw=motyw_num,
        tresc=motyw_text,
        citation_string=citation,
        license=LICENSE_EURLEX,
        scrape_date=TODAY,
        source_url=source_url,
        metadata={
            "data_publikacji": cfg.data_publikacji,
            "data_wejscia_w_zycie": cfg.data_wejscia_w_zycie,
            "data_implementacji": cfg.data_implementacji,
            "polska_implementacja": cfg.polska_implementacja,
            "section": "preambula",
        },
    )


def _build_chunk(
    art: str | None,
    ust: str | None,
    pkt: str | None,
    lit: str | None,
    motyw: str | None,
    tresc: str,
    cfg: DyrektywaConfig,
    source_url: str,
    extra_meta: dict[str, Any] | None = None,
) -> UEChunk:
    """Construct a UEChunk with deterministic chunk_id and citation_string."""
    parts = [f"celex_{cfg.celex_id}"]
    if art is not None:
        parts.append(f"art_{art}")
    if ust is not None:
        parts.append(f"ust_{ust}")
    if pkt is not None:
        parts.append(f"pkt_{pkt}")
    if lit is not None:
        parts.append(f"lit_{lit}")
    if motyw is not None:
        parts.append(f"motyw_{motyw}")
    chunk_id = "_".join(parts)

    citation = build_citation_directive(
        cfg.direktywa_id, art=art, ust=ust, pkt=pkt, lit=lit, motyw=motyw
    )

    meta: dict[str, Any] = {
        "data_publikacji": cfg.data_publikacji,
        "data_wejscia_w_zycie": cfg.data_wejscia_w_zycie,
        "data_implementacji": cfg.data_implementacji,
        "polska_implementacja": cfg.polska_implementacja,
        "section": "preambula" if motyw is not None else "articles",
    }
    if extra_meta:
        # Filter None values
        for k, v in extra_meta.items():
            if v is not None:
                meta[k] = v

    return UEChunk(
        chunk_id=chunk_id,
        celex_id=cfg.celex_id,
        direktywa_id=cfg.direktywa_id,
        direktywa_title_pl=cfg.title_pl,
        art=art,
        ust=ust,
        pkt=pkt,
        lit=lit,
        motyw=motyw,
        tresc=tresc,
        citation_string=citation,
        license=LICENSE_EURLEX,
        scrape_date=TODAY,
        source_url=source_url,
        metadata=meta,
    )


# === Validation hook (Pydantic) ===


def validate_chunks(chunks: list[UEChunk]) -> list[UEChunk]:
    """Validate chunks against the strict Pydantic schema (halu.schemas.UEDyrektywa)."""
    from halu.schemas import UEDyrektywa

    valid: list[UEChunk] = []
    drop_count = 0
    for c in chunks:
        d = c.as_dict()
        d["scrape_date"] = date.fromisoformat(d["scrape_date"])
        try:
            UEDyrektywa(**d)  # strict validation
            valid.append(c)
        except Exception as exc:
            logger.warning("drop invalid chunk %s: %s", c.chunk_id, exc)
            drop_count += 1
    if drop_count:
        logger.warning("dropped %d invalid chunks (schema)", drop_count)
    return valid


# === Main ===


def scrape_directive(
    cfg: DyrektywaConfig, fetcher: Fetcher, output_dir: Path
) -> ScrapeStats:
    """Pobierz pojedyncza dyrektywe + zapisz JSONL + meta."""
    fmt = EurLexFormats(cfg.celex_id)
    logger.info("=== %s — %s ===", cfg.direktywa_id, cfg.title_pl[:80])
    resp = fetcher.get(fmt.url_html)
    if resp is None:
        logger.error("FETCH FAIL %s", fmt.url_html)
        return ScrapeStats(
            source=cfg.direktywa_id,
            scrape_date=TODAY,
            license=LICENSE_EURLEX,
            total_records=0,
            notes="fetch failed",
        )

    chunks, observed_title = parse_directive_html(resp.text, cfg, fmt.url_html)
    logger.info("parsed %d chunks from %s", len(chunks), cfg.celex_id)

    chunks = validate_chunks(chunks)
    logger.info("validated %d chunks from %s", len(chunks), cfg.celex_id)

    # Output
    safe_id = cfg.celex_id
    jsonl_path = output_dir / f"{safe_id}.jsonl"
    meta_path = output_dir / f"{safe_id}_meta.json"

    write_jsonl([c.as_dict() for c in chunks], jsonl_path)

    motyw_count = sum(1 for c in chunks if c.motyw is not None)
    art_count = sum(1 for c in chunks if c.art is not None)
    distinct_arts = sorted({c.art for c in chunks if c.art is not None}, key=lambda x: int(re.sub(r"\D", "", x) or "0"))
    meta = {
        "celex_id": cfg.celex_id,
        "direktywa_id": cfg.direktywa_id,
        "title_pl": cfg.title_pl,
        "title_observed": observed_title,
        "data_publikacji": cfg.data_publikacji,
        "data_wejscia_w_zycie": cfg.data_wejscia_w_zycie,
        "data_implementacji": cfg.data_implementacji,
        "polska_implementacja": cfg.polska_implementacja,
        "notes": cfg.notes,
        "chunk_count": len(chunks),
        "motyw_count": motyw_count,
        "article_chunk_count": art_count,
        "distinct_articles": distinct_arts,
        "source_url_html": fmt.url_html,
        "source_url_landing": fmt.url_landing,
        "source_url_pdf": fmt.url_pdf,
        "scrape_date": TODAY,
        "license": LICENSE_EURLEX,
    }
    write_json(meta, meta_path)

    stats = ScrapeStats(
        source=cfg.direktywa_id,
        scrape_date=TODAY,
        license=LICENSE_EURLEX,
        total_records=len(chunks),
        notes=f"motyw={motyw_count} art={art_count} arts={len(distinct_arts)}",
    )
    return stats


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--celex", default=None, help="Pobierz tylko jedna dyrektywe po CELEX id")
    parser.add_argument(
        "--output",
        default=str(
            Path(__file__).resolve().parents[3] / "data" / "raw" / "ue_dyrektywy_2026-05-16"
        ),
    )
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO if not args.verbose else logging.DEBUG,
        format="%(asctime)s %(levelname)-7s %(name)s | %(message)s",
    )

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    fetcher = Fetcher()
    targets = [c for c in DYREKTYWY if (args.celex is None or c.celex_id == args.celex)]
    if not targets:
        logger.error("No matching directive for --celex %s", args.celex)
        return 2

    all_stats: list[dict[str, Any]] = []
    for cfg in targets:
        stats = scrape_directive(cfg, fetcher, output_dir)
        all_stats.append(stats.as_dict())

    # Aggregate stats
    write_json(
        {
            "scrape_date": TODAY,
            "license": LICENSE_EURLEX,
            "directives": all_stats,
            "total_chunks": sum(s["total_records"] for s in all_stats),
        },
        output_dir / "_summary.json",
    )
    logger.info(
        "DONE — %d directives processed, %d total chunks",
        len(all_stats),
        sum(s["total_records"] for s in all_stats),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
