# app/rag/text_extraction.py
from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfReader


def extract_text(file_path: str, content_type: str) -> str:
    """
    Extracts raw text from a PDF, DOCX, or TXT file on disk.
    Raises ValueError for unsupported types — caller should catch and
    mark the Document as FAILED rather than crash the worker.
    """
    path = Path(file_path)

    if content_type == "application/pdf":
        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if content_type in (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ):
        doc = DocxDocument(str(path))
        return "\n".join(p.text for p in doc.paragraphs)

    if content_type == "text/plain":
        return path.read_text(encoding="utf-8", errors="ignore")

    raise ValueError(f"Unsupported content_type for extraction: {content_type}")
