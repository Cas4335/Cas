"""
AuditLog model — records every user query and retrieval event.

Every query must be logged with:
- who asked (user_id)
- what they asked (query text)
- which chunks were retrieved (chunk_ids)
- what answer was returned (answer_summary)
- when (timestamp)
"""

from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)

    # The user's query
    query_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Roles active at query time (snapshot)
    user_roles: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)

    # Access tags derived from roles (snapshot of what filter was applied)
    allowed_tags: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)

    # Retrieved chunk IDs
    retrieved_chunk_ids: Mapped[Optional[List]] = mapped_column(JSON, nullable=True)

    # Answer metadata
    answer_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_grounded: Mapped[Optional[bool]] = mapped_column(default=True, nullable=True)

    # Latency in milliseconds
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    user: Mapped["User"] = relationship(back_populates="audit_logs")
