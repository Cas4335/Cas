"""
Ingest pipeline — orchestrates scanning, parsing, chunking, embedding, and upsert.

For each source:
1. Scan documents
2. Skip unchanged (by content hash)
3. Chunk text
4. Embed chunks (local Ollama)
5. Upsert to Qdrant
6. Record state in Postgres
"""

import structlog
from datetime import datetime, timezone
from typing import List, Dict, Any

from app.config import settings
from app.connectors.base import RawDocument
from app.chunker.text_chunker import chunk_text
from app.embedder import embed_text
from app.qdrant_writer import upsert_chunks
from app.state_tracker import (
    get_last_hash,
    record_sync_item,
    create_sync_job,
    complete_sync_job,
    get_or_create_source_id,
)

logger = structlog.get_logger(__name__)

# Batch size for Qdrant upserts
UPSERT_BATCH_SIZE = 50


def run_source_sync(source_config: dict) -> Dict[str, int]:
    """
    Run the full ingest pipeline for one source.
    Returns counters: scanned, indexed, skipped, failed
    """
    from app.connectors.filesystem import FilesystemConnector
    from app.connectors.postgres_connector import PostgresConnector
    from app.connectors.sqlserver_connector import SQLServerConnector

    source_type = source_config.get("type", "filesystem")
    source_ref = source_config["id"]
    tenant_id = settings.TENANT_ID

    CONNECTOR_MAP = {
        "filesystem": FilesystemConnector,
        "postgres": PostgresConnector,
        "sqlserver": SQLServerConnector,
    }

    connector_cls = CONNECTOR_MAP.get(source_type)
    if not connector_cls:
        logger.error("unknown_source_type", type=source_type)
        return {"scanned": 0, "indexed": 0, "skipped": 0, "failed": 1}

    # Get/create source record in Postgres
    source_db_id = get_or_create_source_id(source_ref, source_type, tenant_id, source_config)

    # Create a sync job
    job_id = create_sync_job(source_db_id, source_ref)
    if job_id < 0:
        return {"scanned": 0, "indexed": 0, "skipped": 0, "failed": 1}

    counts = {"scanned": 0, "indexed": 0, "skipped": 0, "failed": 0}
    chunk_size = source_config.get("chunk_size", 512)
    chunk_overlap = source_config.get("chunk_overlap", 64)

    connector = connector_cls(source_config, tenant_id)
    batch_chunks: List[Dict[str, Any]] = []
    batch_vectors: List[List[float]] = []

    try:
        for doc in connector.scan():
            counts["scanned"] += 1
            try:
                result = _process_document(
                    doc=doc,
                    job_id=job_id,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    batch_chunks=batch_chunks,
                    batch_vectors=batch_vectors,
                    counts=counts,
                )
                # Flush batch when full
                if len(batch_chunks) >= UPSERT_BATCH_SIZE:
                    _flush_batch(batch_chunks, batch_vectors)
                    batch_chunks.clear()
                    batch_vectors.clear()
            except Exception as e:
                logger.error("document_process_failed", item=doc.item_key, error=str(e))
                counts["failed"] += 1
                record_sync_item(job_id, source_ref, doc.item_key, "", "failed", error=str(e))

        # Flush remaining
        if batch_chunks:
            _flush_batch(batch_chunks, batch_vectors)

        error = None
    except Exception as e:
        error = str(e)
        logger.error("source_sync_failed", source_ref=source_ref, error=error)

    complete_sync_job(
        job_id,
        scanned=counts["scanned"],
        indexed=counts["indexed"],
        skipped=counts["skipped"],
        failed=counts["failed"],
        error=error,
    )

    logger.info(
        "source_sync_complete",
        source_ref=source_ref,
        **counts,
    )
    return counts


def _process_document(
    doc: RawDocument,
    job_id: int,
    chunk_size: int,
    chunk_overlap: int,
    batch_chunks: List,
    batch_vectors: List,
    counts: Dict,
) -> None:
    """Process a single document: check hash, chunk, embed, add to batch."""
    source_ref = doc.source_id

    # Skip if content hash unchanged
    if doc.content_hash:
        last_hash = get_last_hash(source_ref, doc.item_key)
        if last_hash and last_hash == doc.content_hash:
            counts["skipped"] += 1
            record_sync_item(
                job_id, source_ref, doc.item_key,
                doc.content_hash, "skipped",
            )
            return

    if not doc.text or not doc.text.strip():
        record_sync_item(job_id, source_ref, doc.item_key, doc.content_hash or "", "skipped", error="empty text")
        counts["skipped"] += 1
        return

    # Chunk the text
    chunks = chunk_text(
        text=doc.text,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        source_id=doc.source_id,
        item_key=doc.item_key,
    )

    if not chunks:
        counts["skipped"] += 1
        return

    chunk_count = 0
    for chunk in chunks:
        # Embed each chunk
        vector = embed_text(chunk.text)
        if not vector:
            continue

        # Build payload with all required metadata fields
        payload = {
            "chunk_id": chunk.chunk_id,
            "text": chunk.text,
            "tenant_id": doc.tenant_id,
            "source_id": doc.source_id,
            "source_type": doc.source_type,
            "source_path": doc.source_path,
            "title": doc.title,
            "department": doc.department,
            "access_tags": doc.access_tags,
            "doc_type": doc.doc_type,
            "record_id": doc.item_key,
            "modified_at": doc.modified_at.isoformat() if doc.modified_at else "",
            "content_hash": chunk.content_hash,
            "chunk_index": chunk.chunk_index,
            "total_chunks": chunk.total_chunks,
        }

        batch_chunks.append(payload)
        batch_vectors.append(vector)
        chunk_count += 1

    if chunk_count > 0:
        counts["indexed"] += 1
        record_sync_item(
            job_id, source_ref, doc.item_key,
            doc.content_hash or "", "indexed",
            chunk_count=chunk_count,
        )
    else:
        counts["failed"] += 1
        record_sync_item(
            job_id, source_ref, doc.item_key,
            doc.content_hash or "", "failed",
            error="no chunks embedded",
        )


def _flush_batch(chunks: List[Dict], vectors: List[List[float]]) -> None:
    """Write a batch to Qdrant."""
    count = upsert_chunks(chunks, vectors)
    logger.info("batch_flushed", count=count)
