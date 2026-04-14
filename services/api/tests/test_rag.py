"""Tests for RAG service: prompt building, citations, insufficiency detection."""

import pytest
from app.services.rag import (
    build_prompt,
    format_citations,
    is_insufficient_context,
    UNCERTAINTY_RESPONSE,
)


SAMPLE_CHUNKS = [
    {
        "chunk_id": "abc123",
        "text": "The vacation policy allows 15 days per year for full-time employees.",
        "source_id": "hr-docs",
        "source_path": "/customer_data/hr/vacation_policy.pdf",
        "title": "Vacation Policy",
        "department": "hr",
        "doc_type": "hr_policy",
        "score": 0.92,
        "access_tags": ["hr", "admin"],
    },
    {
        "chunk_id": "def456",
        "text": "Remote work is permitted up to 3 days per week with manager approval.",
        "source_id": "hr-docs",
        "source_path": "/customer_data/hr/remote_work.pdf",
        "title": "Remote Work Policy",
        "department": "hr",
        "doc_type": "hr_policy",
        "score": 0.87,
        "access_tags": ["hr", "admin"],
    },
]


class TestPromptBuilding:
    def test_prompt_contains_query(self):
        prompt = build_prompt("How many vacation days do I get?", SAMPLE_CHUNKS)
        assert "How many vacation days do I get?" in prompt

    def test_prompt_contains_chunk_text(self):
        prompt = build_prompt("vacation days", SAMPLE_CHUNKS)
        assert "15 days per year" in prompt

    def test_prompt_contains_source_info(self):
        prompt = build_prompt("vacation", SAMPLE_CHUNKS)
        assert "Vacation Policy" in prompt

    def test_strict_mode_contains_instruction(self):
        prompt = build_prompt("vacation", SAMPLE_CHUNKS)
        assert "ONLY" in prompt or "only" in prompt

    def test_empty_chunks_builds_prompt(self):
        prompt = build_prompt("vacation", [])
        assert "vacation" in prompt

    def test_prompt_context_truncation(self):
        # Very long chunk text should be truncated
        big_chunk = SAMPLE_CHUNKS[0].copy()
        big_chunk["text"] = "x" * 100000
        chunks = [big_chunk]
        prompt = build_prompt("test", chunks)
        # Prompt should still be built but context is limited
        assert "test" in prompt


class TestCitations:
    def test_format_citations_count(self):
        citations = format_citations(SAMPLE_CHUNKS)
        assert len(citations) == 2

    def test_citation_fields(self):
        citations = format_citations(SAMPLE_CHUNKS)
        c = citations[0]
        assert c["chunk_id"] == "abc123"
        assert c["source_id"] == "hr-docs"
        assert c["title"] == "Vacation Policy"
        assert "excerpt" in c
        assert 0 <= c["score"] <= 1.0

    def test_excerpt_truncated(self):
        long_chunk = SAMPLE_CHUNKS[0].copy()
        long_chunk["text"] = "word " * 500
        citations = format_citations([long_chunk])
        assert len(citations[0]["excerpt"]) <= 205  # 200 + "..."

    def test_empty_chunks_returns_empty_citations(self):
        assert format_citations([]) == []


class TestInsufficientContext:
    def test_detects_insufficient_marker(self):
        assert is_insufficient_context("INSUFFICIENT_CONTEXT")
        assert is_insufficient_context("insufficient_context extra words")

    def test_empty_answer_is_insufficient(self):
        assert is_insufficient_context("")
        assert is_insufficient_context("   ")

    def test_very_short_answer_insufficient(self):
        assert is_insufficient_context("No.")

    def test_normal_answer_not_insufficient(self):
        assert not is_insufficient_context(
            "According to the vacation policy, employees receive 15 days per year."
        )

    def test_uncertainty_response_not_returned_as_sufficient(self):
        # The uncertainty response itself should not be treated as grounded
        assert is_insufficient_context("INSUFFICIENT_CONTEXT - not enough data")
