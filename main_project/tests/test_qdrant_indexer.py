"""Test stubs dla ``src.halu.qdrant_indexer``.

Unit testy dla deterministic helpers + skip dla integration (live Qdrant).
"""

from __future__ import annotations

import uuid
from datetime import date

import numpy as np
import pytest
from src.halu.qdrant_indexer import (
    DEFAULT_COLLECTION,
    DEFAULT_VECTOR_SIZE,
    QdrantIndexer,
    _chunk_id_to_point_id,
    _chunk_to_payload,
)
from src.halu.schemas import LegalChunk


class TestChunkIdToPointId:
    """Unit testy deterministic UUID5 mapping."""

    def test_deterministic(self) -> None:
        chunk_id = "eli_DU_2014_827_art_27_ust_1"
        uuid1 = _chunk_id_to_point_id(chunk_id)
        uuid2 = _chunk_id_to_point_id(chunk_id)
        assert uuid1 == uuid2

    def test_valid_uuid_format(self) -> None:
        result = _chunk_id_to_point_id("test_chunk")
        parsed = uuid.UUID(result)
        assert parsed.version == 5

    def test_different_chunks_different_uuids(self) -> None:
        u1 = _chunk_id_to_point_id("chunk_a")
        u2 = _chunk_id_to_point_id("chunk_b")
        assert u1 != u2


class TestChunkToPayload:
    """Konwersja LegalChunk → Qdrant payload dict."""

    @pytest.fixture
    def sample_chunk(self) -> LegalChunk:
        return LegalChunk(
            chunk_id="eli_test_001",
            ustawa_id="DU/2014/827",
            ustawa_title="Ustawa o prawach konsumenta",
            ustawa_data_uchwalenia=date(2014, 5, 30),
            art="27",
            paragraf=None,
            ust="1",
            pkt=None,
            lit=None,
            tresc="Konsument może odstąpić w terminie 14 dni bez podawania przyczyny.",
            citation_string="art. 27 ust. 1 Ustawy o prawach konsumenta",
            scrape_date=date(2026, 5, 16),
            source_url="https://api.sejm.gov.pl/eli/acts/DU/2014/827/text.html",
            metadata={"data_uchwalenia": "2014-05-30"},
        )

    def test_required_fields_present(self, sample_chunk: LegalChunk) -> None:
        payload = _chunk_to_payload(sample_chunk)
        for key in (
            "chunk_id",
            "ustawa_id",
            "ustawa_title",
            "ustawa_data_uchwalenia",
            "art",
            "tresc",
            "citation_string",
            "source_url",
            "scrape_date",
        ):
            assert key in payload, f"Missing required key: {key}"

    def test_dates_serialized_iso(self, sample_chunk: LegalChunk) -> None:
        payload = _chunk_to_payload(sample_chunk)
        assert payload["scrape_date"] == "2026-05-16"
        assert payload["ustawa_data_uchwalenia"] == "2014-05-30"

    def test_optional_none_fields_skipped(self, sample_chunk: LegalChunk) -> None:
        payload = _chunk_to_payload(sample_chunk)
        # ust set → present; paragraf/pkt/lit None → skipped
        assert "ust" in payload
        assert "paragraf" not in payload
        assert "pkt" not in payload
        assert "lit" not in payload


class TestQdrantIndexerConfig:
    """Konfiguracja bez połączenia (lazy client)."""

    def test_default_config(self) -> None:
        indexer = QdrantIndexer()
        assert indexer.host == "localhost"
        assert indexer.port == 6333
        assert indexer.collection == DEFAULT_COLLECTION
        assert indexer._client is None  # lazy

    def test_index_chunks_dimension_mismatch_raises(self) -> None:
        indexer = QdrantIndexer()
        chunks: list[LegalChunk] = []  # empty matches with no embeddings
        embs = np.zeros((3, DEFAULT_VECTOR_SIZE), dtype=np.float32)
        with pytest.raises(ValueError, match="Mismatch"):
            indexer.index_chunks(chunks, embs)

    def test_hybrid_stub_raises(self) -> None:
        indexer = QdrantIndexer()
        with pytest.raises(NotImplementedError, match=r"Iter\. 1"):
            indexer.hybrid_search(
                query_embedding=np.zeros(DEFAULT_VECTOR_SIZE, dtype=np.float32),
                sparse_features={1: 0.5},
            )


_SKIP_REASON_QDRANT = (
    "Integration test - wymaga live Qdrant (docker run -p 6333:6333 qdrant/qdrant)"
)


@pytest.mark.integration
@pytest.mark.skip(reason=_SKIP_REASON_QDRANT)
class TestQdrantIndexerIntegration:
    """Live Qdrant tests — odpalić po `docker run qdrant/qdrant`."""

    @pytest.fixture
    def indexer(self) -> QdrantIndexer:
        ix = QdrantIndexer(collection="test_citationbench")
        ix.create_collection(recreate=True)
        yield ix
        ix.client.delete_collection("test_citationbench")

    def test_health_check_live(self, indexer: QdrantIndexer) -> None:
        assert indexer.health_check() is True

    def test_index_and_search_roundtrip(self, indexer: QdrantIndexer) -> None:
        chunk = LegalChunk(
            chunk_id="eli_test_001",
            ustawa_id="DU/2014/827",
            ustawa_title="Ustawa o prawach konsumenta",
            ustawa_data_uchwalenia=date(2014, 5, 30),
            art="27",
            paragraf=None,
            ust="1",
            pkt=None,
            lit=None,
            tresc="Konsument może odstąpić w terminie 14 dni.",
            citation_string="art. 27 ust. 1 Ustawy o prawach konsumenta",
            scrape_date=date(2026, 5, 16),
            source_url="https://example.com",
            metadata={},
        )
        # Fake embedding (random but normalized)
        rng = np.random.default_rng(seed=42)
        emb = rng.standard_normal(DEFAULT_VECTOR_SIZE).astype(np.float32)
        emb /= np.linalg.norm(emb)

        indexer.index_chunks([chunk], emb[np.newaxis, :])
        assert indexer.count() == 1

        hits = indexer.search(emb, top_k=1)
        assert len(hits) == 1
        assert hits[0].payload["chunk_id"] == "eli_test_001"
        assert hits[0].score > 0.99  # same vector → score ~1
