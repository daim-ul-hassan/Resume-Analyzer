from __future__ import annotations

from io import BytesIO

from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(BytesIO(file_bytes))
    pages: list[str] = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return "\n".join(pages).strip()


def extract_text_from_txt(file_bytes: bytes) -> str:
    return file_bytes.decode("utf-8", errors="ignore").strip()


def extract_text(filename: str, file_bytes: bytes) -> str:
    lower_name = filename.lower()

    if lower_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)

    if lower_name.endswith(".txt"):
        return extract_text_from_txt(file_bytes)

    raise ValueError("Unsupported file type. Please upload a PDF or TXT file.")
