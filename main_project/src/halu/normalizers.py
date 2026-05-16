"""Normalizers: raw source records → unified ``Chunk`` (option b per Magda 2026-05-16).

Każda rodzina źródeł ma swój ``normalize_*`` adapter:

- ``normalize_eli_record`` — ELI ustaw (S0 + S1), fix BLOCKER 1 dataset_builder bug
  (``para`` → ``paragraf``, missing ``chunk_id``, ``ustawa_data_uchwalenia`` from metadata)
- ``normalize_uokik_qa`` — UOKiK Q&A FAQ pairs
- ``normalize_consumer_question`` — fora/Reddit consumer questions
- ``normalize_encyclopedic`` — Wikipedia/NGO/gov.pl (E1)
- ``normalize_consumer_document`` — long-form PDF (E4)
- ``normalize_ue_directive`` — UE dyrektywy (S3)
- ``normalize_tsue_judgment`` — TSUE orzeczenia (S3)
- ``normalize_uokik_decision`` — decyzje UOKiK (S2)
- ``normalize_court_judgment`` — orzeczenia sądowe (S2 + E4)

Plus ``categorize_chunk`` — heuristic multi-label categorization based on title +
content keyword matching. Stratified eval split downstream używa ``categories`` field.

Per Magda decision 2b: ``FINANCE_ADJACENT`` tag dla RF FAQ (świadomy bias).
"""

from __future__ import annotations

import hashlib
import logging
import unicodedata
from datetime import date, datetime
from typing import Any

from src.halu.citation_extractor import extract_all_citations
from src.halu.schemas import Category, Chunk, SourceType

logger = logging.getLogger(__name__)

# === Date parsing ===


def _parse_date(value: Any) -> date:
    """Parse date z ISO string lub date object."""
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value[:10]).date()
    raise ValueError(f"Cannot parse date from {value!r}")


def _ensure_nfc(text: str) -> str:
    """Force NFC normalization (idempotent)."""
    if not text:
        return ""
    return unicodedata.normalize("NFC", text)


def _stable_chunk_id(prefix: str, *parts: str) -> str:
    """Generate deterministic chunk_id from prefix + identifying parts."""
    suffix = "_".join(str(p).replace("/", "_").replace(" ", "_") for p in parts if p)
    return (
        f"{prefix}_{suffix}"
        if suffix
        else f"{prefix}_{hashlib.sha1(prefix.encode()).hexdigest()[:8]}"
    )


# === Categorization ===

_CATEGORY_KEYWORDS = {
    Category.CONSUMER_CORE: [
        "prawa konsumenta",
        "konsument",
        "ustawa o prawach konsumenta",
        "UPK",
    ],
    Category.CONSUMER_CONTRACT: [
        "umow",
        "rękojm",
        "gwarancj",
        "wad",
        "zgodność towaru",
        "świadczeni",
    ],
    Category.CONSUMER_CREDIT: [
        "kredyt konsumencki",
        "kredyt hipoteczny",
        "RRSO",
        "pożyczka",
        "frank szwajcarski",
        "CHF",
        "raty",
    ],
    Category.CONSUMER_DIGITAL: [
        "e-commerce",
        "sklep internetowy",
        "umowa zawarta na odległość",
        "treść cyfrow",
        "usług cyfrow",
        "dane osobow",
    ],
    Category.CONSUMER_TELECOM: [
        "prawo telekomunikacyjne",
        "operator telekomunikacyjny",
        "abonament",
        "umowa o świadczenie usług telekomunikacyjnych",
    ],
    Category.CONSUMER_RETURN_REFUND: [
        "zwrot",
        "odstąpienie",
        "14 dni",
        "reklamacj",
        "zwrócić towar",
    ],
    Category.CONSUMER_UNFAIR_PRACTICES: [
        "klauzul niedozwolon",
        "klauzul abuzywn",
        "nieuczciw praktyk",
        "wprowadzanie w błąd",
    ],
    Category.CONSUMER_DISPUTE_RESOLUTION: [
        "ADR",
        "mediacj",
        "arbitraż",
        "rzecznik konsumentów",
        "pozasądowe rozwiązywanie sporów",
    ],
    Category.FINANCE_ADJACENT: [
        "ubezpieczeni",
        "bank",
        "polisa",
        "fundusze",
        "inwestycje",
        "rzecznik finansowy",
        "AC",
        "OC",
    ],
    Category.EU_DIRECTIVE: [
        "dyrektywa",
        "rozporządzenie (UE)",
        "prawo Unii Europejskiej",
    ],
    Category.TSUE_JUDGMENT: [
        "TSUE",
        "Trybunał Sprawiedliwości",
        "CJEU",
        "wyrok C-",
    ],
    Category.COURT_PRECEDENT: [
        "wyrok SN",
        "uchwała SN",
        "wyrok Sądu Najwyższego",
        "sygn. akt",
    ],
    Category.REGULATORY_DECISION: [
        "Prezes UOKiK",
        "decyzja UOKiK",
        "kara pieniężna UOKiK",
    ],
}


