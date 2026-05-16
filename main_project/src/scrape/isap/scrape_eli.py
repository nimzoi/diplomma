"""Scraper polskich ustaw konsumenckich z ELI API (api.sejm.gov.pl/eli).

Cel: corpus chunks dla citation-grounded polish RAG. Każdy chunk to atomowa
jednostka prawna (art./§/ust./pkt./lit.) z deterministycznym citation_string
jednoznacznie identyfikującym source — kluczowe dla halu detection.

Pokrycie (6 ustaw konsumenckich, ustalone w sources_catalog § Domain A):
  - Ustawa o prawach konsumenta (DU/2014/827)
  - Kodeks cywilny (DU/1964/93) — wybrane sekcje: art. 384-385, 535-581
  - Ustawa o przeciwdziałaniu nieuczciwym praktykom rynkowym (DU/2007/1206)
  - Ustawa o ochronie konkurencji i konsumentów (DU/2007/331)
  - Ustawa o usługach płatniczych (DU/2011/1175)
  - Ustawa o pozasądowym rozwiązywaniu sporów konsumenckich (DU/2016/1823)

Strategia ekstraktu:
  - Metadata: `/eli/acts/{publisher}/{year}/{num}` (JSON)
  - Treść: `/eli/acts/{publisher}/{year}/{num}/text.html` (pełen tekst)
    Per-art endpoint (`/text.html/art={N}`) zwraca pustkę dla niektórych ustaw
    (KC, ochrona konkur., usługi płatn.) — pełen tekst zawsze działa.
  - Parser HTML: stdlib `html.parser`, walka po divach `unit_arti` → `unit_pass`/
    `unit_para` → `unit_pint` → `unit_lett`. Treść w `<div data-template="xText">`.

Hierarchia jednostek prawnych (mapowanie HTML → kanonika):
  unit_arti    → artykuł (art.)
  unit_para    → paragraf (§)     — używane w KC
  unit_pass    → ustęp (ust.)     — używane w nowszych ustawach
  unit_pint    → punkt (pkt)
  unit_lett    → litera (lit.)

Chunkowanie:
  - Atom = najgłębsza jednostka tekstowa (lista). Jeśli artykuł nie ma podziału,
    cały artykuł jest jednym chunkiem.
  - Jeśli artykuł ma ustępy/paragrafy bez punktów — ustęp/paragraf = chunk.
  - Jeśli ustęp ma punkty — punkt = chunk (lead-in z ustępu w metadata.lead_in).
  - Jeśli punkt ma litery — litera = chunk (analogicznie lead-in z pkt).

Citation:
  „art. 27 ust. 1 pkt 2 lit. a Ustawy o prawach konsumenta z dnia 30 maja 2014 r.
  (Dz.U. 2014 poz. 827)"

Usage:
    uv run python -m src.scrape.isap.scrape_eli           # wszystkie 6 ustaw
    uv run python -m src.scrape.isap.scrape_eli --ustawa DU/2014/827
    uv run python -m src.scrape.isap.scrape_eli --dry-run --ustawa DU/2014/827

License source corpusu:
    Art. 4 ust. 1 ustawy o prawie autorskim (DU/1994/83) — akty normatywne nie
    stanowią przedmiotu prawa autorskiego. Public domain de facto.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
import unicodedata
import urllib.request
import urllib.error
from dataclasses import dataclass, field, asdict
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ELI_BASE = "https://api.sejm.gov.pl/eli/acts"
USER_AGENT = "ELI corpus collector - MgSochacka PJATK thesis (citation-grounded RAG)"
REQUEST_TIMEOUT_SEC = 30.0
INTER_REQUEST_DELAY_SEC = 0.4  # polite — feasibility recommends 2-5 req/s
SCRAPE_DATE = "2026-05-16"

POLISH_MONTHS = {
    1: "stycznia",
    2: "lutego",
    3: "marca",
    4: "kwietnia",
    5: "maja",
    6: "czerwca",
    7: "lipca",
    8: "sierpnia",
    9: "września",
    10: "października",
    11: "listopada",
    12: "grudnia",
}


@dataclass(frozen=True)
class UstawaConfig:
    """Konfiguracja per ustawa."""

    ustawa_id: str  # "DU/2014/827"
    short_title: str  # "Ustawy o prawach konsumenta" (genitive — for citation)
    art_filter: tuple[int, ...] | None = (
        None  # None = wszystkie; (384, 385, 535, ..., 581) dla KC
    )


USTAWY: tuple[UstawaConfig, ...] = (
    UstawaConfig(
        ustawa_id="DU/2014/827",
        short_title="Ustawy o prawach konsumenta",
    ),
    UstawaConfig(
        ustawa_id="DU/1964/93",
        short_title="Kodeksu cywilnego",
        art_filter=tuple(range(384, 386)) + tuple(range(535, 582)),
    ),
    UstawaConfig(
        ustawa_id="DU/2007/1206",
        short_title="Ustawy o przeciwdziałaniu nieuczciwym praktykom rynkowym",
    ),
    UstawaConfig(
        ustawa_id="DU/2007/331",
        short_title="Ustawy o ochronie konkurencji i konsumentów",
    ),
    UstawaConfig(
        ustawa_id="DU/2011/1175",
        short_title="Ustawy o usługach płatniczych",
    ),
    UstawaConfig(
        ustawa_id="DU/2016/1823",
        short_title="Ustawy o pozasądowym rozwiązywaniu sporów konsumenckich",
    ),
    # === Dodane w Iter. 0b extension (2026-05-16) — 5 ustaw konsumenckich z scope brief Część B ===
    # NOTE: Magdy brief miał błędne pos:
    #   DU/1997/140 → faktycznie DU/1997/939 (Prawo bankowe; 140 to nr, 939 to poz)
    #   DU/2004/1800 → NOT_IN_FORCE, zastąpione przez DU/2024/1221 (Prawo komunikacji elektronicznej)
    #   DU/2009/89  → DU/2009/89 to Rozporządzenie infrastruktury, NIE Ust. o pos. grup.
    #                  Faktycznie DU/2010/44 (ann. 2009-12-17, prom. 2010-01-18)
    UstawaConfig(
        ustawa_id="DU/1997/939",
        short_title="Ustawy Prawo bankowe",
        # Konsumencko-relewantne: rozdz. 5 (kredyty pożyczki) + 8 (obowiązki banków)
        # + wybrane z rozdz. 3 (rachunki bankowe) i 13 (odpowiedzialność cywilna)
        # Pragmatic: scrape całą ustawę (~194 arts) — analiza filtrów post-hoc
        # przy budowaniu eval set jest tańsza niż restrykcyjny scrape.
    ),
    UstawaConfig(
        ustawa_id="DU/2002/1204",
        short_title="Ustawy o świadczeniu usług drogą elektroniczną",
    ),
    UstawaConfig(
        ustawa_id="DU/2024/1221",
        short_title="Ustawy Prawo komunikacji elektronicznej",
        # Tylko Dział VII (Publicznie dostępne usługi komunikacji elektronicznej) —
        # to centralny konsumencko-relewantny rozdział. Art. 282-410.
        art_filter=tuple(range(282, 411)),
    ),
    UstawaConfig(
        ustawa_id="DU/2011/715",
        short_title="Ustawy o kredycie konsumenckim",
    ),
    UstawaConfig(
        ustawa_id="DU/2010/44",
        short_title="Ustawy o dochodzeniu roszczeń w postępowaniu grupowym",
    ),
)


@dataclass
class Unit:
    """Pojedyncza jednostka prawna parsowana z HTML."""

    kind: str  # 'arti' | 'para' | 'pass' | 'pint' | 'lett'
    name: str  # numer/litera (np. '27', '1', '2', 'a')
    text: str = ""  # treść bezpośrednia (bez treści dzieci)
    children: list[Unit] = field(default_factory=list)
    chapter_title: str = ""  # rozdział nadrzędny (dla context)


@dataclass
class Chunk:
    """Jeden atom corpus."""

    ustawa_id: str
    ustawa_title: str  # pełen oficjalny title z metadata
    art: str
    para: str | None  # § (KC)
    ust: str | None  # ust. (nowsze ustawy)
    pkt: str | None
    lit: str | None
    tresc: str
    citation_string: str
    scrape_date: str
    source_url: str
    metadata: dict[str, Any]


class _StructuralHTMLParser(HTMLParser):
    """Parser HTML — buduje drzewo jednostek prawnych.

    Klasy znaczników w HTML ELI:
      <div class="unit unit_arti pro-text false" data-id="arti_27">
      <div class="unit unit_para pro-text false" data-id="para_1">
      <div class="unit unit_pass pro-text false" data-id="pass_1">
      <div class="unit unit_pint pro-text false" data-id="pint_1">
      <div class="unit unit_lett pro-text false" data-id="lett_a">
      <div data-template="xText" CLASS="pro-text">treść...</div>
      <div class="unit unit_chpt ..."> z <h3>...</h3> dla nazw rozdziałów

    Stack-based — gdy zaczyna się unit, push; gdy kończy, pop i append do parent.
    xText to tekst danej jednostki (PRZED dziećmi w HTML, ale w prawie często
    działa jako lead-in dla następujących pkt/lit).
    """

    UNIT_TYPES = (
        "arti",
        "para",
        "pass",
        "pint",
        "lett",
        "chpt",
        "titl",
        "sect",
        "book",
        "bran",
    )
    CHAPTER_LIKE = ("chpt", "titl", "sect", "book", "bran")

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.roots: list[Unit] = []
        self._stack: list[Unit] = []
        # chapter context — nazwa najbardziej zagnieżdżonego "chpt"/"titl" obowiązująca
        self._chapter_stack: list[tuple[str, str]] = []  # (level_kind, title_text)
        self._chapter_title_buffer: str | None = None
        self._capturing_xtext: int = (
            0  # zagnieżdżona głębokość divów z data-template="xText"
        )
        self._text_buffer: list[str] = []
        self._capturing_chapter_h3: int = 0
        self._h3_text_buffer: list[str] = []
        self._pending_unit_kind: str | None = (
            None  # następny ujęty unit dla chapter context
        )

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_d = dict(attrs)
        klass = (attr_d.get("class") or "").lower()
        data_id = attr_d.get("data-id") or ""

        if tag.lower() == "div":
            kind = self._classify_unit(klass, data_id)
            if kind is not None:
                self._flush_text_to_current()
                # Wyłącz capturing xText jeśli wchodzimy do nowej jednostki
                # (nie powinno się zdarzyć — xText jest leaf, ale sanity guard)
                if self._capturing_xtext > 0:
                    self._capturing_xtext = 0
                    self._text_buffer.clear()

                name = self._extract_name(data_id, kind)
                if kind in self.CHAPTER_LIKE:
                    # Push chapter context — title z najbliższego H3 (zostanie wpisane w handle_endtag h3)
                    self._chapter_stack.append((kind, ""))
                    self._pending_unit_kind = kind
                    # Nie dodajemy do _stack (nie chcemy chapter jako self-standing unit)
                    return
                unit = Unit(
                    kind=kind,
                    name=name,
                    chapter_title=self._current_chapter_title(),
                )
                self._stack.append(unit)
                return

            # data-template="xText" — wejście w treść tekstową bieżącej jednostki
            if attr_d.get("data-template", "").lower() == "xtext":
                if self._stack:
                    self._capturing_xtext += 1
                return

        if tag.lower() == "h3":
            # Capture tylko jeśli mamy świeżą jednostkę chapter-like na _chapter_stack
            # bez nazwy — tj. ostatnio dodaną pustą.
            if self._chapter_stack and not self._chapter_stack[-1][1]:
                self._capturing_chapter_h3 += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "div":
            # 1) Najpierw obsłuż xText close — tekst wpadnie do bieżącej unit.
            if self._capturing_xtext > 0:
                self._capturing_xtext -= 1
                if self._capturing_xtext == 0:
                    text = self._collect_text()
                    if self._stack and text:
                        existing = self._stack[-1].text
                        sep = " " if existing else ""
                        self._stack[-1].text = (existing + sep + text).strip()
            # 2) ZAWSZE wywołaj _on_close_div — pop div_kind_stack i ewentualnie unit_stack.
            self._on_close_div()

        if tag.lower() == "h3":
            if self._capturing_chapter_h3 > 0:
                self._capturing_chapter_h3 -= 1
                if self._capturing_chapter_h3 == 0:
                    title = self._collect_h3_text()
                    if self._chapter_stack:
                        kind, _ = self._chapter_stack[-1]
                        self._chapter_stack[-1] = (kind, title)

    def handle_data(self, data: str) -> None:
        if self._capturing_xtext > 0:
            self._text_buffer.append(data)
        if self._capturing_chapter_h3 > 0:
            self._h3_text_buffer.append(data)

    def _flush_text_to_current(self) -> None:
        if self._text_buffer and self._stack and self._capturing_xtext > 0:
            joined = "".join(self._text_buffer).strip()
            if joined:
                existing = self._stack[-1].text
                sep = " " if existing else ""
                self._stack[-1].text = (existing + sep + joined).strip()
            self._text_buffer.clear()

    def _collect_text(self) -> str:
        joined = "".join(self._text_buffer)
        self._text_buffer.clear()
        # Zwiń whitespace
        return re.sub(r"\s+", " ", joined).strip()

    def _collect_h3_text(self) -> str:
        joined = "".join(self._h3_text_buffer)
        self._h3_text_buffer.clear()
        return re.sub(r"\s+", " ", joined).strip()

    def _classify_unit(self, klass: str, data_id: str) -> str | None:
        if "unit" not in klass:
            return None
        for utype in self.UNIT_TYPES:
            if f"unit_{utype}" in klass:
                return utype
        return None

    @staticmethod
    def _extract_name(data_id: str, kind: str) -> str:
        # data-id format: "arti_27", "para_1", "pass_1", "pint_2", "lett_a"
        prefix = f"{kind}_"
        if data_id.startswith(prefix):
            return data_id[len(prefix) :]
        return data_id

    def _current_chapter_title(self) -> str:
        for _, title in reversed(self._chapter_stack):
            if title:
                return title
        return ""

    def _on_close_div(self) -> None:
        # Wywoływane po każdym </div>. Bez state, używamy DivDepthMixin (poniżej).
        pass  # nadpisywane w subklasie


class _DepthTrackingParser(_StructuralHTMLParser):
    """Parser z dokładnym śledzeniem głębokości divów aby poprawnie zamykać jednostki.

    Każdy <div> rejestruje, czy był to:
      - unit (push do _stack, push do _div_kind_stack jako 'unit:<kind>')
      - chapter unit (push do _chapter_stack, push jako 'chpt:<kind>')
      - xText (jedyny inny tracked div poza unit, push jako 'xtext')
      - inne (push jako 'other')

    Pop przy </div> według tego trackera.
    """

    def __init__(self) -> None:
        super().__init__()
        self._div_kind_stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "div":
            attr_d = dict(attrs)
            klass = (attr_d.get("class") or "").lower()
            data_id = attr_d.get("data-id") or ""
            kind = self._classify_unit(klass, data_id)

            if kind is not None:
                if kind in self.CHAPTER_LIKE:
                    self._div_kind_stack.append(f"chpt:{kind}")
                else:
                    self._div_kind_stack.append(f"unit:{kind}")
            elif attr_d.get("data-template", "").lower() == "xtext":
                self._div_kind_stack.append("xtext")
            else:
                self._div_kind_stack.append("other")

        super().handle_starttag(tag, attrs)

    def _on_close_div(self) -> None:
        if not self._div_kind_stack:
            return
        kind_marker = self._div_kind_stack.pop()
        if kind_marker.startswith("unit:"):
            if not self._stack:
                return
            closed = self._stack.pop()
            if self._stack:
                self._stack[-1].children.append(closed)
            else:
                self.roots.append(closed)
        elif kind_marker.startswith("chpt:"):
            if self._chapter_stack:
                self._chapter_stack.pop()
        # 'xtext' i 'other' nie wymagają akcji na _stack/_chapter_stack
        # (xText decrement obsłużony w handle_endtag)


def normalize_polish(text: str) -> str:
    """NFC normalization + sanitize whitespace + clean polish nbsp."""
    text = unicodedata.normalize("NFC", text)
    # Replace non-breaking spaces z regular
    text = text.replace(" ", " ")
    # Zwiń wielokrotne whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def parse_act_html(html_content: str) -> list[Unit]:
    """Parsuj pełen HTML aktu — zwróć listę top-level artykułów (Unit kind='arti')."""
    parser = _DepthTrackingParser()
    parser.feed(html_content)
    parser.close()
    arts: list[Unit] = []

    # Strategia: emituj TYLKO artykuły będące dziećmi struktur nadrzędnych
    # (chpt/titl/sect/book/bran/part) — NIE artykuły zagnieżdżone w innych
    # artykułach (te są tekstem przepisu zmieniającego, np. „art. 118 wprowadza
    # do innej ustawy art. 20a" — arti_20a istnieje w HTML ale nie jest własnym
    # artykułem tej ustawy).
    #
    # Wyjątek: nowe artykuły dodane do tej ustawy z literowym suffixem (np. 4a),
    # jeśli są dziećmi tego samego chapter co główne arti. ELI publikuje je
    # jako bezpośrednie children chapter (potwierdzone na arti_4a w DU/2007/331,
    # arti_16a w DU/2016/1823) — więc są wyłapywane top-level walk.
    #
    # Implementacja: walk po roots; jeśli root.kind == 'arti', emit + zatrzymaj
    # zejście (sub-arti pod arti to amendment text). Jeśli kind chapter-like —
    # zejdź.
    def _walk(units: list[Unit]) -> None:
        for u in units:
            if u.kind == "arti":
                arts.append(u)
                # NIE descend dalej — sub-arti pod arti to amendment text.
            else:
                _walk(u.children)

    _walk(parser.roots)
    return arts


def _format_announcement_date(iso_date: str) -> str:
    """'2014-05-30' → '30 maja 2014 r.' (polish citation format)."""
    try:
        d = datetime.fromisoformat(iso_date).date()
    except ValueError:
        return iso_date
    return f"{d.day} {POLISH_MONTHS[d.month]} {d.year} r."


def _format_dz_u(meta: dict[str, Any]) -> str:
    """'Dz.U. 2014 poz. 827' z metadata."""
    return f"Dz.U. {meta['year']} poz. {meta['pos']}"


def build_citation_string(
    ustawa_short_title: str,
    meta: dict[str, Any],
    art: str,
    para: str | None,
    ust: str | None,
    pkt: str | None,
    lit: str | None,
) -> str:
    parts = [f"art. {art}"]
    if para:
        parts.append(f"§ {para}")
    if ust:
        parts.append(f"ust. {ust}")
    if pkt:
        parts.append(f"pkt {pkt}")
    if lit:
        parts.append(f"lit. {lit}")
    unit_str = " ".join(parts)
    data = _format_announcement_date(meta["announcementDate"])
    dz_u = _format_dz_u(meta)
    return f"{unit_str} {ustawa_short_title} z dnia {data} ({dz_u})"


def _build_source_url(meta: dict[str, Any], art: str) -> str:
    """Stable URL do pojedynczego artykułu (preferowany cytowanie level)."""
    pub = meta["publisher"]
    yr = meta["year"]
    pos = meta["pos"]
    return f"{ELI_BASE}/{pub}/{yr}/{pos}/text.html/art={art}"


def flatten_to_chunks(
    units: list[Unit],
    ustawa: UstawaConfig,
    meta: dict[str, Any],
    valid_paths: set[tuple[tuple[str, str], ...]] | None = None,
) -> list[Chunk]:
    """Spłaszcz drzewo Units → płaska lista Chunków na poziomie leaf.

    Algorytm:
      Dla każdego artykułu:
        - Jeśli brak dzieci → cały art = chunk
        - Jeśli artykuł ma dzieci typu para/pass:
          → dla każdego dziecka rekursja `_descend(child, art=N, para/ust=...)`
        - W _descend: jeśli child ma kolejny poziom (pint/lett) → recurse, ale jeśli
          aktualne unit ma WŁASNY text (lead-in), zachowaj jako metadata.lead_in dla
          chunków potomnych.
        - Leaf = chunk.
    """
    chunks: list[Chunk] = []
    ustawa_title = meta.get("title", "")

    for art_unit in units:
        if art_unit.kind != "arti":
            continue
        # Extract base number z nazwy (e.g. "4a" → 4, "535" → 535)
        m = re.match(r"^(\d+)", art_unit.name)
        art_num_int = int(m.group(1)) if m else 0
        if ustawa.art_filter is not None and art_num_int not in ustawa.art_filter:
            continue

        art_name = art_unit.name
        source_url = _build_source_url(meta, art_name)

        def _emit(
            text: str,
            para: str | None,
            ust: str | None,
            pkt: str | None,
            lit: str | None,
            lead_in: str = "",
            chapter_title: str = "",
        ) -> None:
            text_norm = normalize_polish(text)
            if not text_norm:
                return
            citation = build_citation_string(
                ustawa.short_title, meta, art_name, para, ust, pkt, lit
            )
            extra_meta: dict[str, Any] = {
                "data_uchwalenia": meta.get("announcementDate"),
                "data_promulgacji": meta.get("promulgation"),
                "data_wejscia_w_zycie": meta.get("entryIntoForce"),
                "ostatnia_zmiana": meta.get("changeDate"),
                "obowiazujaca": meta.get("inForce") == "IN_FORCE",
                "status": meta.get("status"),
                "rozdzial": chapter_title or art_unit.chapter_title or None,
            }
            if lead_in:
                extra_meta["lead_in"] = normalize_polish(lead_in)
            chunks.append(
                Chunk(
                    ustawa_id=ustawa.ustawa_id,
                    ustawa_title=ustawa_title,
                    art=art_name,
                    para=para,
                    ust=ust,
                    pkt=pkt,
                    lit=lit,
                    tresc=text_norm,
                    citation_string=citation,
                    scrape_date=SCRAPE_DATE,
                    source_url=source_url,
                    metadata=extra_meta,
                )
            )

        def _path_in_struct(
            p_para: str | None, p_ust: str | None, p_pkt: str | None, p_lit: str | None
        ) -> bool:
            if valid_paths is None:
                return True
            path: list[tuple[str, str]] = [("arti", art_name)]
            if p_para:
                path.append(("para", p_para))
            if p_ust:
                path.append(("pass", p_ust))
            if p_pkt:
                path.append(("pint", p_pkt))
            if p_lit:
                path.append(("lett", p_lit))
            return tuple(path) in valid_paths

        def _descend(
            unit: Unit,
            para: str | None,
            ust: str | None,
            pkt: str | None,
            lit: str | None,
            parent_lead_in: str = "",
        ) -> None:
            own_text = unit.text
            # Zignoruj zagnieżdżone arti (są to text przepisów zmieniających).
            structural_children = [c for c in unit.children if c.kind != "arti"]

            # Czy dzieci strukturalne mają walidne path-y w ELI struct? Jeśli nie
            # (np. para pod pint w ustawie używającej tylko ust.) — to znaczy że
            # to amending text wstawiony w HTML; emit own_text na poziomie obecnej
            # jednostki i nie schodzimy.
            #
            # ALSO: kanoniczna hierarchia ELI to arti > para|pass|pint > pint > lett.
            # Jeśli obecna jednostka MA już ustawione `pkt` i widzi child `pint` —
            # to NIE jest poprawna hierarchia (pkt nie ma child pkt). Identycznie
            # dla `pass` pod ustawą która już ma `ust` set. Wskazuje amending text.
            def _child_path_valid(child: Unit) -> bool:
                # Hierarchia: skip jeśli próbujemy nadpisać już-ustawione pole hierarchiczne.
                if child.kind == "pint" and pkt is not None:
                    return False
                if child.kind == "pass" and ust is not None:
                    return False
                if child.kind == "para" and para is not None:
                    return False
                if child.kind == "lett" and lit is not None:
                    return False
                # ELI hierarchy: lett jest leaf — pod lett nie może być pint/pass/para.
                # Jeśli aktualnie jesteśmy na lett (lit set), żaden nowy struktur. dziecko OK.
                # (już blokowane przez powyższe checki dla lett, ale dodajmy explicit dla pkt:
                #  pod pint może być TYLKO lett.)
                if pkt is not None and child.kind != "lett":
                    return False
                cp_para, cp_ust, cp_pkt, cp_lit = para, ust, pkt, lit
                if child.kind == "para":
                    cp_para = child.name
                elif child.kind == "pass":
                    cp_ust = child.name
                elif child.kind == "pint":
                    cp_pkt = child.name
                elif child.kind == "lett":
                    cp_lit = child.name
                return _path_in_struct(cp_para, cp_ust, cp_pkt, cp_lit)

            valid_structural = [c for c in structural_children if _child_path_valid(c)]
            has_valid_children = bool(valid_structural)
            if not has_valid_children:
                # Leaf z punktu widzenia validnej hierarchii — emit own_text.
                _emit(
                    own_text,
                    para,
                    ust,
                    pkt,
                    lit,
                    lead_in=parent_lead_in,
                    chapter_title=unit.chapter_title,
                )
                return
            # Mamy dzieci walidne. Aktualny `own_text` to lead-in dla nich.
            lead = parent_lead_in
            if own_text:
                lead = f"{lead} {own_text}".strip() if lead else own_text
            for child in valid_structural:
                if child.kind == "para":
                    _descend(
                        child,
                        para=child.name,
                        ust=ust,
                        pkt=pkt,
                        lit=lit,
                        parent_lead_in=lead,
                    )
                elif child.kind == "pass":
                    _descend(
                        child,
                        para=para,
                        ust=child.name,
                        pkt=pkt,
                        lit=lit,
                        parent_lead_in=lead,
                    )
                elif child.kind == "pint":
                    _descend(
                        child,
                        para=para,
                        ust=ust,
                        pkt=child.name,
                        lit=lit,
                        parent_lead_in=lead,
                    )
                elif child.kind == "lett":
                    _descend(
                        child,
                        para=para,
                        ust=ust,
                        pkt=pkt,
                        lit=child.name,
                        parent_lead_in=lead,
                    )
                else:
                    _descend(
                        child, para=para, ust=ust, pkt=pkt, lit=lit, parent_lead_in=lead
                    )

        # Start z artykułem na top.
        if not art_unit.children:
            _emit(
                art_unit.text,
                para=None,
                ust=None,
                pkt=None,
                lit=None,
                chapter_title=art_unit.chapter_title,
            )
        else:
            _descend(
                art_unit, para=None, ust=None, pkt=None, lit=None, parent_lead_in=""
            )

    return chunks


def http_get(url: str, *, accept: str = "*/*") -> bytes:
    """HTTP GET z politem User-Agent i timeoutem. Raise on non-200."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept": accept},
    )
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SEC) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP {response.status} for {url}")
            return response.read()
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code} for {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network error for {url}: {exc.reason}") from exc


def fetch_act_metadata(ustawa_id: str) -> dict[str, Any]:
    pub, yr, num = ustawa_id.split("/")
    url = f"{ELI_BASE}/{pub}/{yr}/{num}"
    logger.info("Fetching metadata: %s", url)
    data = http_get(url, accept="application/json")
    return json.loads(data.decode("utf-8"))


def fetch_act_struct(ustawa_id: str) -> list[dict[str, Any]]:
    """Pobierz authoritative strukturę aktu z ELI."""
    pub, yr, num = ustawa_id.split("/")
    url = f"{ELI_BASE}/{pub}/{yr}/{num}/struct"
    logger.info("Fetching structure: %s", url)
    data = http_get(url, accept="application/json")
    return json.loads(data.decode("utf-8"))


def collect_valid_legal_paths(
    struct: list[dict[str, Any]],
) -> set[tuple[tuple[str, str], ...]]:
    """Z ELI struct JSON zwróć zbiór wszystkich validnych ścieżek prawnych.

    Każda ścieżka to tuple (type, name) zaczynający się od arti. Skip kontenery
    typu chpt/titl/sect/book/bran/part.
    """
    legal_kinds = {"arti", "para", "pass", "pint", "lett"}
    out: set[tuple[tuple[str, str], ...]] = set()

    def walk(units: list[dict[str, Any]], path: tuple[tuple[str, str], ...]) -> None:
        for u in units:
            t = u.get("type")
            n = u.get("name", "")
            new_path = path + ((t, n),) if t in legal_kinds else path
            if t in legal_kinds:
                out.add(new_path)
            for c in u.get("children", []):
                walk([c], new_path)

    walk(struct, ())
    return out


def fetch_act_html(ustawa_id: str) -> tuple[str, str]:
    pub, yr, num = ustawa_id.split("/")
    url = f"{ELI_BASE}/{pub}/{yr}/{num}/text.html"
    logger.info("Fetching full text HTML: %s", url)
    data = http_get(url, accept="text/html")
    return data.decode("utf-8"), url


def write_jsonl(chunks: list[Chunk], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for chunk in chunks:
            fh.write(json.dumps(asdict(chunk), ensure_ascii=False))
            fh.write("\n")


def write_meta(
    meta: dict[str, Any], ustawa: UstawaConfig, chunk_count: int, path: Path
) -> None:
    out = {
        "ustawa_id": ustawa.ustawa_id,
        "short_title": ustawa.short_title,
        "title": meta.get("title"),
        "publisher": meta.get("publisher"),
        "year": meta.get("year"),
        "pos": meta.get("pos"),
        "display_address": meta.get("displayAddress"),
        "type": meta.get("type"),
        "data_uchwalenia": meta.get("announcementDate"),
        "data_promulgacji": meta.get("promulgation"),
        "data_wejscia_w_zycie": meta.get("entryIntoForce"),
        "ostatnia_zmiana": meta.get("changeDate"),
        "obowiazujaca": meta.get("inForce") == "IN_FORCE",
        "in_force_raw": meta.get("inForce"),
        "status": meta.get("status"),
        "ELI": meta.get("ELI"),
        "previous_title": meta.get("previousTitle"),
        "art_filter": list(ustawa.art_filter) if ustawa.art_filter else None,
        "chunk_count": chunk_count,
        "source_metadata_url": f"{ELI_BASE}/{ustawa.ustawa_id}",
        "source_html_url": f"{ELI_BASE}/{ustawa.ustawa_id}/text.html",
        "consolidated_text_references": [
            ref.get("id")
            for ref in meta.get("references", {}).get("Inf. o tekście jednolitym", [])
        ]
        if isinstance(meta.get("references"), dict)
        else None,
        "amending_acts": [
            ref.get("id")
            for ref in meta.get("references", {}).get("Akty zmieniające", [])
        ]
        if isinstance(meta.get("references"), dict)
        else None,
        "directives_eu": [d.get("address") for d in meta.get("directives", []) or []],
        "scrape_date": SCRAPE_DATE,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


def scrape_one(ustawa: UstawaConfig, output_dir: Path) -> tuple[int, str]:
    """Scrape jednej ustawy. Zwróć (chunk_count, status_msg)."""
    safe_id = ustawa.ustawa_id.replace("/", "_")
    jsonl_path = output_dir / f"{safe_id}.jsonl"
    meta_path = output_dir / f"{safe_id}_meta.json"

    try:
        meta = fetch_act_metadata(ustawa.ustawa_id)
        time.sleep(INTER_REQUEST_DELAY_SEC)
        struct = fetch_act_struct(ustawa.ustawa_id)
        time.sleep(INTER_REQUEST_DELAY_SEC)
        html_content, _ = fetch_act_html(ustawa.ustawa_id)
    except RuntimeError as exc:
        logger.error("Failed to fetch %s: %s", ustawa.ustawa_id, exc)
        return 0, f"FAILED: {exc}"

    logger.info("Parsing HTML (%d bytes)...", len(html_content))
    units = parse_act_html(html_content)
    logger.info("Parsed %d top-level articles", len(units))

    valid_paths = collect_valid_legal_paths(struct)
    # Przekazujemy valid_paths do flatten — descend będzie pomijał ścieżki
    # nieobecne w canonical ELI struct (amending text inside HTML).
    chunks = flatten_to_chunks(units, ustawa, meta, valid_paths=valid_paths)
    logger.info(
        "Flattened to %d chunks (art_filter=%s)",
        len(chunks),
        "all" if ustawa.art_filter is None else f"{len(ustawa.art_filter)} arts",
    )

    write_jsonl(chunks, jsonl_path)
    write_meta(meta, ustawa, len(chunks), meta_path)
    logger.info("Wrote %s (%d chunks) + %s", jsonl_path, len(chunks), meta_path)

    return len(chunks), "OK"


def configure_logging(verbose: bool = False) -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--ustawa",
        type=str,
        default=None,
        help='ID jednej ustawy, np. "DU/2014/827". Domyślnie: scrape wszystkie 6.',
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(f"data/raw/eli_ustawy_konsumenckie_{SCRAPE_DATE}"),
        help="Katalog wyjściowy (domyślnie data/raw/eli_ustawy_konsumenckie_{date}/).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Tylko fetch + parse, nie zapisuj plików.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args(argv)

    configure_logging(args.verbose)

    if args.ustawa:
        targets = [u for u in USTAWY if u.ustawa_id == args.ustawa]
        if not targets:
            logger.error(
                "Nieznana ustawa: %s. Dostępne: %s",
                args.ustawa,
                [u.ustawa_id for u in USTAWY],
            )
            return 2
    else:
        targets = list(USTAWY)

    output_dir: Path = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    summary: list[tuple[str, int, str]] = []
    for ustawa in targets:
        logger.info("=" * 60)
        logger.info("USTAWA: %s — %s", ustawa.ustawa_id, ustawa.short_title)
        logger.info("=" * 60)
        if args.dry_run:
            try:
                meta = fetch_act_metadata(ustawa.ustawa_id)
                time.sleep(INTER_REQUEST_DELAY_SEC)
                struct = fetch_act_struct(ustawa.ustawa_id)
                time.sleep(INTER_REQUEST_DELAY_SEC)
                html_content, _ = fetch_act_html(ustawa.ustawa_id)
                units = parse_act_html(html_content)
                valid_paths = collect_valid_legal_paths(struct)
                chunks = flatten_to_chunks(units, ustawa, meta, valid_paths=valid_paths)
                summary.append((ustawa.ustawa_id, len(chunks), "DRY-RUN-OK"))
                logger.info("DRY-RUN: would write %d chunks", len(chunks))
            except Exception as exc:
                summary.append((ustawa.ustawa_id, 0, f"DRY-RUN-FAIL: {exc}"))
                logger.error("DRY-RUN failed: %s", exc)
        else:
            count, status = scrape_one(ustawa, output_dir)
            summary.append((ustawa.ustawa_id, count, status))
        time.sleep(INTER_REQUEST_DELAY_SEC)

    print("\n=== SCRAPE SUMMARY ===")
    print(f"{'ustawa_id':<20} {'chunks':>8}  status")
    print("-" * 60)
    total = 0
    for uid, count, status in summary:
        print(f"{uid:<20} {count:>8}  {status}")
        total += count
    print("-" * 60)
    print(f"{'TOTAL':<20} {total:>8}")
    print(f"\nOutput: {output_dir.resolve()}")
    return 0 if all(s.startswith(("OK", "DRY-RUN-OK")) for _, _, s in summary) else 1


if __name__ == "__main__":
    sys.exit(main())
