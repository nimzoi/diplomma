"""Polish legal citation extractor — regex-based parser.

Ekstrahuje cytacje typu:
- ``art. X``, ``art. X ust. Y``, ``art. X ust. Y pkt Z``, ``art. X ust. Y pkt Z lit. a``
- ``art. X § Y``, ``art. X-Y`` (zakres), ``art. X w zw. z art. Y``
- ``Dz.U. {rok} poz. {nr}`` (post-2012 numbering)
- ``Dz.U. {rok} Nr {nr} poz. {nr2}`` (pre-2012 numbering)
- Skróty: ``KC``, ``k.c.``, ``UPK``, ``k.p.c.``, ``KPK``, ``UOKK``, ``OchrKonsU``
- UE: ``Dyrektywa {rok}/{nr}/UE``, ``Dyrektywa (UE) {rok}/{nr}``, ``Rozporządzenie {rok}/{nr}``
- TSUE: ``C-{nr}/{rok}``, ``Sprawa C-{nr}/{rok}``, ``wyrok TSUE z dnia ... w sprawie ...``
- Polish: ``wyrok SN z dnia ... sygn. akt ...``

Output: list of canonical citation strings (deduped, NFC normalized).

Per Magda 2026-05-16: better citation recall (target 40-60% vs E1 heurystyczne 18.7%).
"""

from __future__ import annotations

import re
import unicodedata

# === Statute citation patterns (PL) ===

# art. X (opcjonalnie z suffix ^N dla superscript: art. 22^1)
_ART_PATTERN = re.compile(
    r"art\.\s*(\d+[a-z]?(?:\^?\d+)?)"
    r"(?:\s*§\s*(\d+[a-z]?))?"
    r"(?:\s*ust\.\s*(\d+[a-z]?))?"
    r"(?:\s*pkt\s*(\d+[a-z]?))?"
    r"(?:\s*lit\.\s*([a-z]+))?",
    re.IGNORECASE,
)

# Dz.U. {rok} poz. {nr} (post-2012)
_DZU_NEW_PATTERN = re.compile(
    r"Dz\.\s*U\.\s*(?:z\s+)?(\d{4})\s+poz\.\s*(\d+)",
    re.IGNORECASE,
)

# Dz.U. {rok} Nr {nr} poz. {nr2} (pre-2012)
_DZU_OLD_PATTERN = re.compile(
    r"Dz\.\s*U\.\s*(?:z\s+)?(\d{4})\s+Nr\s+(\d+)\s+poz\.\s*(\d+)",
    re.IGNORECASE,
)

# === Common Polish legal abbreviations ===

_ACT_ABBREVIATIONS = {
    # Pełne formy → skrót (do canonicalization)
    "ustawa o prawach konsumenta": "UPK",
    "kodeks cywilny": "KC",
    "kodeks postępowania cywilnego": "KPC",
    "kodeks karny": "KK",
    "kodeks postępowania karnego": "KPK",
    "ustawa o ochronie konkurencji i konsumentów": "UOKK",
    "ustawa o kredycie konsumenckim": "UKK",
    "ustawa o świadczeniu usług drogą elektroniczną": "UŚUDE",
    "prawo telekomunikacyjne": "PrTel",
    "prawo bankowe": "PrBank",
    "ustawa o usługach płatniczych": "UUP",
    "ustawa o przeciwdziałaniu nieuczciwym praktykom rynkowym": "UPNPR",
}

# Reverse lookup: skrót variants → canonical
_ABBREV_VARIANTS = {
    "k.c.": "KC",
    "kc": "KC",
    "k.p.c.": "KPC",
    "kpc": "KPC",
    "k.k.": "KK",
    "kk": "KK",
    "k.p.k.": "KPK",
    "kpk": "KPK",
    "upk": "UPK",
    "uokk": "UOKK",
}

# === UE / TSUE patterns ===

# Dyrektywa {rok}/{nr}/UE lub Dyrektywa (UE) {rok}/{nr}
_UE_DIRECTIVE_PATTERN = re.compile(
    r"Dyrektyw[ay]\s+(?:\(UE\)\s+)?(\d{4})/(\d+)(?:/(?:WE|UE|EWG))?",
    re.IGNORECASE,
)

# Rozporządzenie (UE) {rok}/{nr}
_UE_REGULATION_PATTERN = re.compile(
    r"Rozporządzeni[ae]\s+(?:\(UE\)\s+)?(\d{4})/(\d+)",
    re.IGNORECASE,
)

# TSUE/CJEU: C-{nr}/{rok lub yy}
_TSUE_PATTERN = re.compile(
    r"(?:sprawa\s+|wyrok.*?w\s+sprawie\s+)?C[-‑]?(\d+)/(\d{2,4})",
    re.IGNORECASE,
)

# === Polish court judgments ===

