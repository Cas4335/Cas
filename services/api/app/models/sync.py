"""
SyncJob and SyncItem models — track ingestion state.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class SyncJob(Base):
    """Represents a single ingest run for a source."""
    __tablename__ = "sync_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[int] = mapped_column(Integer, ForeignKey("sources.id"), nullable=False)
    source_ref: Mapped[str] = mapped_column(String(255), nullable=False)  # source.source_id string
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="pending")
    # status: pending | running | completed | failed
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    items_scanned: Mapped[int] = mapped_column(Integer, default=0)
    items_indexed: Mapped[int] = mapped_column(Integer, default=0)
    items_skipped: Mapped[int] = mapped_column(Integer, default=0)
    items_failed: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    source: Mapped["Source"] = relationship(back_populates="sync_jobs")
    items: Mapped[list["SyncItem"]] = relationship(back_populates="job")


class SyncItem(Base):
    """
    Tracks the ingestion state of a single document or DB row.
    Used to skip unchanged items on subsequent sync runs.
    """
    __tablename__ = "sync_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("sync_jobs.id"), nullable=False)
    source_ref: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    # Unique identifier for this item within its source (file path, row ID, etc.)
    item_key: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    content_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(64), nullable=False, default="pending")
    # status: indexed | skipped | failed
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    indexed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    job: Mapped["SyncJob"] = relationship(back_populates="items")
