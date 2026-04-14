"""
Text chunking — splits long documents into overlapping chunks for embedding.

Uses a simple character-based sliding window approach.
Respects sentence/paragraph boundaries where possible.
"""

import hashlib
import uuid
from typing import List
from dataclasses import dataclass


@dataclass
class TextChunk:
    chunk_id: str
    text: str
    chunk_index: int
    total_chunks: int
    content_hash: str


def chunk_text(
    text: str,
    chunk_size: int = 512,
    chunk_overlap: int = 64,
    source_id: str = "",
    item_key: str = "",
) -> List[TextChunk]:
    """
    Split text into overlapping chunks.

    Args:
        text: Full document text
        chunk_size: Target chunk size in characters
        chunk_overlap: Number of characters to overlap between chunks
        source_id: Source identifier (used for deterministic chunk IDs)
        item_key: Item key (used for deterministic chunk IDs)

    Returns:
        List of TextChunk objects
    """
    text = text.strip()
    if not text:
        return []

    # Try to split on paragraph boundaries first
    # Fall back to raw character splitting
    chunks = []
    start = 0
    chunk_index = 0

    while start < len(text):
        end = start + chunk_size

        if end < len(text):
            # Try to find a good break point (paragraph > sentence > word)
            break_pos = _find_break(text, end, chunk_size // 4)
            end = break_pos

        chunk_text_val = text[start:end].strip()
        if chunk_text_val:
            # Deterministic chunk ID from source + item + position
            chunk_id = _make_chunk_id(source_id, item_key, chunk_index)
            content_hash = hashlib.sha256(chunk_text_val.encode()).hexdigest()[:16]

            chunks.append(TextChunk(
                chunk_id=chunk_id,
                text=chunk_text_val,
                chunk_index=chunk_index,
                total_chunks=0,  # filled in after all chunks are created
                content_hash=content_hash,
            ))
            chunk_index += 1

        start = end - chunk_overlap
        if start >= len(text):
            break

    # Set total_chunks
    total = len(chunks)
    for chunk in chunks:
        chunk.total_chunks = total

    return chunks


def _find_break(text: str, target: int, window: int) -> int:
    """
    Find the best break point near `target` within a window.
    Prefers paragraph breaks, then sentence breaks, then word breaks.
    """
    search_start = max(0, target - window)
    search_end = min(len(text), target + window)
    segment = text[search_start:search_end]

    # Prefer double newline (paragraph break)
    pos = segment.rfind("\n\n")
    if pos >= 0:
        return search_start + pos + 2

    # Fall back to single newline
    pos = segment.rfind("\n")
    if pos >= 0:
        return search_start + pos + 1

    # Fall back to sentence end
    for punct in (". ", "! ", "? "):
        pos = segment.rfind(punct)
        if pos >= 0:
            return search_start + pos + len(punct)

    # Fall back to word boundary
    pos = segment.rfind(" ")
    if pos >= 0:
        return search_start + pos + 1

    return target


def _make_chunk_id(source_id: str, item_key: str, chunk_index: int) -> str:
    """Generate a deterministic chunk ID."""
    key = f"{source_id}::{item_key}::{chunk_index}"
    return hashlib.sha256(key.encode()).hexdigest()[:32]
