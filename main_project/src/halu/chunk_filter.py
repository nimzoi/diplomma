"""Chunk-level scope filter (post-normalization).

Per `KRYTYCZNA_ocena_scope_2026-05-16.md` Wariant B — drop ~50% chunks z v0.4
(17,862 → ~9k consumer_core focused) bez kasowania raw data.

**Audit trail:** `thesis_research/notes/scope_cleanup_decisions_2026-05-16.md`
zawiera per-source decyzje + uzasadnienie + defense scaffolding.

**3 policies:**

- ``strict`` — produkcyjny scope cleanup per Wariant B krytyka. Drop wszystko
  pasujące do `STRICT_DROP_SOURCES` + content patterns (CHF, ubezpieczenia bez
  banking). Used dla v0.5+.
- ``loose`` — keep edge cases (RF PDFs całość, SN orzeczenia całość, ELI Prawo
  bankowe całość). Drop tylko najbardziej oczywiste (uchylone ustawy, ING CSS).
  Compromise mode jeśli `strict` okazuje się za agresywny dla probe training.
- ``none`` — no filter (v0.4 backwards-compat behavior).

Filter operuje na normalized ``Chunk`` obiektach (po `normalizers.py`). Decyzje
opierają się na ``Chunk.metadata['ustawa_id']`` (dla ELI), ``Chunk.source`` (dla
S6 articles), ``Chunk.tresc`` content keywords (CHF/insurance disambiguation).

Returns ``FilterResult`` z (kept, dropped, drop_stats) — drop_stats keyed
per reason dla DATASET_CARD update.
"""

from __future__ import annotations

import logging
import re
from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

from src.halu.schemas import Category, Chunk, SourceType

logger = logging.getLogger(__name__)

# === Policy types ===

FilterPolicy = Literal["strict", "loose", "none"]

# === DROP source rules (per source/metadata) ===

# ELI ustawa_id → reason (drop full statute)
STRICT_DROP_ELI_USTAWY: dict[str, str] = {
    "DU/1964/296": "KPC — 96% NIE consumer-specific (procedural law)",
    "DU/2003/535": "Prawo upadłościowe — separate domain (future work R8)",
    "DU/1997/939": "Prawo bankowe — regulator-bank side, NIE consumer-rights centralne",
    "DU/2011/1175": "Usługi płatnicze — regulator-side, NIE consumer-rights",
    "DU/2003/2275": "UCHYLONA bezp. produktów (replaced by 2024/1221)",
    "DU/2002/1176": "UCHYLONA sprzedaż konsumencka (replaced by UPK 2014/827)",
    "DU/2000/271": "UCHYLONA ochrona praw konsumentów (replaced by UPK 2014/827)",
}

# Loose policy drops only uchylone (3 ustawy) + KPC
LOOSE_DROP_ELI_USTAWY: dict[str, str] = {
    "DU/2003/2275": "UCHYLONA bezp. produktów (replaced by 2024/1221)",
    "DU/2002/1176": "UCHYLONA sprzedaż konsumencka (replaced by UPK 2014/827)",
    "DU/2000/271": "UCHYLONA ochrona praw konsumentów (replaced by UPK 2014/827)",
    "DU/1964/296": "KPC — 96% NIE consumer-specific (procedural law)",
}

# S6 source domain → reason (drop full source)
STRICT_DROP_S6_SOURCES: dict[str, str] = {
    "bankier.pl": "Generic finance journalism, NIE consumer rights (krytyka § Red Flag)",
    "money.pl": "Generic finance journalism, mała próbka",
    "infor.pl": "Generic legal/finance journalism (krytyka § Red Flag)",
    "gazetaprawna.pl": "Borderline media, mała próbka",
    "prawo.pl": "Borderline professional/media",
    "bezprawnik.pl": "Opinion site, garbage-in-garbage-out risk dla probe",
    "ing.pl": "Single-bank sample, większość to CSS scrape artifacts (NIE bank regulations)",
}

# Loose policy drops only ING (clearly garbage artifacts)
LOOSE_DROP_S6_SOURCES: dict[str, str] = {
    "ing.pl": "Single-bank sample, większość to CSS scrape artifacts",
}

# === Content keyword patterns ===

