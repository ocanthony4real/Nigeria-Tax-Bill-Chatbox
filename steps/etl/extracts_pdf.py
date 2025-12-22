from zenml import step
from pathlib import Path
from typing import List
import logging
from datetime import datetime
from uuid import UUID
import re

import pytesseract
import pypdfium2 as pdfium
from pdfminer.high_level import extract_text

from llm_engineering.domain.documents import ArticleDocument

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
def extract_pdfs(pdf_dir: str = "data/pdfs") -> List[ArticleDocument]:
    logger.warning("exctraction of pdf started")

    pdf_dir = Path(pdf_dir)
    documents: List[ArticleDocument] = []

    for pdf_path in pdf_dir.glob("*.pdf"):
        logger.info(f"Processing PDF: {pdf_path.name}")

        pdf = pdfium.PdfDocument(str(pdf_path))
        try:
            for page_idx in range(len(pdf)):
                page_number = page_idx + 1

                # 1️⃣ Try digital extraction first
                text = extract_page_text_pdfminer(pdf_path, page_idx)
                extraction_method = "pdfminer"

                # 2️⃣ OCR fallback only if clearly insufficient
                if len(text.strip()) < 200:
                    text = extract_page_text_ocr(pdf, page_idx)
                    extraction_method = "ocr"

                # 3️⃣ Minimal cleanup (LOSSLESS)
                text = minimal_cleanup(text)

                if not text:
                    logger.warning(
                        f"Empty page {page_number} in {pdf_path.name}"
                    )
                    continue

                # 4️⃣ Build domain document (page-level knowledge unit)
                doc = ArticleDocument(
                    content={
                        "text": text,
                        "file_name": pdf_path.name,
                        "page_number": page_number,
                        "source": "official_gazette",
                        "extraction_method": extraction_method,
                    },
                    platform="nigerian_legislation",
                    author_id=FGN_AUTHOR_ID,
                    author_full_name="Federal Government of Nigeria",
                    link=f"{pdf_path.name}#page={page_number}",
                    created_at=datetime.utcnow(),
                )

                documents.append(doc)

        finally:
            # Guarantee pdfium cleanup even if something fails
            pdf.close()

    # -------------------------------------------------------------------------
    # Bulk insert (atomic)
    # -------------------------------------------------------------------------

    if documents:
        ArticleDocument.bulk_insert(documents)
        logger.info(f"Inserted {len(documents)} page-level documents")
    else:
        logger.warning("No documents extracted")

    return documents