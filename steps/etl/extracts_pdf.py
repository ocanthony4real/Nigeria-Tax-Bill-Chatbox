"""
PDF extraction step for Nigerian tax bill documents.

Extracts text from PDF files using pdfminer with OCR fallback via Tesseract
for pages with limited extractable text.
"""

from zenml import step
from pathlib import Path
from typing import List
import logging
from uuid import UUID
import re


import pytesseract
import pypdfium2 as pdfium
from pdfminer.high_level import extract_text
from llm_engineering.domain.documents import TaxBillDocument

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

FGN_AUTHOR_ID = UUID("11111111-1111-4444-8888-111111111111")

# -----------------------------------------------------------------------------
# Safe, minimal cleanup (LOSSLESS)
# -----------------------------------------------------------------------------

def minimal_cleanup(text: str) -> str:
    """
    Perform ONLY safe, reversible cleanup.
    This function MUST NOT destroy legal meaning.
    """
    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip control characters (except newlines)
    text = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", text)

    return text.strip()

# -----------------------------------------------------------------------------
# Extraction helpers
# -----------------------------------------------------------------------------

def extract_page_text_pdfminer(pdf_path: Path, page_index: int) -> str:
    try:
        return extract_text(pdf_path, page_numbers=[page_index]) or ""
    except Exception as e:
        logger.warning(f"pdfminer failed on page {page_index + 1}: {e}")
        return ""


def extract_page_text_ocr(pdf: pdfium.PdfDocument, page_index: int) -> str:
    page = pdf[page_index]
    try:
        image = page.render(scale=300 / 72).to_pil()
        return pytesseract.image_to_string(image)
    finally:
        page.close()

# -----------------------------------------------------------------------------
# ETL Step
# -----------------------------------------------------------------------------

@step(enable_cache=False)
def extract_pdfs(pdf_dir: str = "data/pdfs") -> List[TaxBillDocument]:
    logger.warning("exctraction of pdf started")

    pdf_dir = Path(pdf_dir)
    documents: List[TaxBillDocument] = []

    for pdf_path in pdf_dir.glob("*.pdf"):
        pdf = pdfium.PdfDocument(str(pdf_path))
        try:
            for page_idx in range(len(pdf)):
                page_number = page_idx + 1

                text = extract_text(pdf_path, page_numbers=[page_idx]) or ""
                extraction_method = "pdfminer"

                # OCR fallback
                if len(text.strip()) < 200:
                    page = pdf[page_idx]
                    try:
                        image = page.render(scale=300 / 72).to_pil()
                        text = pytesseract.image_to_string(image)
                        extraction_method = "ocr"
                    finally:
                        page.close()

                # Minimal cleanup
                text = minimal_cleanup(text)

                if not text:
                    logger.warning(f"Empty page {page_number} in {pdf_path.name}")
                    continue

                doc = TaxBillDocument(
                    file_name=pdf_path.name,
                    page_number=page_number,
                    link=f"{pdf_path.name}#page={page_number}",

                    content={
                        "text": text,
                        "source": "official_gazette",
                        "extraction_method": extraction_method,
                    },
                    platform="nigerian_legislation",
                    author_id=FGN_AUTHOR_ID,
                    author_full_name="Federal Government of Nigeria",
                )

                documents.append(doc)
        finally:
            pdf.close()

    # Bulk insert
    if documents:
        TaxBillDocument.bulk_insert(documents)
        logger.info(f"Inserted {len(documents)} page-level documents")
    else:
        logger.warning("No documents extracted")

    return documents