# CHF/franki dispute keywords — drop SN orzeczenia matching these
_CHF_KEYWORDS = re.compile(
    r"\b(?:CHF|frank(?:i|ów|owicze|owy)?|denomin(?:owan|acj)|"
    r"indeksowan(?:y|e|a|ej|ą|ego|ym|ymi)|"
    r"walut(?:y|cie|ie)?\s+obcej?|"
    r"hipotec(?:zny|znego|znej|znym))\b",
    re.IGNORECASE,
)

# Insurance-specific keywords (RF FAQ filter dla pure-insurance content)
_INSURANCE_KEYWORDS = re.compile(
    r"\b(?:ubezpieczeni(?:e|a|owy|owej|owym|owej)|"
    r"polis(?:a|y|ie|ę|ą)|"
    r"\bOC\b|\bAC\b|\bNNW\b|"
    r"fundusz(?:e|y|ach)?\s+(?:inwestycyjn|emerytaln)|"
    r"emerytur(?:a|y|alne)?|"
    r"ubezpieczyciel(?:e|i|owi|em)?|"
    r"składk(?:a|i|ę|ą)\s+ubezpieczeniow)\b",
    re.IGNORECASE,
)

# Consumer-credit/banking keywords (whitelist — keep RF chunks z tymi terminami)
_CONSUMER_CREDIT_KEYWORDS = re.compile(
    r"\b(?:kredyt(?:u|owi|em|y|ów)?\s+konsumencki|"
    r"pożyczk(?:a|i|ę|ą|owy)?\s+konsumenck|"
    r"RRSO|"
    r"reklamac(?:ja|ji|ję|ją)\s+(?:bankow|kart)|"
    r"rachunk(?:u|owi|em|i|ów)?\s+(?:bankow|płatnicz|oszczędno)|"
    r"kart(?:a|y|ę|ą)\s+(?:kredytow|płatnicz|debet))\b",
    re.IGNORECASE,
)

# === Filter helpers ===


def _is_chf_content(chunk: Chunk) -> bool:
    """Detect CHF/frankowicze content (title + first 2000 chars treści)."""
    sample = (chunk.title + " " + chunk.tresc[:2000]).lower()
    return bool(_CHF_KEYWORDS.search(sample))


def _is_pure_insurance_content(chunk: Chunk) -> bool:
    """Detect insurance-dominant content WITHOUT consumer-credit/banking signals.

    Heuristic: ≥3 insurance keyword hits AND zero consumer-credit/banking keyword hits.
    Used dla RF PDFs filter (drop pure-insurance, keep banking-consumer content).
    """
    sample = (chunk.title + " " + chunk.tresc[:3000]).lower()
    insurance_hits = len(_INSURANCE_KEYWORDS.findall(sample))
    credit_hits = len(_CONSUMER_CREDIT_KEYWORDS.findall(sample))
    return insurance_hits >= 3 and credit_hits == 0


def _is_sn_orzeczenie(chunk: Chunk) -> bool:
    """Detect SN orzeczenie (court_judgment z sn.pl source URL pattern)."""
    return chunk.source_type == SourceType.LEGAL_COURT_JUDGMENT and (
        "sn.pl" in chunk.source_url or "sn.pl" in chunk.source
    )


def _is_rf_pdf(chunk: Chunk) -> bool:
    """Detect Rzecznik Finansowy PDF chunk (E4 long-form documents from rf.gov.pl)."""
    return chunk.source_type == SourceType.LEGAL_DOCUMENT_PDF and "rf.gov.pl" in chunk.source


# === Per-policy filter functions ===


@dataclass
class FilterResult:
    """Result of chunk filtering: kept chunks + drop statistics + per-reason audit."""

    kept: list[Chunk]
    dropped_count: int
    drop_stats_by_reason: dict[str, int] = field(default_factory=dict)
    drop_stats_by_source: dict[str, int] = field(default_factory=dict)
    policy: FilterPolicy = "none"

    @property
    def kept_count(self) -> int:
        return len(self.kept)

    @property
    def total(self) -> int:
        return self.kept_count + self.dropped_count

    @property
    def drop_ratio(self) -> float:
        return self.dropped_count / max(self.total, 1)


def _decide_drop_strict(chunk: Chunk) -> tuple[bool, str | None]:
    """Strict policy — return (drop, reason_key) per Wariant B krytyka."""
    # ELI ustawa drops
    ustawa_id = chunk.metadata.get("ustawa_id")
    if ustawa_id in STRICT_DROP_ELI_USTAWY:
        return True, f"eli_{ustawa_id}"

    # S6 source drops (by Chunk.source domain)
    if chunk.source in STRICT_DROP_S6_SOURCES:
        return True, f"s6_{chunk.source}"

    # SN orzeczenie CHF content
    if _is_sn_orzeczenie(chunk) and _is_chf_content(chunk):
        return True, "sn_chf_content"

    # RF PDF pure-insurance content
    if _is_rf_pdf(chunk) and _is_pure_insurance_content(chunk):
        return True, "rf_pure_insurance"

    return False, None