# Sygnatura akt: format `[I|II|III|IV|V] [CSK|CZP|UK|FK] {nr}/{rok}`
_SYGNATURA_PATTERN = re.compile(
    r"sygn\.\s*akt\s+([IVX]+\s+[A-ZŁŚŻŹĆ]+\s+\d+/\d+)",
    re.IGNORECASE,
)

# SN orzeczenie: `wyrok SN z dnia X w sprawie Y` lub `uchwała SN`
_SN_PATTERN = re.compile(
    r"(?:wyrok|uchwała|postanowienie)\s+SN\s+z\s+dnia\s+(\d{1,2}\.\d{1,2}\.\d{4})",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    """NFC normalization + whitespace collapse."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", " ".join(text.split()))


def extract_article_citations(text: str) -> list[str]:
    """Ekstraktuj cytacje typu art. X [§ P] [ust. U] [pkt K] [lit. l].

    Zwraca canonical form: 'art. {art}[ § {paragraf}][ ust. {ust}][ pkt {pkt}][ lit. {lit}]'.
    """
    citations: list[str] = []
    for match in _ART_PATTERN.finditer(text):
        art, paragraf, ust, pkt, lit = match.groups()
        parts = [f"art. {art}"]
        if paragraf:
            parts.append(f"§ {paragraf}")
        if ust:
            parts.append(f"ust. {ust}")
        if pkt:
            parts.append(f"pkt {pkt}")
        if lit:
            parts.append(f"lit. {lit.lower()}")
        citations.append(" ".join(parts))
    return citations


def extract_dziennik_ustaw(text: str) -> list[str]:
    """Ekstraktuj Dz.U. references (oba formaty: post-2012 i pre-2012)."""
    refs: list[str] = []
    for match in _DZU_NEW_PATTERN.finditer(text):
        rok, poz = match.groups()
        refs.append(f"Dz.U. {rok} poz. {poz}")
    for match in _DZU_OLD_PATTERN.finditer(text):
        rok, nr, poz = match.groups()
        refs.append(f"Dz.U. {rok} Nr {nr} poz. {poz}")
    return refs


def extract_act_abbreviations(text: str) -> list[str]:
    """Ekstraktuj skróty aktów prawnych (KC, KPC, UPK, k.c. itd.)."""
    found: set[str] = set()
    text_lower = text.lower()
    for variant, canonical in _ABBREV_VARIANTS.items():
        # Word boundary check (no partial matches)
        pattern = r"\b" + re.escape(variant) + r"\b"
        if re.search(pattern, text_lower):
            found.add(canonical)
    return sorted(found)


def extract_ue_citations(text: str) -> list[str]:
    """Ekstraktuj UE dyrektywy + rozporządzenia + TSUE sprawy."""
    citations: list[str] = []
    for match in _UE_DIRECTIVE_PATTERN.finditer(text):
        rok, nr = match.groups()
        citations.append(f"Dyrektywa {rok}/{nr}/UE")
    for match in _UE_REGULATION_PATTERN.finditer(text):
        rok, nr = match.groups()
        citations.append(f"Rozporządzenie (UE) {rok}/{nr}")
    for match in _TSUE_PATTERN.finditer(text):
        nr, rok = match.groups()
        if len(rok) == 2:
            rok = ("20" if int(rok) <= 30 else "19") + rok  # heuristic
        citations.append(f"C-{nr}/{rok}")
    return citations


def extract_court_judgments(text: str) -> list[str]:
    """Ekstraktuj sygnatury akt + SN orzeczenia."""
    citations: list[str] = []
    for match in _SYGNATURA_PATTERN.finditer(text):
        citations.append(f"sygn. akt {match.group(1)}")
    for match in _SN_PATTERN.finditer(text):
        citations.append(f"wyrok SN z {match.group(1)}")
    return citations


def extract_all_citations(text: str) -> list[str]:
    """Ekstraktuj WSZYSTKIE cytacje z tekstu, deduped, sorted.

    Łączy: art. references + Dz.U. + skróty aktów + UE + TSUE + sądy.
    """
    if not text:
        return []
    text = normalize_text(text)
    all_citations: set[str] = set()
    all_citations.update(extract_article_citations(text))
    all_citations.update(extract_dziennik_ustaw(text))
    all_citations.update(extract_act_abbreviations(text))
    all_citations.update(extract_ue_citations(text))
    all_citations.update(extract_court_judgments(text))
    return sorted(all_citations)


def has_citations(text: str) -> bool:
    """Quick boolean check czy text zawiera dowolne cytacje."""
    return bool(extract_all_citations(text))


__all__ = [
    "extract_act_abbreviations",
    "extract_all_citations",
    "extract_article_citations",
    "extract_court_judgments",
    "extract_dziennik_ustaw",
    "extract_ue_citations",
    "has_citations",
    "normalize_text",
]
