"""Pydantic schemas dla Polish CitationBench dataset.

**RAW schemas (per source, multiple strata):**

1. ``LegalChunk`` — atomic chunk z ELI ustawy konsumenckiej (art./§/ust./pkt./lit.)
2. ``QAGoldPair`` — expert Q&A z UOKiK z explicit citations
3. ``ConsumerQuestion`` — real polish consumer question z fora/Reddit
4. ``EncyclopedicChunk`` — Wikipedia/NGO/gov.pl encyclopedic content
5. ``HaluPair`` — synthetic (claim, evidence, label) z hallucination injection
6. ``EvalSample`` — combined eval format z labelami dla probe + verifier validation

**PROCESSED schema (unified — option b per Magda 2026-05-16):**

7. ``Chunk`` — unified processed chunk dla HF dataset publication. Wszystkie raw
   sources normalizowane do tej struktury w preprocessing pipeline. Source-specific
   dodatki w ``metadata`` dict.

Wszystkie schemas mają strict validation (Pydantic v2 ``ConfigDict(strict=True)``)
oraz JSONL serialization helpers w ``dataset_builder.py``.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class HaluType(StrEnum):
    """Pięć typów halucynacji per metodologia v3.2 (R3 § 3.5)."""

    FACTUAL_FABRICATION = "factual_fabrication"
    ENTITY_CONFUSION = "entity_confusion"
    TEMPORAL_DRIFT = "temporal_drift"
    NEGATION_FLIP = "negation_flip"
    PARAGRAPH_MIS_CITATION = "paragraph_mis_citation"


class NLILabel(StrEnum):
    """3-klasowa etykieta NLI dla (claim, evidence) verification."""

    ENTAILED = "entailed"
    CONTRADICTED = "contradicted"
    NEUTRAL = "neutral"


class ConsumerSource(StrEnum):
    """Źródła consumer questions."""

    E_PRAWNIK = "e-prawnik.pl"
    FORUMPRAWNE = "forumprawne.org"
    EPORADY24 = "eporady24.pl"
    REDDIT_POLSKA = "reddit.com/r/Polska"
    REDDIT_POLSKA_WPZ = "reddit.com/r/Polska_wpz"


class ExtendedSource(StrEnum):
    """Źródła dodane w Iter. 0 extended scrape (2026-05-16).

    Mix Q&A pairs, encyclopedic chunks, articles, news. Każdy ma własną
    licencję — patrz ``EncyclopedicChunk.license`` field.
    """

    WIKIPEDIA_PL = "pl.wikipedia.org"  # CC BY-SA 4.0
    FEDERACJA_KONSUMENTOW = "federacja-konsumentow.org.pl"  # fair-use NGO
    RZECZNIK_FINANSOWY = "rf.gov.pl"  # urzędowe Art. 4 PrAut
    UOKIK_NEWS = "uokik.gov.pl/aktualnosci"  # urzędowe Art. 4 PrAut
    GOV_PL_CONSUMER = "gov.pl"  # urzędowe Art. 4 PrAut


class SourceType(StrEnum):
    """Source type klasyfikacja dla unified processed ``Chunk`` (option b).

    Odzwierciedla strukturę raw stratum. Stosowane jako primary discriminator
    w preprocessing pipeline + HF dataset filtering.
    """

    LEGAL_STATUTE = "legal_statute"  # ELI ustawy konsumenckie (S0 + S1)
    LEGAL_UE_DIRECTIVE = "legal_ue_directive"  # UE dyrektywy konsumenckie (S3)
    LEGAL_TSUE_JUDGMENT = "legal_tsue_judgment"  # TSUE orzeczenia (S3)
    LEGAL_COURT_JUDGMENT = "legal_court_judgment"  # orzeczenia.ms.gov.pl, SN (E4 + S2)
    LEGAL_UOKIK_DECISION = "legal_uokik_decision"  # decyzje Prezesa UOKiK (S2)
    LEGAL_DOCUMENT_PDF = "legal_document_pdf"  # E4 poradniki/raporty PDF (UOKiK, RF, FK)
    ENCYCLOPEDIC = "encyclopedic"  # E1 (Wikipedia, NGO, gov.pl, UOKiK news)
    QA_GOLD = "qa_gold"  # UOKiK Q&A FAQ portal
    QA_RAW = "qa_raw"  # consumer questions z forum/Reddit


class Category(StrEnum):
    """Multi-label categorical tag per chunk dla stratified eval split + filtering.

    Jeden chunk może mieć N kategorii (np. UPK art. 28 = CONSUMER_CORE + CONSUMER_CONTRACT).
    ``FINANCE_ADJACENT`` flag per Magda decision 2b: RF FAQ keep, oznacz osobnym tagiem
    żeby świadomie raportować bias w R3 (60% finance / 30% banking / 10% pure consumer).
    """

    CONSUMER_CORE = "consumer_core"  # UPK 2014/827, prawa konsumenta podstawowe
    CONSUMER_CONTRACT = "consumer_contract"  # umowy, rękojmia, gwarancja
    CONSUMER_CREDIT = "consumer_credit"  # kredyt konsumencki
    CONSUMER_DIGITAL = "consumer_digital"  # e-commerce, treści cyfrowe
    CONSUMER_TELECOM = "consumer_telecom"  # prawo telekomunikacyjne
    CONSUMER_RETURN_REFUND = "consumer_return_refund"  # zwroty, odstąpienie 14 dni
    CONSUMER_UNFAIR_PRACTICES = "consumer_unfair_practices"  # nieuczciwe praktyki, klauzule
    CONSUMER_DISPUTE_RESOLUTION = "consumer_dispute_resolution"  # ADR, mediacja
    FINANCE_ADJACENT = "finance_adjacent"  # RF FAQ ubezpieczenia + banki (świadomy bias)
    EU_DIRECTIVE = "eu_directive"  # UE dyrektywy
    TSUE_JUDGMENT = "tsue_judgment"  # TSUE orzecznictwo
    COURT_PRECEDENT = "court_precedent"  # SN + sądy powszechne orzeczenia
    REGULATORY_DECISION = "regulatory_decision"  # UOKiK decyzje
    OTHER = "other"


class Chunk(BaseModel):
    """Unified processed chunk dla HF dataset publication (option b per Magda 2026-05-16).

    Wszystkie raw sources (LegalChunk + EncyclopedicChunk + QAGoldPair + ConsumerQuestion +
    UE Dyrektywy + TSUE orzeczenia + UOKiK decyzje + court judgments + PDF documents)
    normalizowane do tej struktury w preprocessing pipeline. Source-specific dodatki
    w ``metadata`` dict (np. UE celex_id, TSUE case_name, ELI ustawa_id+art+ust+pkt).

    Multi-label ``categories`` dla stratified eval split. ``cited_articles`` jako
    list canonical citation strings ekstrahowanych z tresc via regex.
    """

    model_config = ConfigDict(strict=True, frozen=True)

    chunk_id: str = Field(..., description="Globally unique, np. 'eli_DU_2014_827_art_27_ust_1'")
    source_type: SourceType
    source: str = Field(..., description="Domain, np. 'isap.sejm.gov.pl'")
    source_url: str

    title: str = Field(..., min_length=2, description="Document title or article title")
    tresc: str = Field(..., min_length=10, description="Main content, NFC normalized")

    # Optional canonical citation (for legal sources — None dla encyclopedic/QA)
    citation_string: str | None = Field(
        None, description="Canonical citation (e.g. 'art. 27 ust. 1 UPK z 2014/827')"
    )
    # Extracted citations from tresc (cross-references to other acts)
    cited_articles: list[str] = Field(
        default_factory=list,
        description="Citation strings extracted via regex z tresc, np. ['art. 535 KC']",
    )

    # Categorization
    categories: list[Category] = Field(default_factory=list, description="Multi-label")
    language: str = Field("pl", description="ISO 639-1 code, default 'pl'")
    license: str = Field(..., description="np. 'CC BY-SA 4.0' / 'urzędowe Art. 4 PrAut'")

    scrape_date: date
    process_date: date = Field(..., description="Kiedy przetworzony do unified format")

    # Source-specific extras (e.g. {ustawa_id, art, ust, pkt} dla ELI; {celex_id} dla UE)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("tresc")
    @classmethod
    def validate_nfc(cls, v: str) -> str:
        import unicodedata

        if v != unicodedata.normalize("NFC", v):
            raise ValueError("tresc must be NFC-normalized")
        return v


class EncyclopedicChunk(BaseModel):
    """Atomic chunk z encyclopedycznego / porady source (Wikipedia, NGO, gov.pl).

    Bardziej elastyczny niż ``LegalChunk`` — nie wymaga citation hierarchy
    (art./§/ust.). Używany dla:
    - Wikipedia articles (per H2 section)
    - Federacja Konsumentów porady (per article)
    - UOKiK aktualności (per news article)
    - Gov.pl konsumencki content (per page)

    ``cited_articles`` w metadata (jeśli extracted via regex z body text).
    """

    model_config = ConfigDict(strict=True, frozen=True)

    chunk_id: str = Field(..., description="np. 'wiki_pl_rekojmia_lead'")
    source: str = Field(..., description="domain, np. 'pl.wikipedia.org'")
    source_url: str
    title: str = Field(..., min_length=2)
    section: str | None = Field(None, description="H2 section title lub kategoria")
    tresc: str = Field(..., min_length=50, description="Body text po NFC normalizacji")
    license: str = Field(..., description="np. 'CC BY-SA 4.0 (Wikipedia)'")
    scrape_date: date
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("tresc")
    @classmethod
    def validate_nfc(cls, v: str) -> str:
        import unicodedata

        if v != unicodedata.normalize("NFC", v):
            raise ValueError("tresc must be NFC-normalized")
        return v


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


class UEDyrektywa(BaseModel):
    """Atomic chunk z dyrektywy UE (EUR-Lex scrape, polska wersja językowa).

    Hierarchia: dyrektywa → preambula_motyw lub artykul → ust → lit/pkt.
    Wersja PL sciagnieta z EUR-Lex (formaty HTML/TXT). License: (c) UE,
    free reuse zgodnie z decyzja 2011/833/UE — wymaga attribution.

    Citation_string deterministycznie generowany dla halu detection.
    Mapowanie do polskiej ustawy implementacyjnej via ``polska_implementacja``
    w metadata (cross-language citation chains).
    """

    model_config = ConfigDict(strict=True, frozen=True)

    chunk_id: str = Field(..., description="np. 'celex_32011L0083_art_6_ust_1_lit_a'")
    celex_id: str = Field(
        ...,
        description="CELEX numer, np. '32011L0083' (3=secondary law, 2011=year, L=directive, 0083=num)",
    )
    direktywa_id: str = Field(..., description="Krotki ID, np. '2011/83/UE' lub '93/13/EWG'")
    direktywa_title_pl: str = Field(..., min_length=10)
    art: str | None = Field(None, description="Numer artykulu — None dla motywow preambuly")
    ust: str | None = Field(None, description="Numer ustepu, opcjonalny")
    pkt: str | None = Field(None, description="Numer punktu, opcjonalny")
    lit: str | None = Field(None, description="Litera (a, b, c...), opcjonalna")
    motyw: str | None = Field(None, description="Numer motywu preambuly (alternatywne do `art`)")
    tresc: str = Field(..., min_length=10, description="Tresc chunk po NFC normalization")
    citation_string: str = Field(
        ...,
        description="Deterministyczny: 'art. N ust. U lit. L Dyrektywy YYYY/NN/UE'",
    )
    license: str = Field(
        default="(c) UE — free reuse per Decyzja 2011/833/UE (attribution required)",
        description="EUR-Lex content license string",
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


class TSUEOrzeczenie(BaseModel):
    """Orzeczenie Trybunalu Sprawiedliwosci UE (Court of Justice EU) — polska wersja.

    Kazde orzeczenie ma case_id (np. 'C-260/18') i CELEX numer (np. '62018CJ0260').
    Zawiera streszczenie, tezy kluczowe (sentencja/operative part), i pelna tresc PL.

    License: (c) UE, free reuse zgodnie z 2011/833/UE — wymaga attribution.

    Defense argument: TSUE wykladnia dyrektyw konsumenckich jest wiazaca dla
    polskich sadow (acquis communautaire) -> pelen consumer law stack wymaga
    cytowania orzeczen (np. C-260/18 Dziubak dla CHF klauzul).
    """

    model_config = ConfigDict(strict=True, frozen=True)

    case_id: str = Field(..., description="Numer sprawy, np. 'C-260/18' lub 'C-377/14'")
    celex_id: str = Field(
        ...,
        description="CELEX, np. '62018CJ0260' (6=case-law, 2018=rok skierowania, CJ=Court Judgment, 0260=num)",
    )
    case_name: str = Field(
        ...,
        description="Nazwa sprawy, np. 'Dziubak v Raiffeisen Bank International'",
    )
    data_orzeczenia: date | None = Field(
        None, description="Data wydania wyroku, jesli ekstrachowalna"
    )
    sklad: str | None = Field(
        None,
        description="Izba i sedziowie, np. 'trzecia izba: A. Prechal (sprawozdawca), ...'",
    )
    streszczenie: str | None = Field(
        None,
        description="Pre-orzeczenie 'descriptors' (key legal terms) z headera dokumentu",
    )
    tezy_kluczowe: list[str] = Field(
        default_factory=list,
        description="Operative part / sentencja — kluczowe rozstrzygniecia (po 'Trybunal orzeka:')",
    )
    pelna_tresc: str = Field(
        ..., min_length=100, description="Pelen tekst orzeczenia PL (NFC normalized)"
    )
    citation_string: str = Field(
        ...,
        description="np. 'Wyrok TSUE z dnia 3 pazdziernika 2019 r. w sprawie C-260/18 Dziubak'",
    )
    license: str = Field(
        default="(c) UE — free reuse per Decyzja 2011/833/UE (attribution required)",
        description="EUR-Lex content license",
    )
    scrape_date: date
    source_url: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("pelna_tresc")
    @classmethod
    def validate_nfc(cls, v: str) -> str:
        import unicodedata

        if v != unicodedata.normalize("NFC", v):
            raise ValueError("pelna_tresc must be NFC-normalized")
        return v
