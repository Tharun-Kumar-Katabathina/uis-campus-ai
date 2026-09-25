from pathlib import Path

from pypdf import PdfReader


def extract_pdf(path: Path) -> str:
    """Extract plain text from a PDF, one line per page joined by blank
    lines. Assumes text-based PDFs; scanned/image PDFs would need OCR,
    which is out of scope for this module (roadmap §18)."""
    reader = PdfReader(str(path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(p.strip() for p in pages if p.strip())
