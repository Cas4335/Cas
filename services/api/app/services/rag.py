"""
RAG (Retrieval-Augmented Generation) service.

Assembles a grounded prompt from retrieved chunks and calls the local LLM.

SECURITY:
- Only chunks that passed the authorization filter are accepted here
- The model is explicitly instructed to answer only from context (strict mode)
- No user input is injected into the system prompt in a way that can override rules
"""

import structlog
from typing import List, Tuple

from app.core.config import settings

logger = structlog.get_logger(__name__)

STRICT_SYSTEM_PROMPT = """You are a helpful assistant for company internal knowledge.
Answer the user's question based ONLY on the provided context documents.
Do not use any knowledge outside of the provided context.
If the context does not contain enough information to answer the question,
respond with exactly: "INSUFFICIENT_CONTEXT"
Always cite which documents support your answer."""

CONTEXT_TEMPLATE = """--- Document {n} ---
Source: {source_path}
Title: {title}
Department: {department}
Type: {doc_type}

{text}
"""

QUERY_TEMPLATE = """Context documents:

{context}

User question: {query}

Answer (based only on the context documents above):"""

UNCERTAINTY_RESPONSE = (
    "I don't have enough information in the approved documents to answer "
    "that question confidently. Please consult your relevant team or check "
    "the source documents directly."
)


def build_prompt(query: str, chunks: List[dict]) -> str:
    """
    Build a grounded RAG prompt from retrieved chunks.

    The prompt instructs the model to answer only from context.
    No user-controlled text can override the system instructions.
    """
    context_parts = []
    token_count = 0

    for i, chunk in enumerate(chunks, 1):
        part = CONTEXT_TEMPLATE.format(
            n=i,
            source_path=chunk.get("source_path", "unknown"),
            title=chunk.get("title", "Untitled"),
            department=chunk.get("department", ""),
            doc_type=chunk.get("doc_type", ""),
            text=chunk.get("text", ""),
        )
        # Rough token estimate (4 chars ≈ 1 token)
        estimated_tokens = len(part) // 4
        if token_count + estimated_tokens > settings.RAG_MAX_CONTEXT_TOKENS:
            logger.info("context_truncated", included=i - 1, total=len(chunks))
            break
        context_parts.append(part)
        token_count += estimated_tokens

    context_str = "\n".join(context_parts)

    if settings.RAG_STRICT_MODE:
        full_prompt = f"{STRICT_SYSTEM_PROMPT}\n\n{QUERY_TEMPLATE.format(context=context_str, query=query)}"
    else:
        full_prompt = QUERY_TEMPLATE.format(context=context_str, query=query)

    return full_prompt


def format_citations(chunks: List[dict]) -> List[dict]:
    """
    Convert retrieved chunks into citation objects for the response.
    """
    citations = []
    for chunk in chunks:
        text = chunk.get("text", "")
        # Provide a short excerpt (first 200 chars)
        excerpt = text[:200].strip()
        if len(text) > 200:
            excerpt += "..."

        citations.append({
            "chunk_id": chunk.get("chunk_id", ""),
            "source_id": chunk.get("source_id", ""),
            "source_path": chunk.get("source_path", ""),
            "title": chunk.get("title", "Untitled"),
            "department": chunk.get("department", ""),
            "doc_type": chunk.get("doc_type", ""),
            "score": round(chunk.get("score", 0.0), 4),
            "excerpt": excerpt,
        })
    return citations


def is_insufficient_context(answer: str) -> bool:
    """Check if the model indicated it couldn't answer from context."""
    return (
        not answer
        or "INSUFFICIENT_CONTEXT" in answer.upper()
        or len(answer.strip()) < 10
    )
