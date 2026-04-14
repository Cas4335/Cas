"""
SQL Server source connector (read-only).

Connects to external Microsoft SQL Server databases using read-only credentials.
Only reads from allowlisted tables/views.

SECURITY: This connector is strictly read-only. Never use write operations.
"""

import hashlib
from datetime import datetime, timezone
from typing import Iterator
import structlog

from app.connectors.base import BaseConnector, RawDocument

logger = structlog.get_logger(__name__)


class SQLServerConnector(BaseConnector):
    def __init__(self, source_config: dict, tenant_id: str):
        super().__init__(source_config, tenant_id)
        self.host = source_config["host"]
        self.port = int(source_config.get("port", 1433))
        self.database = source_config["database"]
        self.user = source_config["user"]
        self.password = source_config["password"]
        self.allowed_tables = source_config.get("allowed_tables", [])

    def get_source_type(self) -> str:
        return "sqlserver"

    def scan(self) -> Iterator[RawDocument]:
        """Connect and read from each allowlisted table."""
        try:
            import pymssql
        except ImportError:
            logger.error("pymssql_not_installed", source_id=self.source_id)
            return

        try:
            conn = pymssql.connect(
                server=self.host,
                port=str(self.port),
                database=self.database,
                user=self.user,
                password=self.password,
                login_timeout=10,
            )
        except Exception as e:
            logger.error("sqlserver_connect_failed", source_id=self.source_id, error=str(e))
            return

        try:
            for table_config in self.allowed_tables:
                yield from self._read_table(conn, table_config)
        finally:
            conn.close()

    def _read_table(self, conn, table_config: dict) -> Iterator[RawDocument]:
        """Read rows from a single allowlisted table."""
        schema = table_config.get("schema", "dbo")
        table = table_config["table"]
        title_col = table_config.get("title_column", "id")
        body_cols = table_config.get("body_columns", [])

        cols = [title_col] + body_cols
        col_list = ", ".join(f"[{c}]" for c in cols)
        # SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED for read-only perf
        sql = f"SELECT {col_list} FROM [{schema}].[{table}]"

        try:
            with conn.cursor(as_dict=True) as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        except Exception as e:
            logger.error(
                "sqlserver_table_read_failed",
                table=f"{schema}.{table}",
                error=str(e),
            )
            return

        for row in rows:
            title = str(row.get(title_col, "Unknown"))

            parts = []
            for col in body_cols:
                val = row.get(col)
                if val and str(val).strip():
                    parts.append(f"{col}: {val}")
            text = "\n".join(parts)

            if not text.strip():
                continue

            item_key = f"{schema}.{table}::{title}"
            content = f"{title}\n{text}"
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            yield RawDocument(
                item_key=item_key,
                source_id=self.source_id,
                source_type="sqlserver",
                tenant_id=self.tenant_id,
                text=content,
                title=title,
                department=self.department,
                access_tags=self.access_tags,
                doc_type=self.doc_type,
                source_path=f"{self.database}/{schema}/{table}/{title}",
                modified_at=datetime.now(timezone.utc),
                content_hash=content_hash,
            )
