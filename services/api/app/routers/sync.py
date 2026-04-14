"""Sync status router — view ingest job status."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth import require_admin
from app.models.user import User
from app.models.sync import SyncJob
from app.schemas.sync import SyncJobResponse, SyncStatusResponse

router = APIRouter()


@router.get("/", response_model=List[SyncJobResponse])
async def list_sync_jobs(
    limit: int = 20,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List recent sync jobs (admin only)."""
    jobs = (
        db.query(SyncJob)
        .order_by(SyncJob.created_at.desc())
        .limit(limit)
        .all()
    )
    return jobs


@router.get("/{source_ref}", response_model=SyncStatusResponse)
async def get_sync_status(
    source_ref: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get the sync status for a specific source (admin only)."""
    jobs = (
        db.query(SyncJob)
        .filter(SyncJob.source_ref == source_ref)
        .order_by(SyncJob.created_at.desc())
        .all()
    )

    last_job = jobs[0] if jobs else None

    return SyncStatusResponse(
        source_id=source_ref,
        last_job=SyncJobResponse.model_validate(last_job) if last_job else None,
        total_jobs=len(jobs),
    )
