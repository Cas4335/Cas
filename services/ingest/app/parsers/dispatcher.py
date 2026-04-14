"""
File parser dispatcher — routes files to the appropriate parser by extension.
"""

from pathlib import Path
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


def parse_file(file_path: Path, raw_bytes: bytes) -> str:
    """
    Extract text from a file based on its extension.

    Returns extracted text string, or empty string if parsing fails.
    """
    ext = file_path.suffix.lower()

    parsers = {
        ".txt": parse_text,
        ".md": parse_text,
        ".pdf": parse_pdf,
        ".docx": parse_docx,
        ".csv": parse_csv,
        ".xlsx": parse_xlsx,
    }

    parser = parsers.get(ext)
    if not parser:
        logger.warning("unsupported_file_type", ext=ext, path=str(file_path))
        return ""

    try:
        return parser(raw_bytes, file_path)
    except Exception as e:
        logger.error("parse_failed", path=str(file_path), ext=ext, error=str(e))
        return ""


def parse_text(raw_bytes: bytes, file_path: Path) -> str:
    """Parse plain text and Markdown files."""
    import chardet
    detected = chardet.detect(raw_bytes)
    encoding = detected.get("encoding") or "utf-8"
    try:
        return raw_bytes.decode(encoding, errors="replace")
    except Exception:
        return raw_bytes.decode("utf-8", errors="replace")


def parse_pdf(raw_bytes: bytes, file_path: Path) -> str:
    """Extract text from PDF using pypdf."""
    import io
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(raw_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)
    return "\n\n".join(pages)


def parse_docx(raw_bytes: bytes, file_path: Path) -> str:
    """Extract text from Word documents using python-docx."""
    import io
    from docx import Document

    doc = Document(io.BytesIO(raw_bytes))
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n\n".join(paragraphs)


def parse_csv(raw_bytes: bytes, file_path: Path) -> str:
    """Convert CSV to readable text — each row becomes a sentence."""
    import io
    import csv
    import chardet

    detected = chardet.detect(raw_bytes)
    encoding = detected.get("encoding") or "utf-8"
    text_io = io.StringIO(raw_bytes.decode(encoding, errors="replace"))
    reader = csv.DictReader(text_io)

    rows = []
    headers = reader.fieldnames or []
    for row in reader:
        parts = [f"{k}: {v}" for k, v in row.items() if v and v.strip()]
        if parts:
            rows.append("; ".join(parts))

    header_line = f"Columns: {', '.join(headers)}" if headers else ""
    return header_line + "\n\n" + "\n".join(rows)


def parse_xlsx(raw_bytes: bytes, file_path: Path) -> str:
    """Convert Excel to readable text — each sheet/row becomes text."""
    import io
    import openpyxl

    wb = openpyxl.load_workbook(io.BytesIO(raw_bytes), read_only=True, data_only=True)
    sheets = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = []
        headers = None

        for i, row in enumerate(ws.iter_rows(values_only=True)):
            if i == 0:
                headers = [str(c) if c is not None else "" for c in row]
                continue
            if headers:
                parts = [
                    f"{headers[j]}: {row[j]}"
                    for j in range(min(len(headers), len(row)))
                    if row[j] is not None and str(row[j]).strip()
                ]
                if parts:
                    rows.append("; ".join(parts))

        if rows:
            sheets.append(f"Sheet: {sheet_name}\n" + "\n".join(rows))

    wb.close()
    return "\n\n".join(sheets)
