"""Tests for filesystem connector."""

import sys, os, tempfile, hashlib
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from app.connectors.filesystem import FilesystemConnector


def make_connector(tmpdir: str, **kwargs) -> FilesystemConnector:
    config = {
        "id": "test-source",
        "type": "filesystem",
        "path": tmpdir,
        "department": "testing",
        "access_tags": ["shared_user"],
        "doc_type": "test_doc",
        "include_patterns": ["**/*"],
        "exclude_patterns": [],
        **kwargs,
    }
    return FilesystemConnector(config, tenant_id="test-tenant")


class TestFilesystemConnector:
    def test_scans_txt_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.txt").write_text("Hello world content")
            connector = make_connector(tmpdir)
            docs = list(connector.scan())
            assert len(docs) == 1
            assert "Hello world content" in docs[0].text

    def test_skips_unsupported_extensions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "file.py").write_text("print('hello')")
            (Path(tmpdir) / "file.txt").write_text("good file")
            connector = make_connector(tmpdir)
            docs = list(connector.scan())
            assert len(docs) == 1  # only .txt

    def test_recursive_scan(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            (subdir / "nested.txt").write_text("nested content")
            (Path(tmpdir) / "root.txt").write_text("root content")
            connector = make_connector(tmpdir)
            docs = list(connector.scan())
            assert len(docs) == 2

    def test_exclude_patterns(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "keep.txt").write_text("keep this")
            (Path(tmpdir) / "~$temp.txt").write_text("temp file")
            connector = make_connector(tmpdir, exclude_patterns=["**/$~*", "**/~$*"])
            docs = list(connector.scan())
            assert len(docs) == 1
            assert docs[0].text == "keep this"

    def test_content_hash_computed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            content = b"test content for hashing"
            (Path(tmpdir) / "test.txt").write_bytes(content)
            connector = make_connector(tmpdir)
            docs = list(connector.scan())
            expected_hash = hashlib.sha256(content).hexdigest()
            assert docs[0].content_hash == expected_hash

    def test_metadata_fields_present(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "doc.txt").write_text("content")
            connector = make_connector(tmpdir)
            doc = list(connector.scan())[0]
            assert doc.source_id == "test-source"
            assert doc.tenant_id == "test-tenant"
            assert doc.department == "testing"
            assert doc.access_tags == ["shared_user"]
            assert doc.doc_type == "test_doc"
            assert doc.source_type == "filesystem"
            assert doc.modified_at is not None

    def test_missing_path_yields_nothing(self):
        connector = make_connector("/nonexistent/path/xyz")
        docs = list(connector.scan())
        assert docs == []

    def test_unchanged_file_has_same_hash(self):
        """Same file content → same hash (enables skip logic)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            content = "stable content"
            (Path(tmpdir) / "file.txt").write_text(content)
            connector = make_connector(tmpdir)
            docs1 = list(connector.scan())
            docs2 = list(connector.scan())
            assert docs1[0].content_hash == docs2[0].content_hash
