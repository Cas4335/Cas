"""Tests for text chunking logic."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.chunker.text_chunker import chunk_text, _make_chunk_id


class TestTextChunker:
    def test_short_text_single_chunk(self):
        text = "This is a short document."
        chunks = chunk_text(text, chunk_size=512, chunk_overlap=64)
        assert len(chunks) == 1
        assert chunks[0].text == text

    def test_long_text_multiple_chunks(self):
        text = "word " * 300  # ~1500 chars
        chunks = chunk_text(text, chunk_size=200, chunk_overlap=20)
        assert len(chunks) > 1

    def test_overlap_creates_overlap(self):
        text = "a" * 400
        chunks = chunk_text(text, chunk_size=200, chunk_overlap=50)
        # Second chunk should start before first ends
        assert len(chunks) >= 2

    def test_empty_text_returns_empty(self):
        chunks = chunk_text("", chunk_size=512)
        assert chunks == []

    def test_whitespace_only_returns_empty(self):
        chunks = chunk_text("   \n\n  ")
        assert chunks == []

    def test_chunk_ids_are_deterministic(self):
        text = "Same content."
        chunks1 = chunk_text(text, source_id="s1", item_key="k1")
        chunks2 = chunk_text(text, source_id="s1", item_key="k1")
        assert chunks1[0].chunk_id == chunks2[0].chunk_id

    def test_different_items_different_ids(self):
        text = "Same content."
        chunks1 = chunk_text(text, source_id="s1", item_key="k1")
        chunks2 = chunk_text(text, source_id="s1", item_key="k2")
        assert chunks1[0].chunk_id != chunks2[0].chunk_id

    def test_total_chunks_set_correctly(self):
        text = "word " * 300
        chunks = chunk_text(text, chunk_size=200, chunk_overlap=20)
        for chunk in chunks:
            assert chunk.total_chunks == len(chunks)

    def test_chunk_index_sequential(self):
        text = "word " * 300
        chunks = chunk_text(text, chunk_size=200, chunk_overlap=20)
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_content_hash_present(self):
        chunks = chunk_text("test text here")
        assert chunks[0].content_hash
        assert len(chunks[0].content_hash) > 0