def categorize_chunk(title: str, tresc: str) -> list[Category]:
    """Heuristic multi-label categorization based on title + content keywords."""
    combined = (title + " " + tresc).lower()
    matched: list[Category] = []
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw.lower() in combined for kw in keywords):
            matched.append(category)
    return matched or [Category.OTHER]


# === Normalizers per source ===


def normalize_eli_record(
    record: dict[str, Any], source_url_base: str = "https://api.sejm.gov.pl"
) -> Chunk:
    """ELI ustawy → unified Chunk. Fix BLOCKER 1 (per E3 EDA findings).

    Bug fix:
    - ``para`` → ``paragraf`` (raw scrape używa skrótu)
    - missing ``chunk_id`` → synthesize from ustawa_id + art + ust + pkt
    - ``ustawa_data_uchwalenia`` w ``metadata`` → top-level
    """
    ustawa_id = record["ustawa_id"]
    art = record["art"]
    # Handle both 'para' (raw scrape) and 'paragraf' (canonical)
    paragraf = record.get("paragraf") or record.get("para")
    ust = record.get("ust")
    pkt = record.get("pkt")
    lit = record.get("lit")

    # Synthesize chunk_id deterministically
    chunk_id = _stable_chunk_id(
        "eli",
        ustawa_id,
        f"art_{art}",
        f"par_{paragraf}" if paragraf else "",
        f"ust_{ust}" if ust else "",
        f"pkt_{pkt}" if pkt else "",
        f"lit_{lit}" if lit else "",
    )

    metadata = dict(record.get("metadata", {}))
    metadata.update(
        {
            "ustawa_id": ustawa_id,
            "ustawa_title": record["ustawa_title"],
            "art": art,
            "paragraf": paragraf,
            "ust": ust,
            "pkt": pkt,
            "lit": lit,
        }
    )

    tresc = _ensure_nfc(record["tresc"])

    return Chunk(
        chunk_id=chunk_id,
        source_type=SourceType.LEGAL_STATUTE,
        source="isap.sejm.gov.pl",
        source_url=record.get("source_url", source_url_base),
        title=record["ustawa_title"],
        tresc=tresc,
        citation_string=record.get("citation_string"),
        cited_articles=extract_all_citations(tresc),
        categories=categorize_chunk(record["ustawa_title"], tresc),
        license="urzędowe (Art. 4 ust. 2 PrAut + TDM exception 2024)",
        scrape_date=_parse_date(record["scrape_date"]),
        process_date=date.today(),
        metadata=metadata,
    )


def normalize_uokik_qa(record: dict[str, Any]) -> Chunk:
    """UOKiK Q&A FAQ → Chunk (treść = question + ' ' + answer)."""
    tresc = _ensure_nfc(record["question"] + "\n\nOdpowiedź: " + record["answer"])
    categories = categorize_chunk(record.get("category", ""), tresc)

    return Chunk(
        chunk_id=f"uokik_qa_{record['qa_id']}",
        source_type=SourceType.QA_GOLD,
        source="prawakonsumenta.uokik.gov.pl",
        source_url=record["source_url"],
        title=record["question"][:200],
        tresc=tresc,
        citation_string=None,
        cited_articles=record.get("cited_articles", []) or extract_all_citations(tresc),
        categories=categories,
        license="urzędowe (Art. 4 ust. 2 PrAut)",
        scrape_date=_parse_date(record["scrape_date"]),
        process_date=date.today(),
        metadata={
            "qa_id": record["qa_id"],
            "category": record.get("category"),
            "question": record["question"],
            "answer": record["answer"],
        },
    )


