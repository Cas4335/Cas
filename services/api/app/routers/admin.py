"""Admin router — audit logs and user management."""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth import require_admin
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse
from app.schemas.auth import UserMeResponse

router = APIRouter()


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def list_audit_logs(
    limit: int = Query(default=50, le=500),
    offset: int = Query(default=0, ge=0),
    user_id: int = Query(default=None),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List audit log entries (admin only). Supports pagination and filtering by user."""
    query = db.query(AuditLog).order_by(AuditLog.created_at.desc())
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    logs = query.offset(offset).limit(limit).all()
    return logs


@router.get("/users", response_model=List[UserMeResponse])
async def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List all users (admin only)."""
    users = db.query(User).all()
    return [
        UserMeResponse(
            id=u.id,
            email=u.email,
            display_name=u.display_name,
            roles=u.get_role_names(),
            is_active=u.is_active,
            created_at=u.created_at,
        )
        for u in users
    ]
