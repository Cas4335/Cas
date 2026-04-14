from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class SourceResponse(BaseModel):
    id: int
    source_id: str
    source_type: str
    tenant_id: str
    department: Optional[str]
    access_tags: Optional[List[str]]
    doc_type: Optional[str]
    is_enabled: bool
    created_at: datetime
    last_synced_at: Optional[datetime]

    model_config = {"from_attributes": True}
