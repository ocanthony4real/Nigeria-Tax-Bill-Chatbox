# steps/etl/extract_pdfs.py
from zenml import step
from pathlib import Path
import json
from typing import List
import logging

from llm_engineering.domain.documents import Document
from llm_engineering.domain.types import DataCategory
from llm_engineering.domain.documents import ArticleDocument

import pytesseract
from pdfminer.high_level import extract_text
from PIL import Image

import pypdfium2 as pdfium
import io
from uuid import UUID

logger = logging.getLogger(__name__)


def extract_text_from_pdfminer(pdf_path: Path) -> str:
    """Try to extract text normally using pdfminer."""
    try:
        text = extract_text(pdf_path)
        return text.strip()
    except Exception as e:
        logger.warning(f"pdfminer failed on {pdf_path.name}: {e}")
        return ""


def extract_text_from_ocr(pdf_path: Path) -> str:
    """
    Extract text from scanned PDFs using pypdfium2 + PIL + pytesseract.
    This mirrors the proven standalone test logic.
    """
    text_chunks = []

    try:
        pdf = pdfium.PdfDocument(str(pdf_path))

        for page_num, page in enumerate(pdf, start=1):
            try:
                # Render page at 300 DPI (same as your test)
                pil_image = page.render(scale=300 / 72).to_pil()

                text = pytesseract.image_to_string(pil_image)
                if text.strip():
                    text_chunks.append(text)

                page.close()

            except Exception as e:
                logger.warning(
                    f"OCR failed on page {page_num} of {pdf_path.name}: {e}"
                )

        pdf.close()

    except Exception as e:
        logger.error(
            f"OCR extraction failed entirely for {pdf_path.name}: {e}"
        )

    return "\n".join(text_chunks).strip()



@step(enable_cache=False)
def extract_pdfs(pdf_dir: str = "data/pdfs") -> List[Document]:
    """
    ETL Step: Extract text from all PDFs in a folder.
    Uses pdfminer for digital text and pytesseract for scanned text.
    """
    pdf_dir = Path(pdf_dir)
    documents = []

    if not pdf_dir.exists():
        logger.error(f"PDF directory not found: {pdf_dir.resolve()}")
        raise FileNotFoundError(f"{pdf_dir} does not exist")

    for pdf_path in pdf_dir.glob("*.pdf"):
        logger.info(f"Processing: {pdf_path.name}")

        # Try digital extraction first
        text = extract_text_from_pdfminer(pdf_path)

        # If text is too short, try OCR fallback
        if len(text.split()) < 30:
            logger.info(f"{pdf_path.name}: minimal text found, switching to OCR...")
            text = extract_text_from_ocr(pdf_path)

        if not text:
            logger.warning(f"No readable content found in {pdf_path.name}")
            continue


        FGN_AUTHOR_ID = UUID("11111111-1111-4444-8888-111111111111")
        doc = ArticleDocument(
            content={"text": text, "file_name": pdf_path.name, "source": "pdf"},
            platform="nigerian_gazette",
            author_id=FGN_AUTHOR_ID,
            author_full_name="Federal Government of Nigeria",
            link=str(pdf_path),
        )
        
        documents.append(doc)

    # if documents:
    #     inserted_ids = ArticleDocument.bulk_insert(documents)
    #     logger.info(f"Inserted {len(inserted_ids)} PDF documents into MongoDB with ids: {inserted_ids}")

    inserted_ids = ArticleDocument.bulk_insert(documents)
    logger.info(
        f"Inserted PDF documents into MongoDB with ids: {inserted_ids}"
    )

        
        
    # Save output to artifact file
    output_path = Path("data/artifacts/raw_pdf_documents.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump([doc.model_dump() for doc in documents], f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Saved {len(documents)} extracted documents to {output_path}")
    return documents
