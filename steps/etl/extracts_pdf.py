from zenml import step
from pathlib import Path
import json
from typing import List
import logging
from datetime import datetime


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


def extract_page_text_pdfminer(pdf_path: Path, page_number: int) -> str:
    try:
        text = extract_text(pdf_path, page_numbers=[page_number])
        return text.strip()
    except Exception:
        return ""


def extract_page_text_ocr(pdf: pdfium.PdfDocument, page_number: int) -> str:
    page = pdf[page_number]
    pil_image = page.render(scale=300 / 72).to_pil()
    text = pytesseract.image_to_string(pil_image)
    page.close()
    return text.strip()


@step(enable_cache=False)
def extract_pdfs(pdf_dir: str = "data/pdfs") -> List[ArticleDocument]:
    pdf_dir = Path(pdf_dir)
    documents: List[ArticleDocument] = []

    for pdf_path in pdf_dir.glob("*.pdf"):
        logger.info(f"Processing {pdf_path.name}")
        pdf = pdfium.PdfDocument(str(pdf_path))

        for page_idx in range(len(pdf)):
            page_number = page_idx + 1

            text = extract_page_text_pdfminer(pdf_path, page_idx)
            method = "pdfminer"

            if len(text) < 200:
                text = extract_page_text_ocr(pdf, page_idx)
                method = "ocr"

            if not text:
                logger.warning(f"Empty page {page_number} in {pdf_path.name}")
                continue


            FGN_AUTHOR_ID = UUID("11111111-1111-4444-8888-111111111111")

            doc = ArticleDocument(
                content={
                    "text": text,
                    "file_name": pdf_path.name,
                    "page_number": page_number,
                    "source": "official_gazette",
                },
                platform="nigerian_legislation",
                author_id=FGN_AUTHOR_ID,
                author_full_name="Federal Government of Nigeria",
                link=f"{pdf_path.name}#page={page_number}",
                created_at=datetime.utcnow(),
            )


            documents.append(doc)

        pdf.close()

    inserted_ids = ArticleDocument.bulk_insert(documents)
    logger.info(f"Inserted page-level documents")

    return documents