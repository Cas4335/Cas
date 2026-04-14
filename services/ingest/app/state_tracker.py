"""
State tracker — records sync state in Postgres to enable incremental syncs.

Uses content hashes to skip unchanged files/records.
"""

import structlog
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.config import settings

logger = structlog.get_logger(__name__)

_engine = None
_SessionLocal = None


def get_session() -> Session:
    global _engine, _SessionLocal
    if _engine is None:
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
        _SessionLocal = sessionmaker(bind=_engine)
    return _SessionLocal()


def get_last_hash(source_ref: str, item_key: str) -> Optional[str]:
    """
    Get the content hash from the most recent successful index of this item.
    Returns None if never indexed.
    """
    from sqlalchemy import text
    session = get_session()
    try:
        result = session.execute(
            text("""
                SELECT si.content_hash
                FROM sync_items si
                JOIN sync_jobs sj ON si.job_id = sj.id
                WHERE si.source_ref = :source_ref
                  AND si.item_key = :item_key
                  AND si.status = 'indexed'
                ORDER BY si.indexed_at DESC
                LIMIT 1
            """),
            {"source_ref": source_ref, "item_key": item_key},
        ).fetchone()
        return result[0] if result else None
    except Exception as e:
        logger.error("state_check_failed", error=str(e))
        return None
    finally:
        session.close()


def create_sync_job(source_id_int: int, source_ref: str) -> int:
    """Create a new sync job record and return its ID."""
    from sqlalchemy import text
    session = get_session()
    try:
        result = session.execute(
            text("""
                INSERT INTO sync_jobs (source_id, source_ref, status, started_at, created_at)
                VALUES (:source_id, :source_ref, 'running', NOW(), NOW())
                RETURNING id
            """),
            {"source_id": source_id_int, "source_ref": source_ref},
        )
        job_id = result.fetchone()[0]
        session.commit()
        logger.info("sync_job_created", job_id=job_id, source_ref=source_ref)
        return job_id
    except Exception as e:
        session.rollback()
        logger.error("sync_job_create_failed", error=str(e))
        return -1
    finally:
        session.close()


def complete_sync_job(
    job_id: int,
    scanned: int,
    indexed: int,
    skipped: int,
    failed: int,
    error: Optional[str] = None,
) -> None:
    """Mark a sync job as completed."""
    from sqlalchemy import text
    status = "failed" if error else "completed"
    session = get_session()
    try:
        session.execute(
            text("""
                UPDATE sync_jobs
                SET status = :status,
                    finished_at = NOW(),
                    items_scanned = :scanned,
                    items_indexed = :indexed,
                    items_skipped = :skipped,
                    items_failed = :failed,
                    error_message = :error
                WHERE id = :job_id
            """),
            {
                "status": status,
                "scanned": scanned,
                "indexed": indexed,
                "skipped": skipped,
                "failed": failed,
                "error": error,
                "job_id": job_id,
            },
        )
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error("sync_job_complete_failed", error=str(e))
    finally:
        session.close()


def record_sync_item(
    job_id: int,
    source_ref: str,
    item_key: str,
    content_hash: str,
    status: str,
    chunk_count: int = 0,
    error: Optional[str] = None,
) -> None:
    """Record the result for a single synced item."""
    from sqlalchemy import text
    session = get_session()
    try:
        session.execute(
            text("""
                INSERT INTO sync_items
                    (job_id, source_ref, item_key, content_hash, status, chunk_count, error_message, indexed_at)
                VALUES
                    (:job_id, :source_ref, :item_key, :content_hash, :status, :chunk_count, :error, NOW())
            """),
            {
                "job_id": job_id,
                "source_ref": source_ref,
                "item_key": item_key,
                "content_hash": content_hash,
                "status": status,
                "chunk_count": chunk_count,
                "error": error,
            },
        )
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error("sync_item_record_failed", error=str(e))
    finally:
        session.close()


def get_or_create_source_id(source_ref: str, source_type: str, tenant_id: str, config: dict) -> int:
    """Get the integer PK for a source, creating it if not present."""
    import json
    from sqlalchemy import text
    session = get_session()
    try:
        result = session.execute(
            text("SELECT id FROM sources WHERE source_id = :source_id"),
            {"source_id": source_ref},
        ).fetchone()

        if result:
            return result[0]

        result = session.execute(
            text("""
                INSERT INTO sources
                    (source_id, source_type, tenant_id, department, access_tags, doc_type, config_snapshot, is_enabled, created_at)
                VALUES
                    (:source_id, :source_type, :tenant_id, :dept, :tags::jsonb, :doc_type, :config::jsonb, true, NOW())
                RETURNING id
            """),
            {
                "source_id": source_ref,
                "source_type": source_type,
                "tenant_id": tenant_id,
                "dept": config.get("department", ""),
                "tags": json.dumps(config.get("access_tags", [])),
                "doc_type": config.get("doc_type", "document"),
                "config": json.dumps({k: v for k, v in config.items() if k != "password"}),
            },
        )
        source_id = result.fetchone()[0]
        session.commit()
        return source_id
    except Exception as e:
        session.rollback()
        logger.error("source_create_failed", source_ref=source_ref, error=str(e))
        return -1
    finally:
        session.close()
