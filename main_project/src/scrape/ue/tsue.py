"""Scrape orzeczen TSUE konsumenckich z EUR-Lex (polska wersja jezykowa).

Cel: artikalna baza precedensu TSUE dla consumer rights claims w cytacjach
("claim w polish jest grounded w polish ustawie + cytowany TSUE wyklada
dyrektywe ktora ja implementuje").

Top ~30-50 spraw priority — z hand-curated list opartego o:
- Dyrektywa 93/13/EWG (UCT) — najwiecej praktyki sadowej (klauzule abuzywne,
  CHF kredyty: Dziubak C-260/18, Kasler C-26/13, Bank BPH C-19/20)
- Dyrektywa 2011/83/UE (CRD) — odstapienie od umowy, wymogi informacyjne
- Dyrektywa 2008/48/WE (CCD) — kredyt konsumencki (Radlinger C-377/14)
- Dyrektywa 2005/29/WE (UCPD) — nieuczciwe praktyki
- Definicje konsumenta (Benincasa C-269/95, Gruber C-464/01)

UWAGA: stare sprawy (pre-2004 Polski akcesyjny) mogą NIE miec PL wersji.
W razie braku — skip + dokumentuj w `meta.skipped_no_pl`.

CELEX format dla orzeczen: 6YYYYCJBBBB
  - 6 = case-law sector
  - YYYY = rok skierowania do TS (NIE rok wyroku!)
  - CJ = Court Judgment (CJ=wyrok, CO=postanowienie, CC=Conclusion AG)
  - BBBB = numer (zerami z lewa)

Przyklady:
  C-260/18 Dziubak     -> 62018CJ0260
  C-26/13 Kasler       -> 62013CJ0026
  C-377/14 Radlinger   -> 62014CJ0377
  C-176/17 Profi Credit -> 62017CJ0176

Usage::

    uv run python -m src.scrape.ue.tsue           # cały priority list
    uv run python -m src.scrape.ue.tsue --case C-260/18
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup

# Setup PYTHONPATH for direct module execution.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scrape.ue.common import (  # noqa: E402
    LICENSE_EURLEX,
    TODAY,
    EurLexFormats,
    Fetcher,
    ScrapeStats,
    build_citation_tsue,
    normalize_inline,
    write_json,
    write_jsonl,
)

logger = logging.getLogger("scrape.ue.tsue")


# === Configuration: priority orzeczenia ===


@dataclass(frozen=True)
class TSUECase:
    """Per-case metadata for priority cases."""

    case_id: str  # "C-260/18"
    celex_id: str  # "62018CJ0260"
    case_name_short: str  # "Dziubak" — key party name
    case_name_full: str  # "Kamil Dziubak, Justyna Dziubak v Raiffeisen Bank International AG"
    related_directives: tuple[str, ...]  # ("93/13/EWG",)
    legal_topic: str
    notes: str = ""


PRIORITY_CASES: tuple[TSUECase, ...] = (
    TSUECase(
        case_id="C-260/18",
        celex_id="62018CJ0260",
        case_name_short="Dziubak",
        case_name_full=("Kamil Dziubak, Justyna Dziubak v Raiffeisen Bank International AG"),
        related_directives=("93/13/EWG",),
        legal_topic="klauzule abuzywne, CHF kredyty hipoteczne, polskie tlo",
        notes="CRITICAL — fundament polskiego CHF orzecznictwa",
    ),
    TSUECase(
        case_id="C-26/13",
        celex_id="62013CJ0026",
        case_name_short="Kasler",
        case_name_full="Arpad Kasler, Hajnalka Kaslerne Rabai v OTP Jelzalogbank Zrt",
        related_directives=("93/13/EWG",),
        legal_topic="przejrzystosc klauzul walutowych, CHF",
        notes="prejudycjalny standard transparentnosci",
    ),
    TSUECase(
        case_id="C-377/14",
        celex_id="62014CJ0377",
        case_name_short="Radlinger",
        case_name_full="Ernst Georg Radlinger, Helena Radlingerova v Finway a.s.",
        related_directives=("93/13/EWG", "2008/48/WE"),
        legal_topic="klauzule niedozwolone, kredyt konsumencki, postepowanie egzekucyjne",
    ),
    TSUECase(
        case_id="C-176/17",
        celex_id="62017CJ0176",
        case_name_short="Profi Credit Polska",
        case_name_full="Profi Credit Polska S.A. v Mariusz Wawrzosek",
        related_directives=("93/13/EWG", "2008/48/WE"),
        legal_topic="klauzule abuzywne, weksle, polskie postepowanie nakazowe",
    ),
    TSUECase(
        case_id="C-19/20",
        celex_id="62020CJ0019",
        case_name_short="Bank BPH",
        case_name_full="I.W., R.W. v Bank BPH SA",
        related_directives=("93/13/EWG",),
        legal_topic="CHF, skutek stwierdzenia abuzywnosci, modyfikacja klauzul",
    ),
    TSUECase(
        case_id="C-269/95",
        celex_id="61995CJ0269",
        case_name_short="Benincasa",
        case_name_full="Francesco Benincasa v Dentalkit Srl",
        related_directives=(),
        legal_topic="definicja konsumenta, brak ochrony dla dzialalnosci zawodowej",
        notes="HISTORYCZNY (1997) — moze nie miec PL wersji, skip jesli brak",
    ),
    TSUECase(
        case_id="C-464/01",
        celex_id="62001CJ0464",
        case_name_short="Gruber",
        case_name_full="Johann Gruber v Bay Wa AG",
        related_directives=(),
        legal_topic="umowa mieszana (consumer / professional), test dominujacego celu",
        notes="2005 — moze nie miec PL wersji",
    ),
    TSUECase(
        case_id="C-415/11",
        celex_id="62011CJ0415",
        case_name_short="Aziz",
        case_name_full="Mohamed Aziz v Caixa d'Estalvis de Catalunya, Tarragona i Manresa (Catalunyacaixa)",
        related_directives=("93/13/EWG",),
        legal_topic="postepowanie egzekucyjne, ochrona konsumenta, dostep do sadu",
    ),
    TSUECase(
        case_id="C-243/08",
        celex_id="62008CJ0243",
        case_name_short="Pannon GSM",
        case_name_full="Pannon GSM Zrt v Erzsebet Sustikne Gyorfi",
        related_directives=("93/13/EWG",),
        legal_topic="ex officio (z urzedu) kontrola klauzul abuzywnych przez sad",
    ),
    TSUECase(
        case_id="C-453/10",
        celex_id="62010CJ0453",
        case_name_short="Perenicova",
        case_name_full=("Jana Perenicova, Vladislav Perenic v SOS financ spol. s r. o."),
        related_directives=("93/13/EWG", "2005/29/WE"),
        legal_topic="skutek stwierdzenia abuzywnosci, dalsze trwanie umowy",
    ),
    # Additional CHF / klauzule kredytowe seria (post-Dziubak, krytyczne dla polskiego stanu)
    TSUECase(
        case_id="C-118/17",
        celex_id="62017CJ0118",
        case_name_short="Dunai",
        case_name_full="Zsuzsanna Dunai v ERSTE Bank Hungary Zrt",
        related_directives=("93/13/EWG",),
        legal_topic="CHF kredyty, skutek dla umowy ze stwierdzonej abuzywnosci",
    ),
    TSUECase(
        case_id="C-186/16",
        celex_id="62016CJ0186",
        case_name_short="Andriciuc",
        case_name_full="Ruxandra Paula Andriciuc i in. v Banca Romaneasca SA",
        related_directives=("93/13/EWG",),
        legal_topic="ryzyko walutowe, obowiazek informacyjny banku, CHF",
    ),
    TSUECase(
        case_id="C-212/20",
        celex_id="62020CJ0212",
        case_name_short="A.S. SA",
        case_name_full="M.P., B.P. v A.S. SA",
        related_directives=("93/13/EWG",),
        legal_topic="CHF, sredni kurs, mechanizm zmiany klauzul",
    ),
    TSUECase(
        case_id="C-520/21",
        celex_id="62021CJ0520",
        case_name_short="Bank M.",
        case_name_full="A.S. v Bank M. S.A.",
        related_directives=("93/13/EWG",),
        legal_topic="CHF, wynagrodzenie banku za korzystanie z kapitalu, polskie pytanie prejudycjalne",
        notes="2023, polski pytanie prejudycjalne Sadu Rejonowego dla Warszawy-Sródmiescia",
    ),
    # Odstapienie od umowy (CRD)
    TSUECase(
        case_id="C-249/21",
        celex_id="62021CJ0249",
        case_name_short="Fuhrmann-2",
        case_name_full="Fuhrmann-2-GmbH v B.",
        related_directives=("2011/83/UE",),
        legal_topic="przycisk 'zamow z obowiazkiem zaplaty', wymogi informacyjne",
    ),
    TSUECase(
        case_id="C-208/19",
        celex_id="62019CJ0208",
        case_name_short="NK Construction",
        case_name_full="NK v MS, AS, ZS",
        related_directives=("2011/83/UE",),
        legal_topic="umowy zawierane poza lokalem przedsiebiorstwa, odstapienie",
    ),
    # CCD - kredyt konsumencki
    TSUECase(
        case_id="C-449/13",
        celex_id="62013CJ0449",
        case_name_short="CA Consumer Finance",
        case_name_full="CA Consumer Finance SA v Ingrid Bakkaus i in.",
        related_directives=("2008/48/WE",),
        legal_topic="ocena zdolnosci kredytowej, obowiazki banku",
    ),
    TSUECase(
        case_id="C-42/15",
        celex_id="62015CJ0042",
        case_name_short="Home Credit Slovakia",
        case_name_full="Home Credit Slovakia a.s. v Klara Biroova",
        related_directives=("2008/48/WE",),
        legal_topic="forma pisemna umowy kredytu, sankcje za brak wymaganej tresci",
    ),
    TSUECase(
        case_id="C-66/19",
        celex_id="62019CJ0066",
        case_name_short="Kreissparkasse",
        case_name_full="JC v Kreissparkasse Saarlouis",
        related_directives=("2008/48/WE",),
        legal_topic="odstapienie od umowy kredytu, wymogi informacyjne, jasnosc",
    ),
    TSUECase(
        case_id="C-565/12",
        celex_id="62012CJ0565",
        case_name_short="LCL",
        case_name_full="LCL Le Credit Lyonnais SA v Fesih Kalhan",
        related_directives=("2008/48/WE",),
        legal_topic="sankcje za naruszenie obowiazku oceny zdolnosci kredytowej",
    ),
    # Nieuczciwe praktyki (UCPD)
    TSUECase(
        case_id="C-540/08",
        celex_id="62008CJ0540",
        case_name_short="Mediaprint",
        case_name_full="Mediaprint Zeitungs- und Zeitschriftenverlag GmbH & Co. KG v 'Osterreich'-Zeitungsverlag GmbH",
        related_directives=("2005/29/WE",),
        legal_topic="zakaz nieuczciwych praktyk, sprzedaz z premia",
    ),
    TSUECase(
        case_id="C-628/17",
        celex_id="62017CJ0628",
        case_name_short="Orange Polska",
        case_name_full="Prezes Urzedu Ochrony Konkurencji i Konsumentow v Orange Polska S.A.",
        related_directives=("2005/29/WE",),
        legal_topic="agresywne praktyki handlowe, polskie pytanie prejudycjalne, telekomunikacja",
        notes="polskie tlo: UOKiK v Orange",
    ),
    # Wymogi informacyjne + odstapienie
    TSUECase(
        case_id="C-336/03",
        celex_id="62003CJ0336",
        case_name_short="easyCar",
        case_name_full="easyCar (UK) Ltd v Office of Fair Trading",
        related_directives=("97/7/WE",),
        legal_topic="wylaczenia z prawa odstapienia, najem samochodow online",
    ),
    # CHF/klauzule kontynuacja
    TSUECase(
        case_id="C-70/17",
        celex_id="62017CJ0070",
        case_name_short="Abanca",
        case_name_full=("Abanca Corporacion Bancaria SA v Alberto Garcia Salamanca Santos"),
        related_directives=("93/13/EWG",),
        legal_topic="klauzula natychmiastowej wymagalnosci, uzupelnianie umowy",
    ),
    TSUECase(
        case_id="C-125/18",
        celex_id="62018CJ0125",
        case_name_short="Gomez del Moral Guasch",
        case_name_full="Marc Gomez del Moral Guasch v Bankia SA",
        related_directives=("93/13/EWG",),
        legal_topic="klauzula stopy IRPH, indeks oprocentowania, przejrzystosc",
        notes="korekta numeracji 2026-05-16: C-125/18 (nie C-126/18)",
    ),
    TSUECase(
        case_id="C-407/18",
        celex_id="62018CJ0407",
        case_name_short="Addiko Bank",
        case_name_full="Aleš Kuhar, Jožef Kuhar v Addiko Bank d.d.",
        related_directives=("93/13/EWG",),
        legal_topic="postepowanie egzekucyjne, ochrona konsumenta",
    ),
    TSUECase(
        case_id="C-472/10",
        celex_id="62010CJ0472",
        case_name_short="Invitel",
        case_name_full=("Nemzeti Fogyasztovedelmi Hatosag v Invitel Tavkozlesi Zrt"),
        related_directives=("93/13/EWG",),
        legal_topic="kontrola abstrakcyjna klauzul standardowych, telefonia",
    ),
    TSUECase(
        case_id="C-269/15",
        celex_id="62015CJ0269",
        case_name_short="Allianz Vorsorgekasse",
        case_name_full="Allianz Vorsorgekasse",
        related_directives=("93/13/EWG",),
        legal_topic="ubezpieczenia, klauzule abuzywne",
    ),
    # CRD-related additional
    TSUECase(
        case_id="C-380/17",
        celex_id="62017CJ0380",
        case_name_short="Verbraucherzentrale Berlin",
        case_name_full="Verbraucherzentrale Berlin e.V. v Unimatic Vertriebs GmbH",
        related_directives=("2011/83/UE",),
        legal_topic="odstapienie, towary wykonywane na specjalne zamowienie",
    ),
    TSUECase(
        case_id="C-485/17",
        celex_id="62017CJ0485",
        case_name_short="Verbraucherzentrale Berlin (umowy oprocentowane)",
        case_name_full=("Verbraucherzentrale Berlin e.V. v Unimatic Vertriebs GmbH"),
        related_directives=("2011/83/UE",),
        legal_topic="dostarczenie towarow, prawo odstapienia",
    ),
)


# === Schema (mirrors halu.schemas.TSUEOrzeczenie) ===


@dataclass
class TSUERecord:
    """Single TSUE judgment record."""

    case_id: str
    celex_id: str
    case_name: str
    data_orzeczenia: str | None  # ISO date or None
    sklad: str | None
    streszczenie: str | None
    tezy_kluczowe: list[str]
    pelna_tresc: str
    citation_string: str
    license: str
    scrape_date: str
    source_url: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case_id,
            "celex_id": self.celex_id,
            "case_name": self.case_name,
            "data_orzeczenia": self.data_orzeczenia,
            "sklad": self.sklad,
            "streszczenie": self.streszczenie,
            "tezy_kluczowe": self.tezy_kluczowe,
            "pelna_tresc": self.pelna_tresc,
            "citation_string": self.citation_string,
            "license": self.license,
            "scrape_date": self.scrape_date,
            "source_url": self.source_url,
            "metadata": self.metadata,
        }


# === Detection of "no PL version" ===


def is_no_pl_version(html: str) -> bool:
    """Check if EUR-Lex returned the EN landing page (no PL document exists).

    Detection markers:
    - <title> contains 'EUR-Lex - CELEX:...' (landing only, not document)
    - No PL legal content (e.g. no 'Wyrok TRYBUNAŁU' or similar PL keyword)
    """
    if "<title>EUR-Lex" in html[:5000]:
        # Check if document body has Polish content
        # Simple heuristic: look for typical Polish judgment keyword
        if re.search(r"WYROK\s+TRYBUNA[ŁL]U", html, re.IGNORECASE):
            return False
        if re.search(r"\borzeka\s+co\s+nast", html, re.IGNORECASE):
            return False
        if re.search(r"\bArtyku[lł]\s+\d", html):
            return False
        return True
    return False


# === Date and metadata extraction ===

POLISH_MONTHS_TO_NUM = {
    "stycznia": 1,
    "lutego": 2,
    "marca": 3,
    "kwietnia": 4,
    "maja": 5,
    "czerwca": 6,
    "lipca": 7,
    "sierpnia": 8,
    "września": 9,
    "wrzesnia": 9,
    "października": 10,
    "pazdziernika": 10,
    "listopada": 11,
    "grudnia": 12,
}


def extract_judgment_date(text: str) -> str | None:
    """Extract date z naglowka 'WYROK TRYBUNAŁU (...) z dnia D miesiac YYYY r.'.

    Limits search to first 3000 chars (header) to avoid matching dates within
    body content (e.g. cytowanej daty wejscia w zycie). Walks 'z dnia D MIES YYYY r.'
    pattern.
    """
    head = text[:3000]
    m = re.search(
        r"z\s+dnia\s+(\d{1,2})\s+(\w+)\s+(\d{4})\s*r\.",
        head,
        re.IGNORECASE,
    )
    if not m:
        return None
    day = int(m.group(1))
    month_word = m.group(2).lower()
    month = POLISH_MONTHS_TO_NUM.get(month_word)
    if not month:
        return None
    year = int(m.group(3))
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None


def extract_sklad(text: str) -> str | None:
    """Extract izba i sedziowie z 'TRYBUNAŁ (izba)' header."""
    m = re.search(
        r"TRYBUNA[ŁL]\s+\(([^)]+)\)\s*,?\s*w\s+sk[ł]adzie\s*:?\s*([^,]{2,400})",
        text,
        re.IGNORECASE,
    )
    if not m:
        # Simpler: just izba
        m = re.search(r"WYROK\s+TRYBUNA[ŁL]U\s*\(([^)]+)\)", text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return None
    izba = m.group(1).strip()
    sedziowie_tail = m.group(2).strip()
    # Trim sedziowie_tail at first sentence end
    sedziowie_tail = sedziowie_tail.split(",")[0].strip()
    return f"{izba}: {sedziowie_tail}"


def extract_streszczenie(text: str) -> str | None:
    """Extract descriptors (key legal terms) z header pre-orzeczenie.

    Najczesciej tuz po dacie wyroku jest lista pojec rozdzielonych mysliknikami:
    'Odeslanie prejudycjalne – Dyrektywa 93/13/EWG – Umowy zawierane z konsumentami – ...'
    """
    m = re.search(
        r"WYROK\s+TRYBUNA[ŁL]U[^(]*\([^)]+\)\s+z\s+dnia\s+\d{1,2}\s+\w+\s+\d{4}\s+r\.\s*(?:\(\s*\*\d*\s*\))?\s*([^(]{50,2500})",
        text,
        re.IGNORECASE,
    )
    if not m:
        return None
    tail = m.group(1).strip()
    # Cut off at 'W sprawie' or 'TRYBUNAŁ' marker
    cut_idx = re.search(r"\b(W\s+sprawie|TRYBUNA[ŁL]|sprawie\s+C-)", tail, re.IGNORECASE)
    if cut_idx:
        tail = tail[: cut_idx.start()]
    tail = normalize_inline(tail)
    # Limit length
    return tail[:2000] if tail else None


def extract_tezy_kluczowe(text: str) -> list[str]:
    """Extract operative part / sentencja po 'Trybunał orzeka, co następuje:' marker.

    Po tym markerze sa numerowane punkty (1), 2), 3)) ktore stanowia rozstrzygniecie.
    """
    out: list[str] = []
    m = re.search(r"orzeka\s*,?\s*co\s+nast[ęe]puje\s*:?", text, re.IGNORECASE)
    if not m:
        return out
    tail = text[m.end() :]
    # Cut at typical document end (signatures, language declaration)
    end_match = re.search(
        r"(?:Podpisy|Z\s+powyzszych\s+wzgledow|^\s*[A-Z]\.\s+[A-Z][a-z]+,?\s+(?:prezes|sędzia)|\bSekretarz\b)",
        tail,
        re.IGNORECASE | re.MULTILINE,
    )
    if end_match:
        tail = tail[: end_match.start()]
    # Split na numbered points "1)" "2)" "3)"
    points = re.findall(r"(?ms)(?:^|\n)\s*(\d+)\)\s+(.+?)(?=\n\s*\d+\)|\Z)", tail)
    for _num, body in points:
        body_clean = normalize_inline(body)
        if 20 <= len(body_clean) <= 5000:
            out.append(body_clean)
    if not out:
        # Single-point sentencja — take whole tail (limited)
        single = normalize_inline(tail)
        if 20 <= len(single) <= 5000:
            out.append(single)
    return out


# === Parser ===


def parse_judgment_html(html: str, case: TSUECase, source_url: str) -> TSUERecord | None:
    """Parse pojedynczy TSUE judgment HTML."""
    if is_no_pl_version(html):
        logger.warning("No PL version for %s (%s)", case.case_id, case.celex_id)
        return None

    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style"]):
        tag.decompose()

    # Full text — collect all <p> tags from body
    plain_text = normalize_inline(soup.get_text(" ", strip=True))
    if len(plain_text) < 500:
        logger.warning(
            "Suspiciously short text for %s (%d chars) — possible empty PL doc",
            case.case_id,
            len(plain_text),
        )
        return None

    # Extract structured fields
    data_orzeczenia = extract_judgment_date(plain_text)
    sklad = extract_sklad(plain_text)
    streszczenie = extract_streszczenie(plain_text)
    tezy = extract_tezy_kluczowe(plain_text)

    # Build pelna_tresc by taking soup paragraphs with preserved paragraph breaks
    paragraphs_text: list[str] = []
    for p in soup.find_all("p"):
        t = normalize_inline(p.get_text(" ", strip=True))
        if t:
            paragraphs_text.append(t)
    pelna_tresc = "\n".join(paragraphs_text)
    # NFC normalize via re-collapse
    pelna_tresc = normalize_inline(pelna_tresc.replace("\n", "  "))
    # Note: pelna_tresc loses paragraph breaks; that's intentional for chunkability later.

    # Citation string
    data_dt: datetime | None = None
    if data_orzeczenia:
        try:
            data_dt = datetime.fromisoformat(data_orzeczenia)
        except ValueError:
            pass
    citation = build_citation_tsue(
        case.case_id, case_name_short=case.case_name_short, data_orzeczenia=data_dt
    )

    record = TSUERecord(
        case_id=case.case_id,
        celex_id=case.celex_id,
        case_name=case.case_name_full,
        data_orzeczenia=data_orzeczenia,
        sklad=sklad,
        streszczenie=streszczenie,
        tezy_kluczowe=tezy,
        pelna_tresc=pelna_tresc,
        citation_string=citation,
        license=LICENSE_EURLEX,
        scrape_date=TODAY,
        source_url=source_url,
        metadata={
            "case_name_short": case.case_name_short,
            "related_directives": list(case.related_directives),
            "legal_topic": case.legal_topic,
            "jurystdykcja": "TSUE (Court of Justice EU)",
            "notes": case.notes,
        },
    )
    return record


def validate_records(records: list[TSUERecord]) -> list[TSUERecord]:
    """Validate records against the strict Pydantic schema (halu.schemas.TSUEOrzeczenie)."""
    from halu.schemas import TSUEOrzeczenie

    valid: list[TSUERecord] = []
    drop_count = 0
    for r in records:
        d = r.as_dict()
        d["scrape_date"] = date.fromisoformat(d["scrape_date"])
        if d["data_orzeczenia"]:
            d["data_orzeczenia"] = date.fromisoformat(d["data_orzeczenia"])
        try:
            TSUEOrzeczenie(**d)
            valid.append(r)
        except Exception as exc:
            logger.warning("drop invalid record %s: %s", r.case_id, exc)
            drop_count += 1
    if drop_count:
        logger.warning("dropped %d invalid records", drop_count)
    return valid


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--case", default=None, help="Pobierz tylko jedna sprawe po case_id, np. C-260/18"
    )
    parser.add_argument(
        "--output",
        default=str(
            Path(__file__).resolve().parents[3] / "data" / "raw" / "tsue_orzeczenia_2026-05-16"
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
    targets = [c for c in PRIORITY_CASES if (args.case is None or c.case_id == args.case)]
    if not targets:
        logger.error("No matching case for --case %s", args.case)
        return 2

    records: list[TSUERecord] = []
    skipped_no_pl: list[str] = []
    fetch_failures: list[str] = []

    for case in targets:
        fmt = EurLexFormats(case.celex_id)
        logger.info("=== %s (%s) — %s ===", case.case_id, case.celex_id, case.case_name_short)
        resp = fetcher.get(fmt.url_html)
        if resp is None:
            logger.error("FETCH FAIL %s", fmt.url_html)
            fetch_failures.append(case.case_id)
            continue
        rec = parse_judgment_html(resp.text, case, fmt.url_html)
        if rec is None:
            skipped_no_pl.append(case.case_id)
            continue
        records.append(rec)

    # Validate
    records = validate_records(records)

    # Output combined JSONL
    write_jsonl([r.as_dict() for r in records], output_dir / "tsue_orzeczenia.jsonl")

    # Per-case meta (only successful ones)
    per_case_dir = output_dir / "per_case_meta"
    per_case_dir.mkdir(parents=True, exist_ok=True)
    for r in records:
        safe_id = r.case_id.replace("/", "_")
        meta = {
            "case_id": r.case_id,
            "celex_id": r.celex_id,
            "case_name": r.case_name,
            "case_name_short": r.metadata.get("case_name_short"),
            "data_orzeczenia": r.data_orzeczenia,
            "sklad": r.sklad,
            "streszczenie": r.streszczenie,
            "tezy_kluczowe": r.tezy_kluczowe,
            "related_directives": r.metadata.get("related_directives", []),
            "legal_topic": r.metadata.get("legal_topic"),
            "notes": r.metadata.get("notes"),
            "citation_string": r.citation_string,
            "pelna_tresc_length": len(r.pelna_tresc),
            "license": r.license,
            "scrape_date": r.scrape_date,
            "source_url": r.source_url,
        }
        write_json(meta, per_case_dir / f"{safe_id}_meta.json")

    # Summary
    stats = ScrapeStats(
        source="TSUE_consumer_priority",
        scrape_date=TODAY,
        license=LICENSE_EURLEX,
        total_records=len(records),
        skipped_no_pl=skipped_no_pl,
        notes=(
            f"fetch_failures={fetch_failures} | total_candidates={len(targets)} "
            f"| ok={len(records)} | skipped_no_pl={len(skipped_no_pl)}"
        ),
    )
    write_json(stats, output_dir / "_summary.json")

    logger.info(
        "DONE — %d/%d records scraped (skipped no PL: %d, fetch fail: %d)",
        len(records),
        len(targets),
        len(skipped_no_pl),
        len(fetch_failures),
    )
    if skipped_no_pl:
        logger.warning("Skipped (no PL version): %s", skipped_no_pl)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
