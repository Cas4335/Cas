"""
Chat router — the primary user-facing endpoint.

Flow:
1. Authenticate user (JWT)
2. Load user roles from DB
3. Derive allowed access_tags from roles
4. Retrieve authorized chunks from Qdrant (filtered)
5. Build grounded RAG prompt
6. Call local LLM
7. Return answer + citations
8. Log audit record

SECURITY: Authorization filter is built from roles, never from user input.
The model only sees chunks that passed the filter.
"""

import time
import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.roles import get_allowed_tags
from app.middleware.auth import get_current_user
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.chat import ChatRequest, ChatResponse, Citation
from app.services.retrieval import retrieve_authorized_chunks
from app.services.ollama import generate_answer
from app.services.rag import build_prompt, format_citations, is_insufficient_context, UNCERTAINTY_RESPONSE

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Answer a user question using strict RAG over authorized documents.
    """
    start_time = time.monotonic()

    # 1. Derive allowed tags from user roles
    user_roles = current_user.get_role_names()
    allowed_tags = get_allowed_tags(user_roles)

    if not allowed_tags:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access tags configured for your role",
        )

    logger.info(
        "chat_request",
        user_id=current_user.id,
        roles=user_roles,
        tag_count=len(allowed_tags),
    )

    # 2. Retrieve authorized chunks
    top_k = request.top_k or settings.RAG_TOP_K
    chunks = await retrieve_authorized_chunks(
        query=request.query,
        allowed_tags=allowed_tags,
        top_k=top_k,
    )

    # 3. Build response
    grounded = True
    answer = UNCERTAINTY_RESPONSE
    citations = []

    if chunks:
        # Build and send grounded prompt
        prompt = build_prompt(request.query, chunks)
        raw_answer = await generate_answer(prompt)

        if is_insufficient_context(raw_answer):
            grounded = False
            answer = UNCERTAINTY_RESPONSE
        else:
            answer = raw_answer
            grounded = True

        citations = format_citations(chunks)
    else:
        grounded = False

    latency_ms = int((time.monotonic() - start_time) * 1000)

    # 4. Write audit log
    chunk_ids = [c.get("chunk_id") for c in chunks]
    audit = AuditLog(
        user_id=current_user.id,
        tenant_id=settings.TENANT_ID,
        query_text=request.query,
        user_roles=user_roles,
        allowed_tags=allowed_tags,
        retrieved_chunk_ids=chunk_ids,
        answer_text=answer[:500] if answer else None,  # truncate for storage
        answer_grounded=grounded,
        latency_ms=latency_ms,
    )
    db.add(audit)
    db.commit()

    logger.info(
        "chat_response",
        user_id=current_user.id,
        chunks=len(chunks),
        grounded=grounded,
        latency_ms=latency_ms,
    )

    return ChatResponse(
        answer=answer,
        citations=[Citation(**c) for c in citations],
        grounded=grounded,
        query=request.query,
        retrieved_count=len(chunks),
    )
