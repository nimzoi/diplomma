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

# Temporal drift: dni → inne dni, lata → inne lata, miesiące, godziny
_TEMPORAL_DAYS = {
    "14 dni": ["7 dni", "30 dni", "60 dni", "21 dni"],
    "30 dni": ["14 dni", "7 dni", "60 dni", "45 dni"],
    "7 dni": ["14 dni", "30 dni", "10 dni"],
    "60 dni": ["30 dni", "14 dni", "90 dni"],
    "90 dni": ["60 dni", "30 dni", "120 dni"],
    "21 dni": ["14 dni", "30 dni"],
    "2 lata": ["1 rok", "3 lata", "5 lat"],
    "5 lat": ["3 lata", "10 lat", "2 lata"],
    "10 lat": ["5 lat", "20 lat"],
    "rok": ["dwa lata", "pół roku", "trzy lata"],
    "miesiąc": ["dwa miesiące", "pół roku", "trzy miesiące"],
    "tydzień": ["dwa tygodnie", "trzy tygodnie", "miesiąc"],
    "24 godziny": ["48 godzin", "72 godziny", "12 godzin"],
    "48 godzin": ["24 godziny", "72 godziny"],
}

_TEMPORAL_YEARS = {
    "2014": ["2007", "2020", "2024", "2011"],
    "2007": ["2014", "2020", "2002"],
    "2002": ["2014", "2020", "2007"],
    "2011": ["2014", "2017", "2020"],
    "2016": ["2014", "2020", "2024"],
    "2024": ["2014", "2020", "2018"],
    "2020": ["2018", "2014", "2022"],
}

# Entity confusion: zamiana podmiotów (consumer/business + B2C/B2B + sprzedawca/kupujący)
_ENTITY_SWAPS = {
    "konsument": "przedsiębiorca",
    "konsumenta": "przedsiębiorcy",
    "konsumentowi": "przedsiębiorcy",
    "konsumentem": "przedsiębiorcą",
    "konsumenci": "przedsiębiorcy",
    "przedsiębiorca": "konsument",
    "przedsiębiorcy": "konsumenta",
    "przedsiębiorcę": "konsumenta",
    "sprzedawca": "kupujący",
    "sprzedawcy": "kupującego",
    "kupujący": "sprzedawca",
    "kupujące": "sprzedające",
    "nabywca": "zbywca",
    "kredytodawca": "kredytobiorca",
    "kredytobiorca": "kredytodawca",
    "ubezpieczyciel": "ubezpieczony",
    "ubezpieczony": "ubezpieczyciel",
    "operator": "abonent",
    "abonent": "operator",
    "B2C": "B2B",
    "B2B": "B2C",
    "powód": "pozwany",
    "pozwany": "powód",
}

# Negation flip: assert ↔ negate (PL legal patterns expanded)
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
    (r"\bjest uprawniony\b", "nie jest uprawniony"),
    (r"\bnie jest uprawniony\b", "jest uprawniony"),
    (r"\bmusi\b", "nie musi"),
    (r"\bnie musi\b", "musi"),
    (r"\bdopuszcza się\b", "nie dopuszcza się"),
    (r"\bnie dopuszcza się\b", "dopuszcza się"),
    (r"\bzakazuje\b", "dozwala"),
    (r"\bdozwala\b", "zakazuje"),
    (r"\bjest ważn", "jest nieważn"),
    (r"\bjest nieważn", "jest ważn"),
    (r"\bjest dozwolon", "jest niedozwolon"),
    (r"\bjest niedozwolon", "jest dozwolon"),
    (r"\bjest skuteczn", "jest bezskuteczn"),
    (r"\bjest bezskuteczn", "jest skuteczn"),
    (r"\bzgodnie z\b", "wbrew"),
    (r"\bwbrew\b", "zgodnie z"),
]

