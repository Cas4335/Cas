"""
PostgreSQL source connector (read-only).

Connects to external customer Postgres databases using read-only credentials.
Only reads from allowlisted tables/views — no arbitrary SQL from config.

SECURITY: This connector is strictly read-only. Never use write operations.
"""

import hashlib
from datetime import datetime, timezone
from typing import Iterator
import structlog

from app.connectors.base import BaseConnector, RawDocument

logger = structlog.get_logger(__name__)


class PostgresConnector(BaseConnector):
    def __init__(self, source_config: dict, tenant_id: str):
        super().__init__(source_config, tenant_id)
        self.host = source_config["host"]
        self.port = int(source_config.get("port", 5432))
        self.database = source_config["database"]
        self.user = source_config["user"]
        self.password = source_config["password"]
        self.allowed_tables = source_config.get("allowed_tables", [])

    def get_source_type(self) -> str:
        return "postgres"

    def scan(self) -> Iterator[RawDocument]:
        """Connect and read from each allowlisted table."""
        import psycopg2

        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                dbname=self.database,
                user=self.user,
                password=self.password,
                connect_timeout=10,
                # Explicitly set read-only transaction
                options="-c default_transaction_read_only=on",
            )
        except Exception as e:
            logger.error("postgres_connect_failed", source_id=self.source_id, error=str(e))
            return

        try:
            for table_config in self.allowed_tables:
                yield from self._read_table(conn, table_config)
        finally:
            conn.close()

    def _read_table(self, conn, table_config: dict) -> Iterator[RawDocument]:
        """Read rows from a single allowlisted table and yield as documents."""
        schema = table_config.get("schema", "public")
        table = table_config["table"]
        title_col = table_config.get("title_column", "id")
        body_cols = table_config.get("body_columns", [])

        # Build SELECT with only allowlisted columns
        # This is NOT user input — it comes from the admin-controlled sources.yaml
        cols = [title_col] + body_cols
        col_list = ", ".join(f'"{c}"' for c in cols)
        sql = f'SELECT {col_list} FROM "{schema}"."{table}"'

        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                rows = cur.fetchall()
        except Exception as e:
            logger.error(
                "postgres_table_read_failed",
                table=f"{schema}.{table}",
                error=str(e),
            )
            return

        for row in rows:
            row_dict = dict(zip(cols, row))
            title = str(row_dict.get(title_col, "Unknown"))

            # Build text from body columns
            parts = []
            for col in body_cols:
                val = row_dict.get(col)
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
                source_type="postgres",
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
