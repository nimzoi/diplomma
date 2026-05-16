"""High-level citation-grounded retriever — kompozycja Embedder + Indexer.

Public API dla Iter. 1 RAG pipeline (Bielik 11B v3 generator + citation
attribution). Zwraca chunks WRAZ z ``citation_string`` — pipeline downstream
może bezpośrednio użyć tekstu cytacji w promptcie generatora (Bielik) i w
verifier check ((claim, evidence) NLI).

Decyzje API:
- ``retrieve()`` zwraca lekkie ``RetrievedChunk`` dataclasses (NIE Pydantic —
  to read-only output, brak walidacji potrzebnej i unikamy ``model_validate``
  overhead w hot path).
- ``retrieve_with_evidence()`` zwraca dict gotowy do JSON serialization dla
  Langfuse trace logging (R5 observability stack).
- ``ustawa_filter`` propagowany z indexer (np. „tylko KC" dla focused query).

Stub dla cross-register (RQ5):
- ``retrieve_cross_register()`` — przyszły hook gdy dodamy pairing ChPL↔Ulotka
  (na razie tylko legal corpus, nie ma pairów).

Usage:
    from src.halu.embedder import BGEM3Embedder
    from src.halu.qdrant_indexer import QdrantIndexer
    from src.halu.retriever import CitationGroundedRetriever

    embedder = BGEM3Embedder(device="cuda")
    indexer = QdrantIndexer()
    retriever = CitationGroundedRetriever(embedder, indexer)

    hits = retriever.retrieve("Czy mogę zwrócić rower po 30 dniach?", top_k=5)
    for h in hits:
        print(f"[{h.score:.3f}] {h.citation_string}")
        print(f"  {h.tresc[:200]}...")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from src.halu.embedder import BGEM3Embedder
    from src.halu.qdrant_indexer import QdrantIndexer

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class RetrievedChunk:
    """Lekki output ``CitationGroundedRetriever.retrieve()``.

    Frozen dla bezpieczeństwa (downstream nie mutuje). Slots dla memory
    efficiency przy dużych top_k batch.
    """

    chunk_id: str
    citation_string: str
    tresc: str
    ustawa_id: str
    art: str
    score: float
    payload: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_qdrant_hit(cls, hit: Any) -> RetrievedChunk:
        """Konwersja z qdrant ``ScoredPoint`` → ``RetrievedChunk``.

        Defensywnie sprawdza payload — czasami pole może brakować (np. stary
        index z innym schema). Brak ``citation_string`` → log warning, użyj
        fallback ``"unknown citation"``.
        """
        payload = hit.payload or {}
        return cls(
            chunk_id=payload.get("chunk_id", str(hit.id)),
            citation_string=payload.get("citation_string", "unknown citation"),
            tresc=payload.get("tresc", ""),
            ustawa_id=payload.get("ustawa_id", ""),
            art=payload.get("art", ""),
            score=float(hit.score),
            payload=payload,
        )


class CitationGroundedRetriever:
    """Kompozycja Embedder + Indexer = retrieval API z citation attribution.

    Args:
        embedder: ``BGEM3Embedder`` instance.
        indexer: ``QdrantIndexer`` instance z istniejącą kolekcją.
    """

    def __init__(self, embedder: BGEM3Embedder, indexer: QdrantIndexer) -> None:
        self.embedder = embedder
        self.indexer = indexer
        logger.info(
            "CitationGroundedRetriever ready: embedder=%s collection=%s",
            embedder.model_name,
            indexer.collection,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 10,
        ustawa_filter: str | None = None,
        score_threshold: float | None = None,
    ) -> list[RetrievedChunk]:
        """End-to-end retrieval: query string → top-k chunks z citation_string.

        Args:
            query: Polski tekst pytania (NFC normalized wewnątrz embedder).
            top_k: Liczba zwracanych hits. Default 10.
            ustawa_filter: Opcjonalny filtr (np. ``"DU/2014/827"``).
            score_threshold: Min cosine score (0-1).

        Returns:
            Lista ``RetrievedChunk`` sortowana DESC po score.
        """
        if not query or not query.strip():
            raise ValueError("query nie może być puste")

        query_vec = self.embedder.embed_query(query)
        hits = self.indexer.search(
            query_embedding=query_vec,
            top_k=top_k,
            ustawa_filter=ustawa_filter,
            score_threshold=score_threshold,
        )
        chunks = [RetrievedChunk.from_qdrant_hit(h) for h in hits]
        logger.debug("Retrieved %d chunks dla query: %r", len(chunks), query[:60])
        return chunks

    def retrieve_with_evidence(
        self,
        query: str,
        top_k: int = 10,
        ustawa_filter: str | None = None,
    ) -> dict[str, Any]:
        """Retrieval + format dla Langfuse trace / RAG prompt context.

        Returns:
            Dict struktury::

                {
                    "query": str,
                    "top_k": int,
                    "evidence_chunks": list[dict] (chunk_id, tresc, score),
                    "citation_strings": list[str] (unique, ordered),
                    "scores": list[float],
                }
        """
        chunks = self.retrieve(query, top_k=top_k, ustawa_filter=ustawa_filter)
        # Unikalne citations zachowując kolejność (top score first)
        seen: set[str] = set()
        unique_citations: list[str] = []
        for c in chunks:
            if c.citation_string not in seen:
                seen.add(c.citation_string)
                unique_citations.append(c.citation_string)

        return {
            "query": query,
            "top_k": top_k,
            "ustawa_filter": ustawa_filter,
            "evidence_chunks": [
                {
                    "chunk_id": c.chunk_id,
                    "citation_string": c.citation_string,
                    "tresc": c.tresc,
                    "score": c.score,
                    "ustawa_id": c.ustawa_id,
                    "art": c.art,
                }
                for c in chunks
            ],
            "citation_strings": unique_citations,
            "scores": [c.score for c in chunks],
        }

    def retrieve_cross_register(
        self,
        query: str,
        top_k: int = 10,
    ) -> list[RetrievedChunk]:
        """[STUB Iter. 1+] Cross-register retrieval (lay query → professional answer).

        Hook dla RQ5 cross-register (pierwotnie ChPL↔Ulotka w pharma; tu w
        consumer-rights variant: pytanie z fora → odpowiedź ekspertska UOKiK
        + cytowane ustawy). Wymaga dual-collection (consumer_questions ekspozycji
        jako queries vs legal chunks jako pool) lub query rewriting.

        Returns:
            Lista ``RetrievedChunk`` (na razie noop).

        Raises:
            NotImplementedError: Hook dla Iter. 1+ — wymaga decyzji dataset
                pairing (UOKiK Q→A→cytowane chunks można już użyć jako gold
                triples bez modyfikacji indexer).
        """
        raise NotImplementedError(
            "Cross-register retrieval — stub Iter. 1. "
            "Plan: użyć UOKiK Q&A jako pary (lay_query, expert_answer, cited_chunks) "
            "i ewaluować accuracy@k przy retrievalu z corpus legal chunks."
        )