def normalize_consumer_question(record: dict[str, Any]) -> Chunk:
    """Forum/Reddit consumer question → Chunk."""
    tresc = _ensure_nfc(record["question"])
    if record.get("context"):
        tresc += "\n\nKontekst: " + _ensure_nfc(record["context"])

    return Chunk(
        chunk_id=f"qraw_{record['question_id']}",
        source_type=SourceType.QA_RAW,
        source=record["source"],
        source_url=record["source_url"],
        title=record["question"][:200],
        tresc=tresc,
        citation_string=None,
        cited_articles=extract_all_citations(tresc),
        categories=categorize_chunk("", tresc),
        license="fair-use (Art. 29 PrAut, academic + anonymized)",
        scrape_date=_parse_date(record["scrape_date"]),
        process_date=date.today(),
        metadata={
            "question_id": record["question_id"],
            "category": record.get("category"),
            "extracted_topics": record.get("extracted_topics", []),
        },
    )


def normalize_encyclopedic(record: dict[str, Any]) -> Chunk:
    """Wikipedia/NGO/gov.pl encyclopedic chunk → unified Chunk.

    Handles two shapes from E1 extended scrape:
    - Standard EncyclopedicChunk (Wikipedia, Federacja, UOKiK news, gov.pl):
      ``{chunk_id, source, source_url, title, section, tresc, license, ...}``
    - Q&A-like (RF FAQ): ``{qa_id, question, answer, source, ...}`` — synthesize tresc
    """
    # Detect Q&A-like shape (RF FAQ)
    if "question" in record and "answer" in record:
        tresc = _ensure_nfc(record["question"] + "\n\nOdpowiedź: " + record["answer"])
        title = record["question"][:200]
        chunk_id = record.get("chunk_id") or f"qa_{record.get('qa_id', 'unknown')}"
        source_type = SourceType.QA_GOLD  # treat FAQ as QA (z citations w answer)
    else:
        tresc = _ensure_nfc(record["tresc"])
        title = record["title"]
        chunk_id = record["chunk_id"]
        source_type = SourceType.ENCYCLOPEDIC

    # Detect finance_adjacent dla RF FAQ per Magda decision 2b
    extra_categories: list[Category] = []
    if "rf.gov.pl" in record.get("source", ""):
        extra_categories.append(Category.FINANCE_ADJACENT)

    categories = categorize_chunk(title, tresc) + extra_categories
    categories = list(dict.fromkeys(categories))

    return Chunk(
        chunk_id=chunk_id,
        source_type=source_type,
        source=record["source"],
        source_url=record["source_url"],
        title=title,
        tresc=tresc,
        citation_string=None,
        cited_articles=record.get("cited_articles", []) or extract_all_citations(tresc),
        categories=categories,
        license=record.get("license", "unknown"),
        scrape_date=_parse_date(record["scrape_date"]),
        process_date=date.today(),
        metadata=dict(record.get("metadata", {})),
    )


def normalize_consumer_document(record: dict[str, Any]) -> Chunk:
    """E4 long-form PDF chunk → Chunk (UOKiK poradniki, RF analizy, FK, orzeczenia)."""
    tresc = _ensure_nfc(record["tresc"])
    title = record.get("title") or record.get("document_title") or "untitled"

    # Detect court judgment vs PDF document
    if "orzeczenie" in record.get("document_type", "").lower() or "orz_" in record.get(
        "chunk_id", ""
    ):
        source_type = SourceType.LEGAL_COURT_JUDGMENT
    else:
        source_type = SourceType.LEGAL_DOCUMENT_PDF

    # Finance adjacent dla RF
    extra_categories: list[Category] = []
    if "rf.gov.pl" in record.get("source", "") or "rzecznik" in record.get("source", ""):
        extra_categories.append(Category.FINANCE_ADJACENT)

    categories = categorize_chunk(title, tresc) + extra_categories
    categories = list(dict.fromkeys(categories))

    return Chunk(
        chunk_id=record["chunk_id"],
        source_type=source_type,
        source=record.get("source", "unknown"),
        source_url=record.get("source_url", ""),
        title=title,
        tresc=tresc,
        citation_string=record.get("citation_string"),
        cited_articles=extract_all_citations(tresc),
        categories=categories,
        license=record.get("license", "urzędowe (Art. 4 ust. 2 PrAut)"),
        scrape_date=_parse_date(record["scrape_date"]),
        process_date=date.today(),
        metadata=dict(record.get("metadata", {})),
    )


