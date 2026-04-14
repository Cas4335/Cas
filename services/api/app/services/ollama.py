"""
Ollama client for local LLM inference and text embedding.

All model calls are local — no outbound internet requests.
"""

import structlog
import httpx
from typing import List, Optional

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Shared async HTTP client (reused across requests)
_http_client: Optional[httpx.AsyncClient] = None


def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            base_url=settings.ollama_base_url,
            timeout=120.0,  # LLM inference can take time
        )
    return _http_client


async def embed_text(text: str) -> List[float]:
    """
    Generate an embedding vector for the given text using the local Ollama model.

    Returns:
        List of floats (embedding vector), or empty list on failure.
    """
    client = get_http_client()
    try:
        response = await client.post(
            "/api/embeddings",
            json={"model": settings.OLLAMA_EMBED_MODEL, "prompt": text},
        )
        response.raise_for_status()
        data = response.json()
        return data.get("embedding", [])
    except Exception as e:
        logger.error("embed_failed", model=settings.OLLAMA_EMBED_MODEL, error=str(e))
        return []


async def generate_answer(prompt: str) -> str:
    """
    Generate a text response from the local LLM.

    Uses the /api/generate endpoint (non-streaming).

    Returns:
        Generated text string, or empty string on failure.
    """
    client = get_http_client()
    try:
        response = await client.post(
            "/api/generate",
            json={
                "model": settings.OLLAMA_LLM_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.1,  # Low temperature for factual retrieval
                    "num_predict": 1024,
                },
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        logger.error("generate_failed", model=settings.OLLAMA_LLM_MODEL, error=str(e))
        return ""
