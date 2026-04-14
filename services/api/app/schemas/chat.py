from pydantic import BaseModel
from typing import List, Optional


class ChatRequest(BaseModel):
    query: str
    top_k: Optional[int] = None  # overrides default if provided


class Citation(BaseModel):
    chunk_id: str
    source_id: str
    source_path: str
    title: str
    department: str
    doc_type: str
    score: float
    excerpt: str  # short excerpt from the chunk


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    grounded: bool  # True if answer is based on retrieved context
    query: str
    retrieved_count: int