def normalize_ue_directive(record: dict[str, Any]) -> Chunk:
    """UE dyrektywa chunk → Chunk (S3 output)."""
    tresc = _ensure_nfc(record["tresc"])
    title = record.get("direktywa_title_pl") or record.get("title", "untitled")

    return Chunk(
        chunk_id=record["chunk_id"]
        if "chunk_id" in record
        else _stable_chunk_id(
            "ue_dyr",
            record.get("celex_id", ""),
            record.get("art", ""),
            record.get("ust", ""),
            record.get("lit", ""),
        ),
        source_type=SourceType.LEGAL_UE_DIRECTIVE,
        source="eur-lex.europa.eu",
        source_url=record.get("source_url", ""),
        title=title,
        tresc=tresc,
        citation_string=record.get("citation_string"),
        cited_articles=extract_all_citations(tresc),
        categories=[Category.EU_DIRECTIVE] + categorize_chunk(title, tresc),
        license="EUR-Lex (© European Union, reuse per 2011/833/UE)",
        scrape_date=_parse_date(record["scrape_date"]),
        process_date=date.today(),
        metadata=dict(record.get("metadata", {})),
    )


def normalize_tsue_judgment(record: dict[str, Any]) -> Chunk:
    """TSUE orzeczenie → Chunk (S3 output)."""
    tresc = _ensure_nfc(record.get("pełna_treść") or record.get("tresc", ""))
    title = record.get("case_name") or record.get("title", "untitled")
    case_id = record.get("case_id", "unknown")

    return Chunk(
        chunk_id=record.get("chunk_id") or _stable_chunk_id("tsue", case_id),
        source_type=SourceType.LEGAL_TSUE_JUDGMENT,
        source="eur-lex.europa.eu",
        source_url=record.get("source_url", ""),
        title=title,
        tresc=tresc,
        citation_string=f"wyrok TSUE {case_id}",
        cited_articles=extract_all_citations(tresc),
        categories=[Category.TSUE_JUDGMENT] + categorize_chunk(title, tresc),
        license="EUR-Lex (© European Union, reuse per 2011/833/UE)",
        scrape_date=_parse_date(record["scrape_date"]),
        process_date=date.today(),
        metadata=dict(record.get("metadata", {})),
    )


def normalize_uokik_decision(record: dict[str, Any]) -> Chunk:
    """Decyzja Prezesa UOKiK → Chunk (S2 output)."""
    tresc = _ensure_nfc(record["tresc"])
    decyzja_id = record["decyzja_id"]

    return Chunk(
        chunk_id=record.get("chunk_id") or _stable_chunk_id("uokik_dec", decyzja_id),
        source_type=SourceType.LEGAL_UOKIK_DECISION,
        source="decyzje.uokik.gov.pl",
        source_url=record.get("source_url", ""),
        title=f"Decyzja UOKiK {decyzja_id}",
        tresc=tresc,
        citation_string=record.get("citation_string"),
        cited_articles=record.get("podstawy_prawne") or extract_all_citations(tresc),
        categories=[Category.REGULATORY_DECISION] + categorize_chunk("", tresc),
        license="urzędowe (Art. 4 ust. 2 PrAut)",
        scrape_date=_parse_date(record["scrape_date"]),
        process_date=date.today(),
        metadata=dict(record.get("metadata", {})),
    )


def normalize_court_judgment(record: dict[str, Any]) -> Chunk:
    """SN orzeczenie / sądy powszechne → Chunk (S2 + E4 output)."""
    tresc = _ensure_nfc(record.get("tresc") or record.get("uzasadnienie", ""))
    sygnatura = record.get("sygnatura") or record.get("sygn_akt", "unknown")
    title = record.get("title") or f"Wyrok {sygnatura}"

    return Chunk(
        chunk_id=record.get("chunk_id") or _stable_chunk_id("court", sygnatura),
        source_type=SourceType.LEGAL_COURT_JUDGMENT,
        source=record.get("source", "orzeczenia.ms.gov.pl"),
        source_url=record.get("source_url", ""),
        title=title,
        tresc=tresc,
        citation_string=f"sygn. akt {sygnatura}",
        cited_articles=extract_all_citations(tresc),
        categories=[Category.COURT_PRECEDENT] + categorize_chunk(title, tresc),
        license="urzędowe (Art. 4 ust. 2 PrAut)",
        scrape_date=_parse_date(record["scrape_date"]),
        process_date=date.today(),
        metadata=dict(record.get("metadata", {})),
    )


__all__ = [
    "categorize_chunk",
    "normalize_consumer_document",
    "normalize_consumer_question",
    "normalize_court_judgment",
    "normalize_eli_record",
    "normalize_encyclopedic",
    "normalize_tsue_judgment",
    "normalize_ue_directive",
    "normalize_uokik_decision",
    "normalize_uokik_qa",
]
