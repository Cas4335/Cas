"""Tests for file parsers."""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import io
from pathlib import Path
from app.parsers.dispatcher import parse_text, parse_csv


class TestTextParser:
    def test_plain_utf8(self):
        content = "Hello, this is UTF-8 content.".encode("utf-8")
        result = parse_text(content, Path("test.txt"))
        assert "Hello" in result

    def test_empty_file(self):
        result = parse_text(b"", Path("empty.txt"))
        assert result == ""

    def test_handles_latin1(self):
        content = "caf\xe9".encode("latin-1")  # 'café'
        result = parse_text(content, Path("test.txt"))
        assert len(result) > 0


class TestCsvParser:
    def test_basic_csv(self):
        csv_content = "name,role,department\nAlice,engineer,ops\nBob,manager,hr\n".encode()
        result = parse_csv(csv_content, Path("test.csv"))
        assert "Alice" in result
        assert "engineer" in result
        assert "Bob" in result

    def test_csv_with_headers(self):
        csv_content = "col1,col2\nval1,val2\n".encode()
        result = parse_csv(csv_content, Path("test.csv"))
        assert "col1" in result or "val1" in result

    def test_empty_csv(self):
        result = parse_csv(b"", Path("empty.csv"))
        # Should not raise, returns empty or header line
        assert isinstance(result, str)
