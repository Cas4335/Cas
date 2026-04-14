"""
Retrieval service: embeds a query and retrieves authorized chunks from Qdrant.

SECURITY CRITICAL:
- allowed_tags is derived from user roles BEFORE this function is called
- The Qdrant filter is built from allowed_tags — never from user input
- The model only sees chunks returned by this function
"""

import structlog
from typing import List, Optional

from qdrant_client.models import Filter, FieldCondition, MatchAny

from app.core.qdrant_client import get_async_qdrant_client
from app.core.config import settings
from app.services.ollama import embed_text

logger = structlog.get_logger(__name__)


async def retrieve_authorized_chunks(
    query: str,
    allowed_tags: List[str],
    top_k: int = None,
    min_score: float = None,
) -> List[dict]:
    """
    Embed the query and retrieve the top-k chunks the user is authorized to see.

    Args:
        query: User's natural language question
        allowed_tags: Tags derived from user roles (not from user input)
        top_k: Number of chunks to retrieve
        min_score: Minimum similarity score threshold

    Returns:
        List of chunk dicts with text, metadata, and score
    """
    top_k = top_k or settings.RAG_TOP_K
    min_score = min_score or settings.RAG_MIN_SCORE

    if not allowed_tags:
        logger.warning("retrieve_called_with_empty_tags")
        return []

    # Build authorization filter — this is applied BEFORE any chunk reaches the model
    auth_filter = Filter(
        must=[
            FieldCondition(
                key="access_tags",
                match=MatchAny(any=allowed_tags),
            ),
            FieldCondition(
                key="tenant_id",
                match={"value": settings.TENANT_ID},
            ),
        ]
    )

    # Embed the query using the local model
    query_vector = await embed_text(query)
    if not query_vector:
        logger.error("embed_failed_for_query")
        return []

    client = get_async_qdrant_client()

    try:
        results = await client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_vector,
            query_filter=auth_filter,
            limit=top_k,
            score_threshold=min_score,
            with_payload=True,
        )
    except Exception as e:
        logger.error("qdrant_search_failed", error=str(e))
        return []

    chunks = []
    for hit in results:
        payload = hit.payload or {}
        chunks.append({
            "chunk_id": payload.get("chunk_id", str(hit.id)),
            "score": hit.score,
            "text": payload.get("text", ""),
            "source_id": payload.get("source_id", ""),
            "source_path": payload.get("source_path", ""),
            "title": payload.get("title", ""),
            "department": payload.get("department", ""),
            "doc_type": payload.get("doc_type", ""),
            "access_tags": payload.get("access_tags", []),
            "modified_at": payload.get("modified_at", ""),
        })

    logger.info(
        "retrieval_complete",
        query_len=len(query),
        chunks_returned=len(chunks),
        tags_used=len(allowed_tags),
    )
    return chunks
