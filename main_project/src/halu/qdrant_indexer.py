"""Qdrant client + bulk indexer + search interface dla Polish CitationBench.

Single collection model: wszystkie ``LegalChunk`` zindeksowane jako points z
payload zawierającym citation_string + ustawa_id + art (+§/ust/pkt/lit jeśli są).
Payload index na ``ustawa_id`` dla per-statute filtering (np. „tylko Kodeks
cywilny"), na ``art`` dla deep-link odpowiedzi.

Decyzje schema:
- ``distance=COSINE`` — embeddingi L2-normalized z BGE-M3, cosine ≡ dot product.
- ``vector_size=1024`` — BGE-M3 dense hidden dim.
- ``point_id``: deterministyczny stable hash z ``chunk_id`` (UUID5) — re-indexing
  idempotentny, audit-friendly. Alternatywą był string ID ale Qdrant prefers
  int/UUID dla performance.
- ``payload``: pełny ``LegalChunk`` (bez ``tresc`` zduplikowanego — ``tresc``
  w payload bo retrieval API musi return czysty tekst BEZ ponownego rebuilda).

Bulk upsert chunks po ~256 — Qdrant gRPC handluje większe ale 256 to safe
default dla local Docker (1-node). Production: tune per cluster.

Hybrid search (RQ5 Iter. 1+) — Qdrant 1.10+ wspiera named sparse vectors;
``hybrid_search`` zostawiony jako stub.

Usage:
    from qdrant_client import QdrantClient
    from src.halu.qdrant_indexer import QdrantIndexer

    indexer = QdrantIndexer(host="localhost", port=6333)
    indexer.create_collection()
    indexer.index_chunks(chunks, embeddings)
    hits = indexer.search(query_embedding, top_k=10)
"""

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:  # pragma: no cover
    from qdrant_client import QdrantClient
    from qdrant_client.models import ScoredPoint

    from src.halu.schemas import LegalChunk

logger = logging.getLogger(__name__)

DEFAULT_COLLECTION = "polish_citationbench"
DEFAULT_VECTOR_SIZE = 1024
DEFAULT_BATCH_SIZE = 256  # punkty na upsert request
DEFAULT_NAMESPACE = uuid.UUID("6f0e1f10-1234-5678-9abc-000000000001")  # stable namespace UUID5


def _chunk_id_to_point_id(chunk_id: str) -> str:
    """Deterministyczny UUID5 z chunk_id — idempotent re-indexing.

    Qdrant point_id musi być int lub UUID. UUID5(namespace, chunk_id) gwarantuje
    że ta sama treść po reindexowaniu nadpisze (upsert) zamiast tworzyć
    duplikaty. Zwracamy string — qdrant-client akceptuje string-UUID.
    """
    return str(uuid.uuid5(DEFAULT_NAMESPACE, chunk_id))


def _chunk_to_payload(chunk: LegalChunk) -> dict[str, Any]:
    """Wyciąga payload z LegalChunk — wszystko poza wektorem.

    Konwertuje ``date`` → ISO string (Qdrant payload JSON-serializable).
    Pomija ``metadata`` jeśli puste (oszczędność miejsca).
    """
    payload: dict[str, Any] = {
        "chunk_id": chunk.chunk_id,
        "ustawa_id": chunk.ustawa_id,
        "ustawa_title": chunk.ustawa_title,
        "ustawa_data_uchwalenia": chunk.ustawa_data_uchwalenia.isoformat(),
        "art": chunk.art,
        "tresc": chunk.tresc,
        "citation_string": chunk.citation_string,
        "source_url": chunk.source_url,
        "scrape_date": chunk.scrape_date.isoformat(),
    }
    for opt_field in ("paragraf", "ust", "pkt", "lit"):
        val = getattr(chunk, opt_field)
        if val is not None:
            payload[opt_field] = val
    if chunk.metadata:
        payload["metadata"] = chunk.metadata
    return payload


