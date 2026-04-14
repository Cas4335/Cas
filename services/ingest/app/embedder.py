"""
Embedding client — calls local Ollama to generate text embeddings.
"""

import structlog
import httpx
from typing import List, Optional

from app.config import settings

logger = structlog.get_logger(__name__)

_client: Optional[httpx.Client] = None


def get_client() -> httpx.Client:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.Client(
            base_url=settings.ollama_base_url,
            timeout=60.0,
        )
    return _client


def embed_text(text: str) -> List[float]:
    """
    Generate an embedding vector for the given text.
    Returns empty list on failure.
    """
    client = get_client()
    try:
        response = client.post(
            "/api/embeddings",
            json={"model": settings.OLLAMA_EMBED_MODEL, "prompt": text},
        )
        response.raise_for_status()
        return response.json().get("embedding", [])
    except Exception as e:
        logger.error("embed_failed", error=str(e))
        return []


def embed_batch(texts: List[str]) -> List[List[float]]:
    """Embed multiple texts, returning a list of vectors."""
    vectors = []
    for text in texts:
        vec = embed_text(text)
        vectors.append(vec)
    return vectors
