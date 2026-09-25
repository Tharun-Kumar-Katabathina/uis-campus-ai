from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

from ingestion.extractors import extract_html, extract_pdf

HTML_FIXTURE = """
<html><body>
<nav><a href="/">Home</a> Skip to main content</nav>
<header>Site Header Menu</header>
<main>
  <h1>Test Page Title</h1>
  <p>This is the real paragraph content that should survive extraction.</p>
  <ul><li>First item</li><li>Second item</li></ul>
</main>
<footer>Copyright 2026. All rights reserved.</footer>
</body></html>
"""


def test_extract_html_preserves_structure_and_drops_boilerplate(tmp_path: Path):
    html_path = tmp_path / "page.html"
    html_path.write_text(HTML_FIXTURE, encoding="utf-8")

    text = extract_html(html_path)

    assert "# Test Page Title" in text
    assert "This is the real paragraph content that should survive extraction." in text
    assert "- First item" in text
    assert "- Second item" in text
    # nav/header/footer tags are dropped entirely by the extractor
    assert "Site Header Menu" not in text
    assert "Copyright" not in text


def test_extract_pdf_returns_text(tmp_path: Path):
    pdf_path = tmp_path / "doc.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=LETTER)
    text = c.beginText(72, 720)
    text.textLine("Extractable PDF sentence for the unit test.")
    c.drawText(text)
    c.showPage()
    c.save()

    extracted = extract_pdf(pdf_path)

    assert "Extractable PDF sentence for the unit test." in extracted
