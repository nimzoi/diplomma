"""BGE-M3 embedder wrapper dla Polish CitationBench retrieval.

Wrapper wokół `BAAI/bge-m3` (multilingual dense+sparse+colbert; 1024-dim dense).
BGE-M3 wybrany jako frozen embedder per stack v3.1 (CLAUDE.md): obsługuje PL bez
fine-tuningu, native sparse (token-weighted) dla hybrid retrieval, i ma najwyższą
PL retrieval quality na MIRACL spośród general-purpose multilingual embedderów
(2024 BAAI report).

Polski tekst PRE-EMBEDDING wymaga NFC normalization (Pydantic ``LegalChunk``
już to robi, ale consumer questions z fora są raw — robimy NFC defensywnie).

Dwie ścieżki API:
1. ``sentence-transformers`` (default) — dense only, prosty interfejs, batchowanie.
2. ``FlagEmbedding.BGEM3FlagModel`` (opcjonalnie) — natywne sparse+dense+colbert,
   wymaga ``pip install FlagEmbedding`` (heavier deps; ładujemy lazy jeśli włączone).

Iter. 0 użyje wyłącznie dense ścieżki (sentence-transformers). Sparse hybrid
zostawiony jako stub do Iter. 1 (RQ5 cross-register może z niego skorzystać —
sparse lexical match często łapie terminologię prawną której dense miss).

Usage:
    from src.halu.embedder import BGEM3Embedder

    embedder = BGEM3Embedder(device="cuda")  # lub "cpu" jeśli brak GPU
    chunk_vecs = embedder.embed_chunks(["art. 27 ust. 1 Ustawy...", ...])
    query_vec = embedder.embed_query("Czy mogę zwrócić rower po 30 dniach?")
"""

from __future__ import annotations

import logging
import unicodedata
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:  # pragma: no cover — tylko dla type hints, unikamy heavy import
    from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "BAAI/bge-m3"
DEFAULT_VECTOR_SIZE = 1024  # BGE-M3 dense hidden dim
DEFAULT_BATCH_SIZE = 32
DEFAULT_MAX_LENGTH = 8192  # BGE-M3 context, ale ustawy konsumenckie ≤512 tokenów


def _normalize_polish(text: str) -> str:
    """NFC normalization + strip — defensywne dla polskich diakrytyków.

    BGE-M3 tokenizer (XLMRoberta) wymaga NFC dla poprawnej segmentacji
    polskich znaków diakrytycznych (ą, ć, ę, ł, ń, ó, ś, ź, ż). Bez NFC
    np. „ż" jako U+007A+U+0307 (z + dot above) zostanie potraktowane jako
    dwa różne tokeny vs U+017C (ż precomposed) — psuje retrieval.
    """
    return unicodedata.normalize("NFC", text).strip()


