"""Synthetic hallucination injection — 5 typów per HaluType enum.

Generuje ``HaluPair`` records z UOKiK gold pairs (QAGoldPair) przez controlled
mutation odpowiedzi. Każdy typ injection wprowadza konkretną klasę błędu:

1. **FACTUAL_FABRICATION** — wstrzyka fikcyjny fakt (np. wymyślona kwota, fikcyjny artykuł)
2. **ENTITY_CONFUSION** — zamienia podmiot (konsument↔przedsiębiorca, B2C↔B2B)
3. **TEMPORAL_DRIFT** — zmienia datę/termin (14 dni → 30 dni, 2014 → 2022)
4. **NEGATION_FLIP** — odwraca negation (może → nie może, ma prawo → nie ma prawa)
5. **PARAGRAPH_MIS_CITATION** — zmienia citation na inny art./ust. tej samej ustawy

Output: ``HaluPair`` list z `is_hallucinated=True` + `halu_type` + `nli_label=contradicted`.
Plus negative samples (`is_hallucinated=False` + `nli_label=entailed`) dla balanced training.

**Approach:** template-based programmatic injection. NIE używamy LLM bo:
- Deterministic + reproducible (seed control)
- Brak external API dependencies (offline)
- Tańsze niż LLM-generated (Bielik 11B inference cost)
- Verifiable (każda mutation traceable do source claim)

LLM-based augmentation jest dla Iter. 1+ (Bielik few-shot generation per spec).
"""

from __future__ import annotations

import logging
import random
import re
from typing import Any

from src.halu.schemas import HaluPair, HaluType, NLILabel

logger = logging.getLogger(__name__)

# === Mutation tables (deterministic templates) ===

# Temporal drift: dni → inne dni, lata → inne lata
_TEMPORAL_DAYS = {
    "14 dni": ["7 dni", "30 dni", "60 dni"],
    "30 dni": ["14 dni", "7 dni", "60 dni"],
    "7 dni": ["14 dni", "30 dni"],
    "60 dni": ["30 dni", "14 dni"],
    "2 lata": ["1 rok", "3 lata", "5 lat"],
    "rok": ["dwa lata", "pół roku", "trzy lata"],
}

_TEMPORAL_YEARS = {
    "2014": ["2007", "2020", "2024"],
    "2007": ["2014", "2020"],
    "2002": ["2014", "2020"],
}

# Entity confusion: zamiana podmiotów
_ENTITY_SWAPS = {
    "konsument": "przedsiębiorca",
    "konsumenta": "przedsiębiorcy",
    "konsumentowi": "przedsiębiorcy",
    "konsumentem": "przedsiębiorcą",
    "przedsiębiorca": "konsument",
    "przedsiębiorcy": "konsumenta",
    "sprzedawca": "kupujący",
    "kupujący": "sprzedawca",
    "B2C": "B2B",
    "B2B": "B2C",
}

# Negation flip: assert ↔ negate
_NEGATION_PATTERNS = [
    (r"\bmoże\b", "nie może"),
    (r"\bnie może\b", "może"),
    (r"\bma prawo\b", "nie ma prawa"),
    (r"\bnie ma prawa\b", "ma prawo"),
    (r"\bjest zobowiązany\b", "nie jest zobowiązany"),
    (r"\bnie jest zobowiązany\b", "jest zobowiązany"),
    (r"\bprzysługuje\b", "nie przysługuje"),
    (r"\bnie przysługuje\b", "przysługuje"),
    (r"\bobowiązuje\b", "nie obowiązuje"),
    (r"\bnie obowiązuje\b", "obowiązuje"),
]

# Factual fabrication: dodaj fikcyjny "fakt" do answer
_FAKE_FACTS = [
    "Termin ten może zostać przedłużony o kolejne 21 dni za zgodą obu stron.",
    "Konsument musi przedstawić oryginał paragonu, w przeciwnym razie reklamacja jest nieskuteczna.",
    "Powyższe zasady stosuje się wyłącznie do umów o wartości powyżej 1000 zł.",
    "Wymagana jest dodatkowa opłata manipulacyjna 25 zł od każdego zwrotu.",
    "Przepisy te nie mają zastosowania w przypadku zakupów dokonanych w wyprzedażach świątecznych.",
]

# Paragraph mis-citation: same ustawa ale wrong art./ust.
_MISCITATION_MUTATIONS = [
    ("art. 27", "art. 28"),
    ("art. 28", "art. 27"),
    ("art. 30", "art. 32"),
    ("art. 535", "art. 540"),
    ("art. 556", "art. 558"),
    ("ust. 1", "ust. 2"),
    ("ust. 2", "ust. 1"),
    ("pkt 1", "pkt 3"),
    ("pkt 2", "pkt 1"),
]


def _mutate_temporal_drift(text: str, rng: random.Random) -> str | None:
    """Wstrzyka temporal drift jeśli text zawiera datę/termin."""
    for original, alternatives in _TEMPORAL_DAYS.items():
        if original in text:
            replacement = rng.choice(alternatives)
            return text.replace(original, replacement, 1)
    for original, alternatives in _TEMPORAL_YEARS.items():
        if original in text:
            replacement = rng.choice(alternatives)
            return text.replace(original, replacement, 1)
    return None