class QdrantIndexer:
    """Wrapper Qdrant client dla bulk indexing + retrieval.

    Args:
        host: Qdrant host. Default ``localhost``.
        port: Qdrant REST port. Default 6333 (gRPC: 6334).
        collection: Nazwa kolekcji. Default ``polish_citationbench``.
        prefer_grpc: Użyj gRPC (szybsze bulk upsert) zamiast REST. Default True.
        api_key: Qdrant Cloud API key (None dla local Docker).
        timeout: Request timeout w sekundach. Default 60.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection: str = DEFAULT_COLLECTION,
        prefer_grpc: bool = True,
        api_key: str | None = None,
        timeout: int = 60,
    ) -> None:
        self.host = host
        self.port = port
        self.collection = collection
        self.prefer_grpc = prefer_grpc
        self.api_key = api_key
        self.timeout = timeout
        self._client: QdrantClient | None = None
        logger.info(
            "QdrantIndexer configured: host=%s port=%d collection=%s grpc=%s",
            host,
            port,
            collection,
            prefer_grpc,
        )

    @property
    def client(self) -> QdrantClient:
        """Lazy connect — nie próbujemy się łączyć aż faktycznie potrzebujemy."""
        if self._client is None:
            try:
                from qdrant_client import QdrantClient
            except ImportError as exc:  # pragma: no cover
                raise ImportError(
                    "Brak `qdrant-client`. Zainstaluj: `uv add qdrant-client`"
                ) from exc
            self._client = QdrantClient(
                host=self.host,
                port=self.port,
                grpc_port=6334 if self.prefer_grpc else None,
                prefer_grpc=self.prefer_grpc,
                api_key=self.api_key,
                timeout=self.timeout,
            )
            logger.info("Qdrant client connected: %s:%d", self.host, self.port)
        return self._client

    def health_check(self) -> bool:
        """Sprawdź czy Qdrant odpowiada. Zwraca True/False (nie raises)."""
        try:
            self.client.get_collections()
        except Exception as exc:
            logger.error("Qdrant health check failed: %s", exc)
            return False
        return True

    def create_collection(
        self,
        vector_size: int = DEFAULT_VECTOR_SIZE,
        recreate: bool = False,
    ) -> None:
        """Utwórz kolekcję jeśli nie istnieje (lub recreate=True wymusza drop+create).

        Tworzy payload index na ``ustawa_id`` (keyword) dla filtered search:
        ``Filter(must=[FieldCondition(key="ustawa_id", match=MatchValue(value="DU/2014/827"))])``.

        Args:
            vector_size: Dim dense wektorów. Default 1024 (BGE-M3).
            recreate: Drop + recreate jeśli True. Default False (no-op jeśli istnieje).
        """
        from qdrant_client.models import Distance, PayloadSchemaType, VectorParams

        existing = {c.name for c in self.client.get_collections().collections}

        if self.collection in existing:
            if recreate:
                logger.warning("Recreate=True — kasuję kolekcję %s", self.collection)
                self.client.delete_collection(self.collection)
            else:
                logger.info("Kolekcja %s już istnieje — skip create", self.collection)
                return

        self.client.create_collection(
            collection_name=self.collection,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        logger.info(
            "Utworzona kolekcja %s (size=%d, distance=COSINE)",
            self.collection,
            vector_size,
        )

        # Payload indices — przyspiesza filtered search
        for field in ("ustawa_id", "art"):
            self.client.create_payload_index(
                collection_name=self.collection,
                field_name=field,
                field_schema=PayloadSchemaType.KEYWORD,
            )
        logger.info("Payload indices utworzone na: ustawa_id, art")

    def index_chunks(
        self,
        chunks: list[LegalChunk],
        embeddings: np.ndarray,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> int:
        """Bulk upsert chunks + embeddings → Qdrant.

        Idempotentne: re-running z tymi samymi ``chunk_id`` nadpisuje (UUID5).

        Args:
            chunks: Lista ``LegalChunk`` po Pydantic validation.
            embeddings: ``np.ndarray`` shape ``(len(chunks), vector_size)``.
            batch_size: Punkty na request. Default 256.

        Returns:
            Liczba upsertowanych punktów.

        Raises:
            ValueError: Jeśli len(chunks) != embeddings.shape[0].
        """
        if len(chunks) != embeddings.shape[0]:
            raise ValueError(f"Mismatch: {len(chunks)} chunks vs {embeddings.shape[0]} embeddings")

        from qdrant_client.models import PointStruct

        if embeddings.shape[1] != DEFAULT_VECTOR_SIZE:
            logger.warning(
                "Embedding dim %d != default %d — upewnij się że kolekcja matched",
                embeddings.shape[1],
                DEFAULT_VECTOR_SIZE,
            )

        total = 0
        for batch_start in range(0, len(chunks), batch_size):
            batch_end = min(batch_start + batch_size, len(chunks))
            batch_chunks = chunks[batch_start:batch_end]
            batch_vecs = embeddings[batch_start:batch_end]

            points = [
                PointStruct(
                    id=_chunk_id_to_point_id(c.chunk_id),
                    vector=vec.tolist(),
                    payload=_chunk_to_payload(c),
                )
                for c, vec in zip(batch_chunks, batch_vecs, strict=True)
            ]
            self.client.upsert(collection_name=self.collection, points=points, wait=True)
            total += len(points)
            logger.debug(
                "Upsertowano %d/%d punktow (batch %d-%d)",
                total,
                len(chunks),
                batch_start,
                batch_end,
            )

        logger.info("Indexing complete: %d punktów do kolekcji %s", total, self.collection)
        return total

    def search(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        ustawa_filter: str | None = None,
        score_threshold: float | None = None,
    ) -> list[ScoredPoint]:
        """Dense vector search w kolekcji.

        Args:
            query_embedding: ``np.ndarray`` shape ``(vector_size,)`` lub 2D z 1
                rzędem. Auto-flatten dla 2D.
            top_k: Liczba zwracanych hits. Default 10.
            ustawa_filter: Jeśli ustawione (np. ``"DU/2014/827"``) — filtruje
                hits tylko z tej ustawy. Wymaga payload index utworzonego w
                ``create_collection``.
            score_threshold: Min cosine score (0-1). Default None.

        Returns:
            Lista ``ScoredPoint`` z polami ``id``, ``score``, ``payload``,
            ``vector`` (None jeśli ``with_vectors=False``).
        """
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        if query_embedding.ndim == 2:
            assert query_embedding.shape[0] == 1
            query_embedding = query_embedding.flatten()

        query_filter: Filter | None = None
        if ustawa_filter:
            query_filter = Filter(
                must=[FieldCondition(key="ustawa_id", match=MatchValue(value=ustawa_filter))]
            )

        hits = self.client.search(
            collection_name=self.collection,
            query_vector=query_embedding.tolist(),
            limit=top_k,
            query_filter=query_filter,
            score_threshold=score_threshold,
            with_payload=True,
            with_vectors=False,
        )
        logger.debug("Search zwrócił %d hits (top_k=%d)", len(hits), top_k)
        return hits

    def count(self) -> int:
        """Zwraca liczbę punktów w kolekcji."""
        return self.client.count(collection_name=self.collection, exact=True).count

    def hybrid_search(
        self,
        query_embedding: np.ndarray,
        sparse_features: dict[int, float],
        top_k: int = 10,
    ) -> list[ScoredPoint]:
        """[STUB Iter. 1] Hybrid dense+sparse search via Qdrant named vectors.

        Wymaga: (1) ``BGEM3Embedder.embed_with_sparse`` zaimplementowany,
        (2) kolekcja recreated z ``VectorsConfig`` zawierającym dense + sparse,
        (3) reciprocal rank fusion lub linear combination scoringu.

        Returns:
            Lista hits z fused score.

        Raises:
            NotImplementedError: Iter. 1 deliverable.
        """
        raise NotImplementedError(
            "Hybrid search — stub Iter. 1. "
            "Wymaga: BGEM3Embedder.embed_with_sparse + collection z dual vectors + "
            "decision RRF vs linear combination scoring."
        )


def chunk_id_to_point_id(chunk_id: str) -> str:
    """Public helper — re-export dla testów (deterministyczny UUID5)."""
    return _chunk_id_to_point_id(chunk_id)
