from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter


ROOT = Path(__file__).resolve().parent
TEMPLATE_PDF = ROOT / "PAIC_Submission_Template.pdf"
OUTPUT_PDF = Path("/mnt/data/PAIC_Final_Submission.pdf")


def build_pdf() -> None:
    if not TEMPLATE_PDF.exists():
        raise FileNotFoundError(f"Template PDF not found: {TEMPLATE_PDF}")

    OUTPUT_PDF.parent.mkdir(parents=True, exist_ok=True)

    template_reader = PdfReader(str(TEMPLATE_PDF))
    writer = PdfWriter()
    for page in template_reader.pages:
        writer.add_page(page)

    with OUTPUT_PDF.open("wb") as handle:
        writer.write(handle)


if __name__ == "__main__":
    build_pdf()
