"""In-memory text extraction for interview application documents."""

from __future__ import annotations

import io
import re
import zipfile
from xml.etree import ElementTree

import pymupdf


MAX_DOCUMENT_CHARACTERS = 30_000
MAX_PDF_PAGES = 10

EMAIL_PATTERN = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}(?!\d)"
)
URL_PATTERN = re.compile(r"\b(?:https?://|www\.)\S+|\b(?:linkedin|github)\.com/\S+", re.I)
STREET_PATTERN = re.compile(
    r"^\s*\d{1,6}\s+.+\b(?:street|st\.?|road|rd\.?|avenue|ave\.?|lane|ln\.?|"
    r"drive|dr\.?|boulevard|blvd\.?|court|ct\.?|way|place|pl\.?)\b.*$",
    re.I,
)
STREET_INLINE_PATTERN = re.compile(
    r"\b\d{1,6}\s+[A-Z0-9 .'’-]+?\b(?:street|st\.?|road|rd\.?|avenue|ave\.?|"
    r"lane|ln\.?|drive|dr\.?|boulevard|blvd\.?|court|ct\.?|way|place|pl\.?)\b"
    r"(?:,?\s+[A-Z .'’-]+,?\s+[A-Z]{2}(?:\s+\d{5}(?:-\d{4})?)?)?",
    re.I,
)


class DocumentParseError(ValueError):
    """Raised when an uploaded document cannot be converted to useful text."""


def _clean_text(text: str) -> str:
    text = text.replace("\x00", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()[:MAX_DOCUMENT_CHARACTERS]


def _pdf_text(data: bytes) -> str:
    with pymupdf.open(stream=data, filetype="pdf") as document:
        pages = [page.get_text("text") for page in document[:MAX_PDF_PAGES]]
    return "\n\n".join(pages)


def _docx_text(data: bytes) -> str:
    # DOCX is a ZIP archive of XML files. Reading the text nodes directly avoids
    # adding another dependency and works for paragraphs as well as tables.
    try:
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            xml = archive.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile) as exc:
        raise DocumentParseError("This DOCX file is damaged or unsupported.") from exc

    root = ElementTree.fromstring(xml)
    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    paragraphs: list[str] = []
    for paragraph in root.iter(f"{namespace}p"):
        text = "".join(node.text or "" for node in paragraph.iter(f"{namespace}t"))
        if text.strip():
            paragraphs.append(text)
    return "\n".join(paragraphs)


def extract_document_text(filename: str, data: bytes) -> str:
    """Extract normalized text without retaining the uploaded file on disk."""
    suffix = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    try:
        if suffix == "pdf":
            text = _pdf_text(data)
        elif suffix == "docx":
            text = _docx_text(data)
        elif suffix == "txt":
            text = data.decode("utf-8-sig", errors="replace")
        else:
            raise DocumentParseError(f"Unsupported file type: .{suffix or 'unknown'}")
    except DocumentParseError:
        raise
    except Exception as exc:
        raise DocumentParseError(f"Could not read {filename}.") from exc

    cleaned = _clean_text(text)
    if len(cleaned) < 40:
        raise DocumentParseError(
            f"Very little text could be read from {filename}. "
            "If it is a scanned document, export it as a text-based PDF or DOCX."
        )
    return cleaned


def redact_contact_details(text: str) -> str:
    """Remove common contact details before text is sent to a model provider."""
    lines = text.splitlines()
    first_nonempty = next((index for index, line in enumerate(lines) if line.strip()), None)
    contact_near_top = any(
        EMAIL_PATTERN.search(line) or PHONE_PATTERN.search(line)
        for line in lines[:6]
    )
    if (
        first_nonempty is not None
        and first_nonempty < 3
        and contact_near_top
        and len(lines[first_nonempty].strip()) <= 80
    ):
        # A short heading immediately above contact details is normally the
        # candidate's name and is not needed for interview tailoring.
        lines[first_nonempty] = "[candidate name removed]"

    redacted_lines: list[str] = []
    for line in lines:
        if STREET_PATTERN.match(line):
            redacted_lines.append("[street address removed]")
            continue
        line = EMAIL_PATTERN.sub("[email removed]", line)
        line = PHONE_PATTERN.sub("[phone removed]", line)
        line = URL_PATTERN.sub("[profile URL removed]", line)
        line = STREET_INLINE_PATTERN.sub("[street address removed]", line)
        redacted_lines.append(line)
    return "\n".join(redacted_lines)
