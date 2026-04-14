from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AuditLogResponse(BaseModel):
    id: int
    user_id: int
    tenant_id: str
    query_text: str
    user_roles: Optional[List[str]]
    allowed_tags: Optional[List[str]]
    retrieved_chunk_ids: Optional[List[str]]
    answer_grounded: Optional[bool]
    latency_ms: Optional[int]
    created_at: datetime

    model_config = {"from_attributes": True}
