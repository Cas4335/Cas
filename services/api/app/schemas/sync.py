from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SyncJobResponse(BaseModel):
    id: int
    source_ref: str
    status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    items_scanned: int
    items_indexed: int
    items_skipped: int
    items_failed: int
    error_message: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class SyncStatusResponse(BaseModel):
    source_id: str
    last_job: Optional[SyncJobResponse]
    total_jobs: int