class BGEM3Embedder:
    """BGE-M3 dense embedder z opcjonalnym sparse output (Iter. 1+).

    Frozen weights (per stack decision) — NIE fine-tunujemy, więc nie ma stanu
    treningowego. Reranker (polish-reranker-roberta-v3) zostaje fine-tuned w
    cyklach retreningu (RQ1/H1).

    Args:
        model_name: HuggingFace model ID. Default ``BAAI/bge-m3``.
        device: ``"cuda"`` / ``"cpu"`` / ``"mps"``. Auto-detection przez
            sentence-transformers jeśli None.
        normalize_embeddings: L2-normalize output dla cosine similarity z
            Qdrant ``Distance.COSINE``. Default True.
        max_length: Truncation długości tokenów (BGE-M3 natywne 8192).
            Default 8192 — ustawy konsumenckie zazwyczaj ≤512 tokenów,
            consumer questions z context czasem przekraczają 2k.

    Attributes:
        model: lazy-loaded SentenceTransformer instance.
        vector_size: 1024 dla BGE-M3.
    """

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        device: str | None = None,
        normalize_embeddings: bool = True,
        max_length: int = DEFAULT_MAX_LENGTH,
    ) -> None:
        self.model_name = model_name
        self.device = device
        self.normalize_embeddings = normalize_embeddings
        self.max_length = max_length
        self.vector_size = DEFAULT_VECTOR_SIZE
        self._model: SentenceTransformer | None = None
        logger.info(
            "BGEM3Embedder configured: model=%s device=%s normalize=%s max_length=%d",
            model_name,
            device or "auto",
            normalize_embeddings,
            max_length,
        )

    @property
    def model(self) -> SentenceTransformer:
        """Lazy load — model download (~2.3 GB) tylko gdy pierwsze ``embed_*``."""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
            except ImportError as exc:  # pragma: no cover — env config issue
                raise ImportError(
                    "Brak `sentence-transformers`. Zainstaluj: `uv add sentence-transformers`"
                ) from exc
            logger.info("Ładowanie modelu %s (device=%s)...", self.model_name, self.device)
            self._model = SentenceTransformer(
                self.model_name,
                device=self.device,
            )
            # Truncation: ustawiamy max_seq_length zamiast manual truncation w call site
            self._model.max_seq_length = min(self.max_length, self._model.max_seq_length)
            logger.info(
                "Model załadowany: max_seq_length=%d, embedding_dim=%d",
                self._model.max_seq_length,
                self._model.get_sentence_embedding_dimension() or self.vector_size,
            )
        return self._model

    def embed_chunks(
        self,
        texts: list[str],
        batch_size: int = DEFAULT_BATCH_SIZE,
        show_progress: bool = False,
    ) -> np.ndarray:
        """Embed batch tekstów (chunks/answers/questions) → dense matrix.

        Args:
            texts: Lista tekstów do embeddingu. NFC normalization wewnątrz.
            batch_size: Rozmiar batcha dla GPU. Default 32 — bezpieczne dla
                ~12 GB VRAM (4090). Zmniejsz do 8/16 dla mniejszych GPU.
            show_progress: Pokaż tqdm progress bar (False default — clean logs
                w pipeline'ach Prefect).

        Returns:
            ``np.ndarray`` o kształcie ``(len(texts), 1024)`` typu ``float32``.
            Jeśli ``normalize_embeddings=True`` — wektory L2-normalized.

        Raises:
            ValueError: Jeśli ``texts`` jest puste.
            RuntimeError: Jeśli OOM (przekaż caller dla retry z mniejszym
                batch_size).
        """
        if not texts:
            raise ValueError("`texts` nie może być puste — embedder zwraca shape mismatch.")

        normalized = [_normalize_polish(t) for t in texts]
        logger.debug("Embedding %d tekstów, batch_size=%d", len(normalized), batch_size)

        try:
            embeddings = self.model.encode(
                normalized,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
                normalize_embeddings=self.normalize_embeddings,
            )
        except RuntimeError as exc:
            if "out of memory" in str(exc).lower():
                logger.error(
                    "CUDA OOM przy batch_size=%d. Spróbuj batch_size=%d.",
                    batch_size,
                    max(batch_size // 2, 1),
                )
            raise

        # sentence-transformers może zwrócić list[Tensor] / Tensor — ujednolicamy
        if not isinstance(embeddings, np.ndarray):
            embeddings = np.asarray(embeddings, dtype=np.float32)
        else:
            embeddings = embeddings.astype(np.float32, copy=False)

        assert embeddings.shape == (len(texts), self.vector_size), (
            f"Unexpected embedding shape: {embeddings.shape}, "
            f"expected ({len(texts)}, {self.vector_size})"
        )
        return embeddings

    def embed_query(self, text: str) -> np.ndarray:
        """Single-query embedding — wrapper dla retrieval interface.

        BGE-M3 NIE wymaga osobnego query prefiksu (jak np. E5: ``"query: ..."``).
        Symetryczny encoder — query i passage idą tym samym torem.

        Returns:
            1-D ``np.ndarray`` shape ``(1024,)`` float32.
        """
        return self.embed_chunks([text], batch_size=1, show_progress=False)[0]

    def embed_with_sparse(
        self,
        texts: list[str],
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> dict[str, Any]:
        """[STUB Iter. 1] Hybrid dense+sparse embedding via ``FlagEmbedding``.

        BGE-M3 natywnie produkuje sparse weights (token-level) dla hybrid
        retrieval. ``FlagEmbedding.BGEM3FlagModel.encode(return_sparse=True)``
        zwraca ``{"dense_vecs": ..., "lexical_weights": [{token_id: weight}]}``.

        Qdrant od 1.10 wspiera named sparse vectors w jednym kolekcji — RQ5
        cross-register może benefit z lexical matching na terminologii prawnej
        której dense embedder gubi (np. „rękojmia" vs „gwarancja").

        Returns:
            Dict ``{"dense": np.ndarray, "sparse": list[dict[int, float]]}``.

        Raises:
            NotImplementedError: Implementacja w Iter. 1 — wymaga decyzji
                dataset_builder o sparse storage w Qdrant payload.
        """
        raise NotImplementedError(
            "Sparse hybrid embedding — stub Iter. 1. "
            "Wymaga: (1) `uv add FlagEmbedding`, (2) Qdrant named sparse vectors "
            "schema, (3) decision RQ5 cross-register czy sparse pomaga."
        )