def _mutate_entity_confusion(text: str, rng: random.Random) -> str | None:
    """Zamień podmiot (konsument↔przedsiębiorca)."""
    candidates = [
        (original, replacement)
        for original, replacement in _ENTITY_SWAPS.items()
        if original in text.lower()
    ]
    if not candidates:
        return None
    original, replacement = rng.choice(candidates)
    # Case-preserving replacement
    pattern = re.compile(re.escape(original), re.IGNORECASE)
    return pattern.sub(replacement, text, count=1)


def _mutate_negation_flip(text: str, rng: random.Random) -> str | None:
    """Odwróć negation jeśli pattern występuje."""
    candidates = [(pat, repl) for pat, repl in _NEGATION_PATTERNS if re.search(pat, text)]
    if not candidates:
        return None
    pattern, replacement = rng.choice(candidates)
    return re.sub(pattern, replacement, text, count=1)


def _mutate_factual_fabrication(text: str, rng: random.Random) -> str:
    """Dodaj fikcyjny fakt jako extra zdanie (zawsze success)."""
    fake = rng.choice(_FAKE_FACTS)
    return text + " " + fake


def _mutate_paragraph_mis_citation(text: str, rng: random.Random) -> str | None:
    """Zmień citation na inny art./ust."""
    candidates = [
        (original, replacement)
        for original, replacement in _MISCITATION_MUTATIONS
        if original in text
    ]
    if not candidates:
        return None
    original, replacement = rng.choice(candidates)
    return text.replace(original, replacement, 1)


def inject_hallucination(
    answer: str,
    halu_type: HaluType,
    rng: random.Random,
) -> str | None:
    """Inject hallucination of specified type. Returns None jeśli mutation niemożliwa."""
    mutators = {
        HaluType.TEMPORAL_DRIFT: _mutate_temporal_drift,
        HaluType.ENTITY_CONFUSION: _mutate_entity_confusion,
        HaluType.NEGATION_FLIP: _mutate_negation_flip,
        HaluType.FACTUAL_FABRICATION: _mutate_factual_fabrication,
        HaluType.PARAGRAPH_MIS_CITATION: _mutate_paragraph_mis_citation,
    }
    mutator = mutators[halu_type]
    result = mutator(answer, rng)
    return result if result and result != answer else None


def generate_halu_pairs_from_qa(
    qa_pairs: list[dict[str, Any]],
    seed: int = 42,
    n_halu_per_pair: int = 3,
) -> list[HaluPair]:
    """Generate synthetic HaluPair records z UOKiK Q&A.

    Per source QA pair:
    - 1 negative sample (is_hallucinated=False, entailed)
    - N halu samples (is_hallucinated=True, contradicted) — różne typy

    Total: ``len(qa_pairs) * (1 + n_halu_per_pair)`` pairs.
    """
    rng = random.Random(seed)
    halu_pairs: list[HaluPair] = []
    halu_types = list(HaluType)

    for qa in qa_pairs:
        qa_id = qa["qa_id"]
        question = qa["question"]
        original_answer = qa["answer"]

        # Negative sample: original answer entailed
        halu_pairs.append(
            HaluPair(
                pair_id=f"halu_{qa_id}_neg",
                source_qa_id=qa_id,
                query=question,
                claim=original_answer,
                evidence_chunks=qa.get("cited_articles", []),
                is_hallucinated=False,
                halu_type=None,
                nli_label=NLILabel.ENTAILED,
                generation_method="manual_uokik_original",
                metadata={"source": "uokik_qa", "category": qa.get("category")},
            )
        )

        # Positive samples: N halu injections per pair
        for i in range(n_halu_per_pair):
            halu_type = halu_types[i % len(halu_types)]
            mutated = inject_hallucination(original_answer, halu_type, rng)
            if mutated is None:
                # Fallback: factual_fabrication zawsze sukces
                mutated = inject_hallucination(original_answer, HaluType.FACTUAL_FABRICATION, rng)
                halu_type = HaluType.FACTUAL_FABRICATION

            halu_pairs.append(
                HaluPair(
                    pair_id=f"halu_{qa_id}_pos_{halu_type.value}_{i}",
                    source_qa_id=qa_id,
                    query=question,
                    claim=mutated,
                    evidence_chunks=qa.get("cited_articles", []),
                    is_hallucinated=True,
                    halu_type=halu_type,
                    nli_label=NLILabel.CONTRADICTED,
                    generation_method="programmatic_template_injection_v1",
                    metadata={
                        "source": "uokik_qa",
                        "category": qa.get("category"),
                        "original_answer": original_answer,
                        "mutation_seed": seed,
                    },
                )
            )

    logger.info(
        "Generated %d HaluPair records z %d UOKiK gold pairs (ratio 1:%d neg:pos)",
        len(halu_pairs),
        len(qa_pairs),
        n_halu_per_pair,
    )
    return halu_pairs


__all__ = [
    "generate_halu_pairs_from_qa",
    "inject_hallucination",
]
