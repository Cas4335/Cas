"""
Base connector interface for all source types.

Every connector must implement:
- scan(): yields RawDocument objects
- get_source_type(): returns the source type string
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterator, Optional, List, Dict, Any
from datetime import datetime


@dataclass
class RawDocument:
    """
    A single document or record ready for parsing and chunking.

    Every document must carry all metadata fields needed for Qdrant.
    """
    # Required identification
    item_key: str           # Unique key within the source (file path, table/pk, etc.)
    source_id: str
    source_type: str        # filesystem | postgres | sqlserver
    tenant_id: str

    # Content
    text: str               # Extracted text content
    title: str

    # Metadata (required for access filtering)
    department: str
    access_tags: List[str]
    doc_type: str

    # Provenance
    source_path: str        # Human-readable path/identifier
    modified_at: Optional[datetime] = None
    content_hash: Optional[str] = None  # SHA-256 of raw content, set by connector

    # Extra metadata (flexible)
    extra: Dict[str, Any] = field(default_factory=dict)


class BaseConnector(ABC):
    """Abstract base class for all source connectors."""

    def __init__(self, source_config: dict, tenant_id: str):
        self.source_config = source_config
        self.tenant_id = tenant_id
        self.source_id = source_config["id"]
        self.department = source_config.get("department", "")
        self.access_tags = source_config.get("access_tags", [])
        self.doc_type = source_config.get("doc_type", "document")

    @abstractmethod
    def scan(self) -> Iterator[RawDocument]:
        """
        Yield RawDocument objects for each item in the source.
        Must be a generator to handle large sources incrementally.
        Must NOT write to the source — read-only access only.
        """
        pass

    @abstractmethod
    def get_source_type(self) -> str:
        """Return the source type identifier string."""
        pass

    def get_source_id(self) -> str:
        return self.source_id
