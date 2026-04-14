"""
Source model — tracks configured data sources.
"""

from datetime import datetime, timezone
from sqlalchemy import String, DateTime, Boolean, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional, List

from app.core.database import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)  # filesystem, postgres, sqlserver
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    access_tags: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)
    doc_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    config_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    sync_jobs: Mapped[List["SyncJob"]] = relationship(back_populates="source")
