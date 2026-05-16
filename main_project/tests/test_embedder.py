"""Test stubs dla ``src.halu.embedder``.

Lightweight unit testy (no model load) + skip dla integration (live model).
Integration testy w Iter. 0.1 — wymagają `uv add sentence-transformers` +
download ~2.3 GB BGE-M3 weights.
"""

from __future__ import annotations

import numpy as np
import pytest
from src.halu.embedder import (
    DEFAULT_BATCH_SIZE,
    DEFAULT_MODEL,
    DEFAULT_VECTOR_SIZE,
    BGEM3Embedder,
    _normalize_polish,
)


class TestNormalizePolish:
    """Unit testy NFC normalization — nie wymagają modelu."""

    def test_already_nfc_passthrough(self) -> None:
        text = "Ustawa o prawach konsumenta z dnia 30 maja 2014 r."
        assert _normalize_polish(text) == text

    def test_strip_whitespace(self) -> None:
        assert _normalize_polish("  art. 27  ") == "art. 27"

    def test_decomposed_diacritic_normalized(self) -> None:
        # ż jako z + combining dot above (U+007A U+0307) → ż precomposed (U+017C)
        decomposed = "żwrot"
        normalized = _normalize_polish(decomposed)
        assert normalized == "żwrot"
        assert len(normalized) < len(decomposed)


class TestBGEM3EmbedderConfig:
    """Konfiguracja embedder bez ładowania modelu (lazy load)."""

    def test_default_config(self) -> None:
        embedder = BGEM3Embedder()
        assert embedder.model_name == DEFAULT_MODEL
        assert embedder.vector_size == DEFAULT_VECTOR_SIZE
        assert embedder.normalize_embeddings is True
        assert embedder._model is None  # lazy

    def test_custom_device(self) -> None:
        embedder = BGEM3Embedder(device="cpu")
        assert embedder.device == "cpu"

    def test_empty_texts_raises(self) -> None:
        embedder = BGEM3Embedder()
        with pytest.raises(ValueError, match="puste"):
            embedder.embed_chunks([])

    def test_sparse_stub_raises(self) -> None:
        embedder = BGEM3Embedder()
        with pytest.raises(NotImplementedError, match=r"Iter\. 1"):
            embedder.embed_with_sparse(["test"])


_SKIP_REASON_EMB = "Integration test - wymaga sentence-transformers + BGE-M3 download (~2.3 GB)"


@pytest.mark.integration
@pytest.mark.skip(reason=_SKIP_REASON_EMB)
class TestBGEM3EmbedderIntegration:
    """Live model tests — odpalić ręcznie po `uv add sentence-transformers`."""

    @pytest.fixture(scope="class")
    def embedder(self) -> BGEM3Embedder:
        return BGEM3Embedder(device="cpu")  # CI-safe

    def test_embed_single_chunk(self, embedder: BGEM3Embedder) -> None:
        vec = embedder.embed_query("art. 27 ust. 1 Ustawy o prawach konsumenta")
        assert vec.shape == (DEFAULT_VECTOR_SIZE,)
        assert vec.dtype == np.float32
        # L2-normalized → norm ≈ 1
        np.testing.assert_allclose(np.linalg.norm(vec), 1.0, atol=1e-5)

    def test_embed_batch(self, embedder: BGEM3Embedder) -> None:
        texts = [
            "art. 27 ust. 1 Ustawy o prawach konsumenta",
            "Konsument może odstąpić od umowy w terminie 14 dni",
            "Kodeks cywilny — rękojmia za wady",
        ]
        embs = embedder.embed_chunks(texts, batch_size=DEFAULT_BATCH_SIZE)
        assert embs.shape == (3, DEFAULT_VECTOR_SIZE)
        # Similar PL legal texts powinny mieć cosine > 0.3
        sim_01 = float(np.dot(embs[0], embs[1]))
        assert sim_01 > 0.3, f"Expected related texts to be similar, got {sim_01}"

    def test_polish_diacritics_preserved(self, embedder: BGEM3Embedder) -> None:
        nfc = embedder.embed_query("żółć łódź ąęć")
        # Sanity: vector nie jest zerowy
        assert np.linalg.norm(nfc) > 0