def _decide_drop_loose(chunk: Chunk) -> tuple[bool, str | None]:
    """Loose policy — drop only uchylone ustawy + KPC + ING CSS artifacts.

    Keeps edge cases (RF PDFs, SN orzeczenia, Prawo bankowe, Usługi płatnicze,
    finance journalism) — used jako compromise jeśli `strict` okazuje się za
    agresywny dla probe training distribution.
    """
    ustawa_id = chunk.metadata.get("ustawa_id")
    if ustawa_id in LOOSE_DROP_ELI_USTAWY:
        return True, f"eli_{ustawa_id}"

    if chunk.source in LOOSE_DROP_S6_SOURCES:
        return True, f"s6_{chunk.source}"

    return False, None


def _decide_drop_none(_chunk: Chunk) -> tuple[bool, str | None]:
    return False, None


_POLICY_DECIDERS: dict[FilterPolicy, Callable[[Chunk], tuple[bool, str | None]]] = {
    "strict": _decide_drop_strict,
    "loose": _decide_drop_loose,
    "none": _decide_drop_none,
}


def filter_chunks(chunks: list[Chunk], policy: FilterPolicy = "strict") -> FilterResult:
    """Filter chunks per policy → FilterResult.

    Per-chunk decision via ``_decide_drop_*`` functions. Counts drops per reason
    (e.g. "eli_DU/1964/296" or "sn_chf_content") + per source (Chunk.source).
    """
    decider = _POLICY_DECIDERS[policy]
    kept: list[Chunk] = []
    reason_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()

    for chunk in chunks:
        drop, reason = decider(chunk)
        if drop:
            assert reason is not None
            reason_counts[reason] += 1
            source_counts[chunk.source] += 1
        else:
            kept.append(chunk)

    result = FilterResult(
        kept=kept,
        dropped_count=sum(reason_counts.values()),
        drop_stats_by_reason=dict(reason_counts.most_common()),
        drop_stats_by_source=dict(source_counts.most_common()),
        policy=policy,
    )

    logger.info(
        "[chunk_filter:%s] kept=%d dropped=%d (%.1f%%) z %d input chunks",
        policy,
        result.kept_count,
        result.dropped_count,
        100 * result.drop_ratio,
        result.total,
    )
    if result.dropped_count > 0:
        logger.info("[chunk_filter:%s] drops by reason:", policy)
        for reason, count in result.drop_stats_by_reason.items():
            logger.info("  %-50s %5d", reason, count)

    return result


# === Reasoning explainer (used dla DATASET_CARD audit) ===


def explain_drop_reason(reason_key: str, policy: FilterPolicy) -> str:
    """Human-readable explanation dla drop reason — used w DATASET_CARD."""
    drops_map = STRICT_DROP_ELI_USTAWY if policy == "strict" else LOOSE_DROP_ELI_USTAWY
    s6_map = STRICT_DROP_S6_SOURCES if policy == "strict" else LOOSE_DROP_S6_SOURCES

    if reason_key.startswith("eli_"):
        ustawa_id = reason_key[len("eli_") :]
        return drops_map.get(ustawa_id, f"ELI ustawa {ustawa_id} (unknown reason)")
    if reason_key.startswith("s6_"):
        source = reason_key[len("s6_") :]
        return s6_map.get(source, f"S6 source {source} (unknown reason)")
    if reason_key == "sn_chf_content":
        return "SN orzeczenie z CHF/franki content (domain shift risk — krytyka § Red Flag #3)"
    if reason_key == "rf_pure_insurance":
        return "RF PDF chunk z pure-insurance content (≥3 insurance kw, 0 banking-credit kw)"
    return f"Unknown drop reason: {reason_key}"


__all__ = [
    "FilterPolicy",
    "FilterResult",
    "STRICT_DROP_ELI_USTAWY",
    "STRICT_DROP_S6_SOURCES",
    "LOOSE_DROP_ELI_USTAWY",
    "LOOSE_DROP_S6_SOURCES",
    "Category",  # re-export dla downstream
    "explain_drop_reason",
    "filter_chunks",
]
