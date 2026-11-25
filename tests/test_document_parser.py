import pymupdf
import pytest

import config
from modules.document_parser import DocumentParseError, parse_pasted_text, parse_uploaded_file

LONG_TEXT = "The customer needs a secure web portal for patient records. " * 5


def make_pdf(text: str) -> bytes:
    doc = pymupdf.open()
    page = doc.new_page()
    if text:
        page.insert_textbox(pymupdf.Rect(50, 50, 550, 750), text)
    data = doc.tobytes()
    doc.close()
    return data


def test_txt_file_is_parsed():
    result = parse_uploaded_file("brief.txt", LONG_TEXT.encode("utf-8"))
    assert result.source_type == "txt"
    assert "patient records" in result.text


def test_pdf_file_is_parsed():
    result = parse_uploaded_file("brief.pdf", make_pdf(LONG_TEXT))
    assert result.source_type == "pdf"
    assert result.page_count == 1
    assert "patient records" in result.text


def test_empty_file_rejected():
    with pytest.raises(DocumentParseError):
        parse_uploaded_file("empty.txt", b"")


def test_unsupported_extension_rejected():
    with pytest.raises(DocumentParseError):
        parse_uploaded_file("notes.docx", b"some bytes")


def test_oversize_file_rejected(monkeypatch):
    monkeypatch.setattr(config, "MAX_UPLOAD_MB", 0)
    with pytest.raises(DocumentParseError):
        parse_uploaded_file("big.txt", LONG_TEXT.encode("utf-8"))


def test_blank_pdf_treated_as_scanned():
    with pytest.raises(DocumentParseError) as err:
        parse_uploaded_file("scan.pdf", make_pdf(""))
    assert "OCR" in str(err.value)


def test_corrupt_pdf_rejected():
    with pytest.raises(DocumentParseError):
        parse_uploaded_file("broken.pdf", b"this is not a pdf")


def test_long_text_is_truncated(monkeypatch):
    monkeypatch.setattr(config, "MAX_INPUT_CHARS", 100)
    result = parse_uploaded_file("long.txt", LONG_TEXT.encode("utf-8"))
    assert result.truncated is True
    assert result.char_count == 100
    assert result.warnings


def test_pasted_text_too_short_rejected():
    with pytest.raises(DocumentParseError):
        parse_pasted_text("hi")