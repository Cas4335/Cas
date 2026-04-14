"""
Filesystem connector — recursively scans directories for supported files.

Reads files from mounted directories (read-only).
Computes content hashes to skip unchanged files.
"""

import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, List
import fnmatch
import structlog

from app.connectors.base import BaseConnector, RawDocument
from app.parsers.dispatcher import parse_file

logger = structlog.get_logger(__name__)

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx", ".csv", ".xlsx"}


class FilesystemConnector(BaseConnector):
    def __init__(self, source_config: dict, tenant_id: str):
        super().__init__(source_config, tenant_id)
        self.path = source_config["path"]
        self.include_patterns = source_config.get("include_patterns", ["**/*"])
        self.exclude_patterns = source_config.get("exclude_patterns", [])

    def get_source_type(self) -> str:
        return "filesystem"

    def scan(self) -> Iterator[RawDocument]:
        """Walk the directory tree and yield parseable documents."""
        root = Path(self.path)
        if not root.exists():
            logger.warning("filesystem_path_not_found", path=str(root))
            return

        for file_path in self._walk(root):
            try:
                yield self._process_file(file_path)
            except Exception as e:
                logger.error("file_process_failed", path=str(file_path), error=str(e))

    def _walk(self, root: Path) -> Iterator[Path]:
        """Walk the directory, applying include/exclude patterns."""
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
                continue

            rel = str(path.relative_to(root))

            # Use pathlib.PurePath.match() for ** glob support,
            # fall back to fnmatch for simple patterns.
            if not any(self._matches(rel, path, p) for p in self.include_patterns):
                continue

            if any(self._matches(rel, path, p) for p in self.exclude_patterns):
                logger.debug("file_excluded", path=rel)
                continue

            yield path

    @staticmethod
    def _matches(rel: str, path: Path, pattern: str) -> bool:
        """
        Match a relative path against a glob pattern.
        Supports ** via pathlib.PurePath.match() and simple fnmatch patterns.
        """
        from pathlib import PurePosixPath
        # pathlib.PurePath.match() handles ** correctly
        if path.match(pattern):
            return True
        # Also try fnmatch on the relative path for patterns like "*.txt"
        return fnmatch.fnmatch(rel, pattern) or fnmatch.fnmatch(path.name, pattern)

    def _process_file(self, file_path: Path) -> RawDocument:
        """Read, parse, and hash a single file."""
        raw_bytes = file_path.read_bytes()
        content_hash = hashlib.sha256(raw_bytes).hexdigest()

        stat = file_path.stat()
        modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

        # Parse text from file
        text = parse_file(file_path, raw_bytes)
        title = file_path.stem.replace("_", " ").replace("-", " ").title()

        return RawDocument(
            item_key=str(file_path),
            source_id=self.source_id,
            source_type="filesystem",
            tenant_id=self.tenant_id,
            text=text,
            title=title,
            department=self.department,
            access_tags=self.access_tags,
            doc_type=self.doc_type,
            source_path=str(file_path),
            modified_at=modified_at,
            content_hash=content_hash,
        )
