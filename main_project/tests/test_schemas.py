"""Unit tests dla Pydantic schemas (LegalChunk, QAGoldPair, ConsumerQuestion, HaluPair)."""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from src.halu.schemas import (
    ConsumerQuestion,
    ConsumerSource,
    HaluPair,
    HaluType,
    LegalChunk,
    NLILabel,
    QAGoldPair,
)


class TestLegalChunk:
    def test_valid_chunk_loads(self, sample_legal_chunk_dict: dict) -> None:
        chunk = LegalChunk.model_validate(sample_legal_chunk_dict)
        assert chunk.chunk_id == "eli_DU_2014_827_art_27_ust_1"
        assert chunk.art == "27"
        assert chunk.ust == "1"
        assert chunk.pkt is None
        assert chunk.scrape_date == date(2026, 5, 16)

    def test_short_tresc_rejected(self, sample_legal_chunk_dict: dict) -> None:
        sample_legal_chunk_dict["tresc"] = "krótko"
        with pytest.raises(ValidationError, match="at least 10"):
            LegalChunk.model_validate(sample_legal_chunk_dict)

    def test_non_nfc_tresc_rejected(self, sample_legal_chunk_dict: dict) -> None:
        # Combining acute accent (NFD) zamiast precomposed (NFC) — should fail
        sample_legal_chunk_dict["tresc"] = "Konsument zawarĺ umowę na odleglosc"
        with pytest.raises(ValidationError, match="NFC"):
            LegalChunk.model_validate(sample_legal_chunk_dict)

    def test_frozen_immutable(self, sample_legal_chunk_dict: dict) -> None:
        chunk = LegalChunk.model_validate(sample_legal_chunk_dict)
        with pytest.raises(ValidationError):
            chunk.art = "999"  # type: ignore[misc]

    def test_optional_fields_default_none(self, sample_legal_chunk_dict: dict) -> None:
        del sample_legal_chunk_dict["paragraf"]
        del sample_legal_chunk_dict["pkt"]
        del sample_legal_chunk_dict["lit"]
        chunk = LegalChunk.model_validate(sample_legal_chunk_dict)
        assert chunk.paragraf is None
        assert chunk.pkt is None
        assert chunk.lit is None


class TestQAGoldPair:
    def test_valid_pair_loads(self, sample_uokik_qa_dict: dict) -> None:
        pair = QAGoldPair.model_validate(sample_uokik_qa_dict)
        assert pair.qa_id.startswith("uokik_")
        assert len(pair.cited_articles) == 1

    def test_empty_citations_allowed(self, sample_uokik_qa_dict: dict) -> None:
        sample_uokik_qa_dict["cited_articles"] = []
        pair = QAGoldPair.model_validate(sample_uokik_qa_dict)
        assert pair.cited_articles == []


class TestConsumerQuestion:
    def test_valid_question_loads(self, sample_consumer_question_dict: dict) -> None:
        q = ConsumerQuestion.model_validate(sample_consumer_question_dict)
        assert q.source == ConsumerSource.E_PRAWNIK
        assert "zwrot" in q.extracted_topics

    def test_invalid_source_rejected(self, sample_consumer_question_dict: dict) -> None:
        sample_consumer_question_dict["source"] = "invalid-source.com"
        with pytest.raises(ValidationError):
            ConsumerQuestion.model_validate(sample_consumer_question_dict)


class TestHaluPair:
    def test_valid_synthetic_pair_loads(self, sample_halu_pair_dict: dict) -> None:
        pair = HaluPair.model_validate(sample_halu_pair_dict)
        assert pair.is_hallucinated is True
        assert pair.halu_type == HaluType.FACTUAL_FABRICATION
        assert pair.nli_label == NLILabel.CONTRADICTED

    def test_non_hallucinated_no_halu_type(self, sample_halu_pair_dict: dict) -> None:
        sample_halu_pair_dict["is_hallucinated"] = False
        sample_halu_pair_dict["halu_type"] = None
        sample_halu_pair_dict["nli_label"] = NLILabel.ENTAILED
        pair = HaluPair.model_validate(sample_halu_pair_dict)
        assert pair.is_hallucinated is False
        assert pair.halu_type is None

    def test_all_5_halu_types_valid(self) -> None:
        types = [t.value for t in HaluType]
        assert set(types) == {
            "factual_fabrication",
            "entity_confusion",
            "temporal_drift",
            "negation_flip",
            "paragraph_mis_citation",
        }
