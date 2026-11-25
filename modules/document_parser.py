"""Reads uploaded PDF/TXT files or pasted text and returns clean text."""
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import config

try:
    import pymupdf as fitz  # newer PyMuPDF name
except ImportError:  # pragma: no cover
    import fitz  # older name

SUPPORTED_EXTENSIONS = {".pdf", ".txt"}
MIN_TEXT_CHARS = 50  # fewer characters than this in a PDF = probably scanned images


class DocumentParseError(Exception):
    """Raised with a user-friendly message when a document can't be used."""


@dataclass
class ParsedDocument:
    filename: str
    source_type: str  # "pdf", "txt" or "pasted"
    text: str
    page_count: int = 0
    truncated: bool = False
    warnings: List[str] = field(default_factory=list)

    @property
    def char_count(self) -> int:
        return len(self.text)


def _clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _limit_length(text: str, warnings: List[str]) -> tuple:
    """Cut very long documents so they fit the model's limits."""
    if len(text) > config.MAX_INPUT_CHARS:
        warnings.append(
            f"The document has {len(text):,} characters. Only the first "
            f"{config.MAX_INPUT_CHARS:,} are analysed; later content is ignored."
        )
        return text[: config.MAX_INPUT_CHARS], True
    return text, False


def _decode_text(data: bytes) -> str:
    for encoding in ("utf-8-sig", "utf-16", "cp1252"):
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, UnicodeError):
            continue
    return data.decode("latin-1", errors="ignore")


def _extract_pdf(data: bytes) -> tuple:
    try:
        doc = fitz.open(stream=data, filetype="pdf")
    except Exception as e:
        raise DocumentParseError("This PDF could not be opened. It may be corrupt or not a real PDF.") from e

    try:
        if doc.needs_pass:
            raise DocumentParseError("This PDF is password-protected. Please upload an unlocked copy.")
        pages = [page.get_text("text") for page in doc]
        return "\n\n".join(pages), len(pages)
    except DocumentParseError:
        raise
    except Exception as e:
        raise DocumentParseError("Text could not be read from this PDF.") from e
    finally:
        doc.close()


def parse_uploaded_file(filename: str, data: bytes) -> ParsedDocument:
    """Parse an uploaded file. Raises DocumentParseError with a clear message on problems."""
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise DocumentParseError(f"Unsupported file type '{ext or 'unknown'}'. Please upload a PDF or TXT file.")
    if not data:
        raise DocumentParseError("The uploaded file is empty.")
    max_bytes = config.MAX_UPLOAD_MB * 1024 * 1024
    if len(data) > max_bytes:
        raise DocumentParseError(f"The file is larger than the {config.MAX_UPLOAD_MB} MB limit.")

    warnings: List[str] = []
    page_count = 0
    if ext == ".pdf":
        raw_text, page_count = _extract_pdf(data)
        source_type = "pdf"
    else:
        raw_text = _decode_text(data)
        source_type = "txt"

    text = _clean_text(raw_text)
    if len(text) < MIN_TEXT_CHARS:
        if source_type == "pdf":
            raise DocumentParseError(
                "No readable text was found in this PDF. It may be a scanned document (images). "
                "OCR is not supported in this MVP - please upload a text-based PDF or paste the text."
            )
        raise DocumentParseError("The file contains too little text to analyse.")

    text, truncated = _limit_length(text, warnings)
    return ParsedDocument(filename, source_type, text, page_count, truncated, warnings)


def parse_pasted_text(text: str) -> ParsedDocument:
    """Use text the user typed or pasted into the text box."""
    cleaned = _clean_text(text or "")
    if len(cleaned) < MIN_TEXT_CHARS:
        raise DocumentParseError("Please paste at least a few sentences of project requirements.")
    warnings: List[str] = []
    cleaned, truncated = _limit_length(cleaned, warnings)
    return ParsedDocument("Pasted text", "pasted", cleaned, 0, truncated, warnings)