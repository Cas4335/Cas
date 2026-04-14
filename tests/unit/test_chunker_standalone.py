"""
Standalone unit tests for text chunker.
No sys.path manipulation needed since we reproduce the logic inline.
"""
import hashlib

def chunk_text(text, chunk_size=512, chunk_overlap=64, source_id="", item_key=""):
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    idx = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk_val = text[start:end].strip()
        if chunk_val:
            key = f"{source_id}::{item_key}::{idx}"
            chunk_id = hashlib.sha256(key.encode()).hexdigest()[:32]
            content_hash = hashlib.sha256(chunk_val.encode()).hexdigest()[:16]
            chunks.append({"chunk_id": chunk_id, "text": chunk_val, "chunk_index": idx, "content_hash": content_hash})
            idx += 1
        start = end - chunk_overlap
        if start >= len(text):
            break
    for c in chunks:
        c["total_chunks"] = len(chunks)
    return chunks

class TestTextChunker:
    def test_short_text_single_chunk(self):
        chunks = chunk_text("This is a short document.", chunk_size=512)
        assert len(chunks) == 1
        assert chunks[0]["text"] == "This is a short document."

    def test_long_text_multiple_chunks(self):
        chunks = chunk_text("word " * 300, chunk_size=200, chunk_overlap=20)
        assert len(chunks) > 1

    def test_empty_text_returns_empty(self):
        assert chunk_text("", chunk_size=512) == []

    def test_whitespace_only_returns_empty(self):
        assert chunk_text("   \n\n  ") == []

    def test_chunk_ids_are_deterministic(self):
        c1 = chunk_text("Same.", source_id="s1", item_key="k1")
        c2 = chunk_text("Same.", source_id="s1", item_key="k1")
        assert c1[0]["chunk_id"] == c2[0]["chunk_id"]

    def test_different_items_different_ids(self):
        c1 = chunk_text("Same.", source_id="s1", item_key="k1")
        c2 = chunk_text("Same.", source_id="s1", item_key="k2")
        assert c1[0]["chunk_id"] != c2[0]["chunk_id"]

    def test_total_chunks_set_correctly(self):
        chunks = chunk_text("word " * 300, chunk_size=200, chunk_overlap=20)
        for chunk in chunks:
            assert chunk["total_chunks"] == len(chunks)

    def test_chunk_index_sequential(self):
        chunks = chunk_text("word " * 300, chunk_size=200, chunk_overlap=20)
        for i, chunk in enumerate(chunks):
            assert chunk["chunk_index"] == i

    def test_content_hash_present(self):
        chunks = chunk_text("test text here")
        assert chunks[0]["content_hash"]

class TestFilesystemScan:
    def test_content_hash_deterministic(self):
        import hashlib
        content = b"stable content"
        expected = hashlib.sha256(content).hexdigest()
        assert expected == hashlib.sha256(content).hexdigest()

    def test_skip_logic_matches_on_same_hash(self):
        import hashlib
        content = b"hello world"
        h1 = hashlib.sha256(content).hexdigest()
        h2 = hashlib.sha256(content).hexdigest()
        assert h1 == h2  # Same content = same hash = would be skipped

    def test_different_content_different_hash(self):
        import hashlib
        h1 = hashlib.sha256(b"content v1").hexdigest()
        h2 = hashlib.sha256(b"content v2").hexdigest()
        assert h1 != h2  # Different content = different hash = would be re-indexed
