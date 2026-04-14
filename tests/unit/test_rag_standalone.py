"""
Standalone unit tests for RAG service logic.
Tests core RAG functions without importing the full app stack.
"""

STRICT_SYSTEM_PROMPT = "Answer based ONLY on the provided context documents. If insufficient, respond with INSUFFICIENT_CONTEXT."
MAX_CONTEXT_TOKENS = 3000

def build_prompt(query, chunks):
    parts = []
    token_count = 0
    for i, chunk in enumerate(chunks, 1):
        part = f"--- Document {i} ---\nTitle: {chunk.get('title','')}\n{chunk.get('text','')}\n"
        estimated = len(part) // 4
        if token_count + estimated > MAX_CONTEXT_TOKENS:
            break
        parts.append(part)
        token_count += estimated
    context = "\n".join(parts)
    return f"{STRICT_SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {query}\n\nAnswer (ONLY from context above):"

def format_citations(chunks):
    citations = []
    for chunk in chunks:
        text = chunk.get("text", "")
        excerpt = text[:200].strip() + ("..." if len(text) > 200 else "")
        citations.append({
            "chunk_id": chunk.get("chunk_id", ""),
            "source_id": chunk.get("source_id", ""),
            "source_path": chunk.get("source_path", ""),
            "title": chunk.get("title", ""),
            "department": chunk.get("department", ""),
            "doc_type": chunk.get("doc_type", ""),
            "score": round(chunk.get("score", 0.0), 4),
            "excerpt": excerpt,
        })
    return citations

def is_insufficient_context(answer):
    return not answer or "INSUFFICIENT_CONTEXT" in answer.upper() or len(answer.strip()) < 10

SAMPLE_CHUNKS = [
    {"chunk_id": "abc123", "text": "The vacation policy allows 15 days per year.", "source_id": "hr-docs",
     "source_path": "/hr/vacation.pdf", "title": "Vacation Policy", "department": "hr", "doc_type": "hr_policy", "score": 0.92},
    {"chunk_id": "def456", "text": "Remote work is permitted 3 days/week.", "source_id": "hr-docs",
     "source_path": "/hr/remote.pdf", "title": "Remote Work Policy", "department": "hr", "doc_type": "hr_policy", "score": 0.87},
]

class TestPromptBuilding:
    def test_prompt_contains_query(self):
        assert "How many vacation days?" in build_prompt("How many vacation days?", SAMPLE_CHUNKS)
    def test_prompt_contains_chunk_text(self):
        assert "15 days per year" in build_prompt("vacation", SAMPLE_CHUNKS)
    def test_prompt_contains_source_info(self):
        assert "Vacation Policy" in build_prompt("vacation", SAMPLE_CHUNKS)
    def test_strict_mode_instruction_present(self):
        assert "ONLY" in build_prompt("vacation", SAMPLE_CHUNKS)
    def test_empty_chunks_builds_prompt(self):
        assert "vacation" in build_prompt("vacation", [])

class TestCitations:
    def test_count(self):
        assert len(format_citations(SAMPLE_CHUNKS)) == 2
    def test_fields(self):
        c = format_citations(SAMPLE_CHUNKS)[0]
        assert c["chunk_id"] == "abc123"
        assert c["title"] == "Vacation Policy"
        assert "excerpt" in c
        assert 0 <= c["score"] <= 1.0
    def test_excerpt_truncated(self):
        long_chunk = {**SAMPLE_CHUNKS[0], "text": "word " * 500}
        assert len(format_citations([long_chunk])[0]["excerpt"]) <= 205
    def test_empty(self):
        assert format_citations([]) == []

class TestInsufficientContext:
    def test_detects_marker(self):
        assert is_insufficient_context("INSUFFICIENT_CONTEXT")
    def test_empty(self):
        assert is_insufficient_context("") and is_insufficient_context("   ")
    def test_short(self):
        assert is_insufficient_context("No.")
    def test_normal(self):
        assert not is_insufficient_context("Employees receive 15 vacation days per year according to policy.")
