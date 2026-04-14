"""
Qdrant writer — upserts chunks and their vectors into Qdrant.
"""

import structlog
from typing import List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from app.config import settings

logger = structlog.get_logger(__name__)

_client: QdrantClient | None = None


def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            timeout=30,
        )
    return _client


def upsert_chunks(
    chunks: List[Dict[str, Any]],
    vectors: List[List[float]],
) -> int:
    """
    Upsert a batch of chunks with their vectors into Qdrant.

    Args:
        chunks: List of chunk payload dicts (must include chunk_id and all metadata)
        vectors: Corresponding embedding vectors

    Returns:
        Number of points upserted
    """
    if not chunks or not vectors:
        return 0

    if len(chunks) != len(vectors):
        logger.error("chunks_vectors_mismatch", chunks=len(chunks), vectors=len(vectors))
        return 0

    client = get_client()
    points = []

    for chunk, vector in zip(chunks, vectors):
        if not vector:
            logger.warning("empty_vector_skipped", chunk_id=chunk.get("chunk_id"))
            continue

        # Use deterministic ID derived from chunk_id for idempotent upserts
        # Qdrant uses uint64 IDs or UUID strings
        points.append(PointStruct(
            id=chunk["chunk_id"],
            vector=vector,
            payload=chunk,
        ))

    if not points:
        return 0

    try:
        client.upsert(
            collection_name=settings.QDRANT_COLLECTION,
            points=points,
        )
        logger.info("upserted_chunks", count=len(points))
        return len(points)
    except Exception as e:
        logger.error("qdrant_upsert_failed", error=str(e))
        return 0


def delete_chunks_for_source(source_id: str) -> None:
    """Remove all chunks for a given source (used when source is disabled)."""
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    client = get_client()
    try:
        client.delete(
            collection_name=settings.QDRANT_COLLECTION,
            points_selector=Filter(
                must=[FieldCondition(key="source_id", match=MatchValue(value=source_id))]
            ),
        )
        logger.info("deleted_source_chunks", source_id=source_id)
    except Exception as e:
        logger.error("qdrant_delete_failed", source_id=source_id, error=str(e))
