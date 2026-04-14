"""
Qdrant client initialization and collection management.

The collection stores all document chunks with their embeddings and metadata.
Metadata fields enable role-based access filtering before retrieval.
"""

import structlog
from qdrant_client import AsyncQdrantClient, QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PayloadSchemaType,
)

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Synchronous client (for non-async contexts)
_sync_client: QdrantClient | None = None
# Async client (for FastAPI route handlers)
_async_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    """Return the synchronous Qdrant client (singleton)."""
    global _sync_client
    if _sync_client is None:
        _sync_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            timeout=30,
        )
    return _sync_client


def get_async_qdrant_client() -> AsyncQdrantClient:
    """Return the async Qdrant client (singleton)."""
    global _async_client
    if _async_client is None:
        _async_client = AsyncQdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            timeout=30,
        )
    return _async_client


async def init_qdrant_collection() -> None:
    """
    Ensure the Qdrant collection exists with the correct vector configuration.
    Creates it if it doesn't exist. Safe to call multiple times.
    """
    client = get_async_qdrant_client()
    collection_name = settings.QDRANT_COLLECTION

    try:
        existing = await client.get_collections()
        names = [c.name for c in existing.collections]

        if collection_name not in names:
            logger.info("creating_qdrant_collection", collection=collection_name)
            await client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=settings.EMBEDDING_DIM,
                    distance=Distance.COSINE,
                ),
            )

            # Create payload indexes for efficient filtering
            # access_tags is the primary filter — index it
            await client.create_payload_index(
                collection_name=collection_name,
                field_name="access_tags",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            await client.create_payload_index(
                collection_name=collection_name,
                field_name="tenant_id",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            await client.create_payload_index(
                collection_name=collection_name,
                field_name="source_id",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            await client.create_payload_index(
                collection_name=collection_name,
                field_name="department",
                field_schema=PayloadSchemaType.KEYWORD,
            )
            logger.info("qdrant_collection_created", collection=collection_name)
        else:
            logger.info("qdrant_collection_exists", collection=collection_name)

    except Exception as e:
        logger.error("qdrant_init_failed", error=str(e))
        raise
