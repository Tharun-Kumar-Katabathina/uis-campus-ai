"""One-off script that generated ingestion/sources/raw/registration_policy.pdf.
Not part of the pipeline itself — kept so the fixture can be regenerated."""

from pathlib import Path

from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas

OUTPUT = Path(__file__).resolve().parent.parent / "sources" / "raw" / "registration_policy.pdf"

PARAGRAPHS = [
    "Course Registration Policy",
    "",
    "This document is synthetic sample content for the UIS CampusAI portfolio",
    "project and does not represent an actual university policy.",
    "",
    "Eligibility",
    "Students in good academic standing may register for courses during their",
    "assigned registration window. A registration hold placed by the Registrar,",
    "Bursar, or Health Services office will prevent registration until resolved.",
    "",
    "Credit Limits",
    "Undergraduate students may register for up to 18 credit hours per semester",
    "without approval. Students wishing to register for more than 18 credit hours",
    "must obtain written approval from their academic advisor and dean.",
    "",
    "Prerequisites",
    "Students may not register for a course without having satisfied its listed",
    "prerequisites, unless granted an override by the offering department.",
    "",
    "Late Registration",
    "Registration after the first week of classes requires instructor permission",
    "and is subject to a late registration fee assessed by the Bursar's office.",
]


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUTPUT), pagesize=LETTER)
    text = c.beginText(72, 720)
    text.setFont("Helvetica", 11)
    for line in PARAGRAPHS:
        text.textLine(line)
    c.drawText(text)
    c.showPage()
    c.save()
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
