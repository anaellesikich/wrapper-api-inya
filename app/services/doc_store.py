# app/services/doc_store.py
"""
Ephemeral document store for user uploads.

- Keeps uploaded text only in memory (RAM)
- Used per session, cleared when server restarts
- Supports .txt, .md, and .pdf files
- Text is injected into /v1/generate calls as context
"""

from typing import Dict, List, Tuple
from fastapi import UploadFile
from pypdf import PdfReader

# session_id -> list[(filename, text)]
_DOCS: Dict[str, List[Tuple[str, str]]] = {}

# To avoid hitting token limits, cap how much we keep per file
MAX_CHARS = 15000  # roughly a few pages of text


# ---------- File reading helpers ----------

def _read_text_file(f: UploadFile) -> str:
    """Reads UTF-8 or fallback text files."""
    data = f.file.read()
    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return data.decode("latin-1", errors="ignore")


def _read_pdf_file(f: UploadFile) -> str:
    """Extracts text from a PDF using PyPDF."""
    reader = PdfReader(f.file)
    parts = []
    for page in