# Factual fabrication: fikcyjny fakt — kwoty, terminy, warunki, opłaty
_FAKE_FACTS = [
    "Termin ten może zostać przedłużony o kolejne 21 dni za zgodą obu stron.",
    "Konsument musi przedstawić oryginał paragonu, w przeciwnym razie reklamacja jest nieskuteczna.",
    "Powyższe zasady stosuje się wyłącznie do umów o wartości powyżej 1000 zł.",
    "Wymagana jest dodatkowa opłata manipulacyjna 25 zł od każdego zwrotu.",
    "Przepisy te nie mają zastosowania w przypadku zakupów dokonanych w wyprzedażach świątecznych.",
    "Konsument zobowiązany jest do zwrotu kosztów dostawy w wysokości 49,99 zł.",
    "Sprzedawca pobiera prowizję 3% od wartości zwracanego towaru.",
    "Przepis ten obowiązuje wyłącznie konsumentów posiadających status rezydenta UE.",
    "Reklamacja musi zostać złożona w formie listu poleconego z potwierdzeniem odbioru.",
    "Termin liczony jest od następnego dnia roboczego po doręczeniu towaru.",
    "Powyższe zasady stosuje się jedynie do produktów elektronicznych klasy A.",
    "Konsument zobowiązany jest do uiszczenia kaucji w wysokości 10% ceny.",
    "Przepis ten został doprecyzowany w rozporządzeniu Ministra Sprawiedliwości z 2023 r.",
    "Sprzedawca ma prawo odmówić przyjęcia reklamacji bez podania przyczyny.",
    "Klauzula ta jest nieważna w przypadku transakcji o wartości poniżej 200 zł.",
]

# Paragraph mis-citation: same ustawa ale wrong art./ust. (UPK + KC + UE common)
_MISCITATION_MUTATIONS = [
    ("art. 12", "art. 13"),
    ("art. 13", "art. 14"),
    ("art. 14", "art. 15"),
    ("art. 27", "art. 28"),
    ("art. 28", "art. 29"),
    ("art. 29", "art. 30"),
    ("art. 30", "art. 32"),
    ("art. 32", "art. 33"),
    ("art. 38", "art. 39"),
    ("art. 39", "art. 40"),
    ("art. 535", "art. 540"),
    ("art. 540", "art. 545"),
    ("art. 556", "art. 558"),
    ("art. 558", "art. 561"),
    ("art. 568", "art. 570"),
    ("art. 22^1", "art. 23"),
    ("art. 6 ust. 1", "art. 6 ust. 2"),
    ("art. 7 ust. 1", "art. 7 ust. 2"),
    ("ust. 1", "ust. 2"),
    ("ust. 2", "ust. 3"),
    ("ust. 3", "ust. 1"),
    ("pkt 1", "pkt 3"),
    ("pkt 2", "pkt 1"),
    ("pkt 3", "pkt 5"),
    ("Dyrektywy 2011/83/UE", "Dyrektywy 93/13/EWG"),
    ("Dyrektywy 93/13/EWG", "Dyrektywy 2005/29/WE"),
    ("Dz.U. 2014 poz. 827", "Dz.U. 2014 poz. 915"),
    ("Dz.U. 1964/93", "Dz.U. 2014/827"),
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


def _try_all_types_balanced(
    text: str, rng: random.Random, max_per_type: int = 2
) -> list[tuple[HaluType, str]]:
    """Try ALL 5 halu types per text — return successful (type, mutated) pairs.

    Per Magda 2026-05-16 critique: previous version cycled types modulo with
    fallback to FACTUAL_FABRICATION → 3/5 types had 0 examples.
    Balanced approach: try each type up to ``max_per_type`` times.
    """
    results: list[tuple[HaluType, str]] = []
    for halu_type in HaluType:
        for _ in range(max_per_type):
            mutated = inject_hallucination(text, halu_type, rng)
            if mutated:
                results.append((halu_type, mutated))
    return results


def generate_halu_pairs_from_qa(
    qa_pairs: list[dict[str, Any]],
    seed: int = 42,
    n_halu_per_pair: int = 10,
) -> list[HaluPair]:
    """Generate synthetic HaluPair records z UOKiK Q&A.

    Per source QA pair: 1 negative sample (entailed) + try ALL 5 halu types
    (max ``n_halu_per_pair`` total positive samples). Per Magda 2026-05-16:
    balanced ratio across 5 types, NIE cycle modulo z fallback.
    """
    rng = random.Random(seed)
    halu_pairs: list[HaluPair] = []

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

        # Positive samples: try all 5 types, take up to n_halu_per_pair
        attempts = _try_all_types_balanced(original_answer, rng, max_per_type=2)
        rng.shuffle(attempts)
        for i, (halu_type, mutated) in enumerate(attempts[:n_halu_per_pair]):
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
        "Generated %d HaluPair records z %d UOKiK gold pairs (ratio 1:up_to_%d neg:pos)",
        len(halu_pairs),
        len(qa_pairs),
        n_halu_per_pair,
    )
    return halu_pairs


