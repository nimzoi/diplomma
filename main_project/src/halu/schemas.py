"""Pydantic schemas dla Polish CitationBench dataset.

Trzy strata source data + combined eval format:

1. ``LegalChunk`` — atomic chunk z ELI ustawy konsumenckiej (art./§/ust./pkt./lit.)
2. ``QAGoldPair`` — expert Q&A z UOKiK z explicit citations
3. ``ConsumerQuestion`` — real polish consumer question z fora/Reddit
4. ``HaluPair`` — synthetic (claim, evidence, label) z hallucination injection
5. ``EvalSample`` — combined eval format z labelami dla probe + verifier validation

Wszystkie schemas mają strict validation (Pydantic v2 ``ConfigDict(strict=True)``)
oraz JSONL serialization helpers w ``dataset_builder.py``.
"""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HaluType(str, Enum):
    """Pięć typów halucynacji per metodologia v3.2 (R3 § 3.5)."""

    FACTUAL_FABRICATION = "factual_fabrication"
    ENTITY_CONFUSION = "entity_confusion"
    TEMPORAL_DRIFT = "temporal_drift"
    NEGATION_FLIP = "negation_flip"
    PARAGRAPH_MIS_CITATION = "paragraph_mis_citation"


class NLILabel(str, Enum):
    """3-klasowa etykieta NLI dla (claim, evidence) verification."""

    ENTAILED = "entailed"
    CONTRADICTED = "contradicted"
    NEUTRAL = "neutral"


class ConsumerSource(str, Enum):
    """Źródła consumer questions."""

    E_PRAWNIK = "e-prawnik.pl"
    FORUMPRAWNE = "forumprawne.org"
    EPORADY24 = "eporady24.pl"
    REDDIT_POLSKA = "reddit.com/r/Polska"
    REDDIT_POLSKA_WPZ = "reddit.com/r/Polska_wpz"


class LegalChunk(BaseModel):
    """Atomic chunk z polskiej ustawy (ISAP/ELI scrape).

    Struktura citation hierarchiczna: ustawa → art → § → ust → pkt → lit.
    Każdy poziom opcjonalny poza ``art`` (atomicity boundary).

    Citation_string deterministycznie generowany dla halu detection.
    """

    model_config = ConfigDict(strict=True, frozen=True)

    chunk_id: str = Field(..., description="Unikatowy ID, np. 'eli_DU_2014_827_art_27_ust_1'")
    ustawa_id: str = Field(..., description="ELI ID, np. 'DU/2014/827'")
    ustawa_title: str
    ustawa_data_uchwalenia: date
    art: str = Field(..., description="Numer artykułu, np. '27' lub '22^1' (superscript notation)")
    paragraf: str | None = Field(None, description="Numer paragrafu (§), opcjonalny")
    ust: str | None = Field(None, description="Numer ustępu, opcjonalny")
    pkt: str | None = Field(None, description="Numer punktu, opcjonalny")
    lit: str | None = Field(None, description="Litera, opcjonalna")
    tresc: str = Field(..., min_length=10, description="Treść chunk po NFC normalization")
    citation_string: str = Field(
        ..., description="Deterministyczny: 'art. N [§ P] [ust. U] ... ustawy ... (Dz.U. ...)'"
    )
    scrape_date: date
    source_url: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("tresc")
    @classmethod
    def validate_nfc(cls, v: str) -> str:
        import unicodedata

        if v != unicodedata.normalize("NFC", v):
            raise ValueError("tresc must be NFC-normalized")
        return v


class QAGoldPair(BaseModel):
    """Gold standard Q&A pair z UOKiK z explicit citations.

    UOKiK FAQ portal `prawakonsumenta.uokik.gov.pl/pytania-i-odpowiedzi/`
    udostępnia ekspertskie answer + explicit `Podstawa prawna:` z cytacjami.
    """

    model_config = ConfigDict(strict=True, frozen=True)

    qa_id: str = Field(..., description="Unikatowy, np. 'uokik_odstapienie_001'")
    question: str = Field(..., min_length=5)
    answer: str = Field(..., min_length=10)
    cited_articles: list[str] = Field(
        default_factory=list,
        description="Lista citation strings, np. ['art. 27 ust. 1 Ustawy o prawach konsumenta']",
    )
    category: str = Field(..., description="UOKiK kategoria, np. 'Odstapienie od umowy'")
    source_url: str
    scrape_date: date


class ConsumerQuestion(BaseModel):
    """Real consumer question z polskich fora prawnych / Reddit.

    Tylko question (NIE odpowiedź) — odpowiedzi z fora są noisy random users,
    NIE ground truth. Używamy questions jako query distribution dla pipeline.
    """

    model_config = ConfigDict(strict=True, frozen=True)

    question_id: str = Field(..., description="Unikatowy, np. 'eprawnik_001'")
    question: str = Field(..., min_length=10)
    context: str | None = Field(None, description="Opcjonalny dodatkowy kontekst od użytkownika")
    source: ConsumerSource
    source_url: str
    category: str | None = None
    thread_responses_count: int | None = Field(None, ge=0)
    extracted_topics: list[str] = Field(
        default_factory=list,
        description="Multi-label topics, np. ['zwrot', 'umowa-na-odleglosc']",
    )
    scrape_date: date


class HaluPair(BaseModel):
    """Synthetic (claim, evidence, label) z controlled hallucination injection.

    Generowane programatycznie w Iter. 1 z UOKiK gold pairs + halu injection
    script. 5 typów halu per ``HaluType`` enum.
    """

    model_config = ConfigDict(strict=True, frozen=True)

    pair_id: str = Field(..., description="np. 'halu_synth_001'")
    source_qa_id: str | None = Field(
        None, description="Reference do origin UOKiK pair jeśli derived"
    )
    query: str = Field(..., min_length=5)
    claim: str = Field(..., description="Claim w odpowiedzi, do verification")
    evidence_chunks: list[str] = Field(
        default_factory=list, description="ID-y chunks ELI (LegalChunk.chunk_id) jako evidence"
    )
    is_hallucinated: bool = Field(
        ..., description="Ground truth label: True jeśli claim jest halucynacją"
    )
    halu_type: HaluType | None = Field(
        None, description="Jeśli is_hallucinated=True, typ halu z 5 kategorii"
    )
    nli_label: NLILabel = Field(
        ..., description="(claim, top evidence) → entailed/contradicted/neutral"
    )
    generation_method: str = Field(..., description="np. 'bielik_11b_few_shot' lub 'manual'")
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvalSample(BaseModel):
    """Combined eval sample: query → retrieved evidence → answer → per-claim labels.

    Final format dla benchmark + probe + verifier eval. Może agregować HaluPair
    + manual labels by autorka (50-100 par diversity coverage).
    """

    model_config = ConfigDict(strict=True, frozen=True)

    sample_id: str
    query: str = Field(..., min_length=5)
    retrieved_evidence: list[str] = Field(
        ..., description="Top-k chunk IDs (LegalChunk.chunk_id) z retriever"
    )
    generated_answer: str = Field(..., description="Bielik 11B v3 generation output")
    claims: list[dict[str, Any]] = Field(
        default_factory=list,
        description="Per claim: {claim_text, supporting_chunk_id, nli_label, halu_score, manual_label}",
    )
    overall_halu_label: bool = Field(..., description="Aggregate: czy answer zawiera ≥1 halu")
    annotation_source: str = Field(
        ..., description="'uokik_gold' / 'manual_magda' / 'synthetic_injected'"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