def generate_halu_pairs_from_legal_chunks(
    chunks: list[dict[str, Any]],
    seed: int = 42,
    n_chunks_sample: int = 1500,
    n_halu_per_chunk: int = 5,
) -> list[HaluPair]:
    """Generate HaluPair records z legal_statute / legal_ue_directive / legal_court_judgment chunks.

    Strategy: per legal chunk
    - 1 negative: claim = chunk text → ENTAILED
    - try ALL 5 halu types → up to ``n_halu_per_chunk`` positive (CONTRADICTED)

    Sample ``n_chunks_sample`` chunks (random z legal sources). Target: 5-10k pairs total
    when combined z UOKiK QA generation. Per Magda critique: balanced 5 types coverage.
    """
    rng = random.Random(seed)
    legal_chunks = [
        c
        for c in chunks
        if c.get("source_type")
        in {
            "legal_statute",
            "legal_ue_directive",
            "legal_court_judgment",
            "legal_uokik_decision",
            "legal_tsue_judgment",
        }
        and len(c.get("tresc", "")) >= 80  # meaningful claims only
    ]
    if not legal_chunks:
        logger.warning("No legal chunks for halu generation")
        return []

    sampled = rng.sample(legal_chunks, min(n_chunks_sample, len(legal_chunks)))
    logger.info("Sampled %d legal chunks z %d total", len(sampled), len(legal_chunks))

    halu_pairs: list[HaluPair] = []
    for chunk in sampled:
        chunk_id = chunk["chunk_id"]
        original_text = chunk["tresc"]
        # Use citation_string lub source as query proxy
        query = chunk.get("title", "Treść aktu prawnego")[:200]

        # Negative
        halu_pairs.append(
            HaluPair(
                pair_id=f"halu_legal_{chunk_id}_neg",
                source_qa_id=chunk_id,
                query=query,
                claim=original_text[:1500],
                evidence_chunks=[chunk_id],
                is_hallucinated=False,
                halu_type=None,
                nli_label=NLILabel.ENTAILED,
                generation_method="legal_chunk_original",
                metadata={
                    "source_type": chunk.get("source_type"),
                    "source": chunk.get("source"),
                    "citation_string": chunk.get("citation_string"),
                },
            )
        )

        # Try all 5 types, balanced
        attempts = _try_all_types_balanced(original_text, rng, max_per_type=1)
        rng.shuffle(attempts)
        for i, (halu_type, mutated) in enumerate(attempts[:n_halu_per_chunk]):
            halu_pairs.append(
                HaluPair(
                    pair_id=f"halu_legal_{chunk_id}_pos_{halu_type.value}_{i}",
                    source_qa_id=chunk_id,
                    query=query,
                    claim=mutated[:1500],
                    evidence_chunks=[chunk_id],
                    is_hallucinated=True,
                    halu_type=halu_type,
                    nli_label=NLILabel.CONTRADICTED,
                    generation_method="legal_chunk_template_injection_v2",
                    metadata={
                        "source_type": chunk.get("source_type"),
                        "source": chunk.get("source"),
                        "citation_string": chunk.get("citation_string"),
                        "original_text": original_text[:500],
                        "mutation_seed": seed,
                    },
                )
            )

    logger.info(
        "Generated %d HaluPair records z %d legal chunks (avg %.1f per chunk)",
        len(halu_pairs),
        len(sampled),
        len(halu_pairs) / max(len(sampled), 1),
    )
    return halu_pairs


__all__ = [
    "generate_halu_pairs_from_qa",
    "generate_halu_pairs_from_legal_chunks",
    "inject_hallucination",
]
