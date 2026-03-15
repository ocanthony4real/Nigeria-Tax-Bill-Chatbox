"""
Document structure annotation step.

Annotates extracted tax bill pages with hierarchical structure metadata
(chapters, parts, and sections) using regex pattern matching.
"""

from zenml import step
import logging
import re
from typing import List

from llm_engineering.infrastructure.db.mongo import connection
from llm_engineering.settings import settings
from llm_engineering.domain.documents import TaxBillDocument

logger = logging.getLogger(__name__)

db = connection.get_database(settings.DATABASE_NAME)
collection = db[TaxBillDocument.get_collection_name()]

CHAPTER_RE = re.compile(r"^\s*CHAPTER\s+[A-Z0-9IVXLC]+", re.IGNORECASE)
PART_RE = re.compile(r"^\s*PART\s+[A-Z0-9IVXLC]+", re.IGNORECASE)
SECTION_RE = re.compile(r"\bSection\s+(\d+[A-Z]?)", re.IGNORECASE)

@step(enable_cache=False)
def annotate_document_structure(_: List[TaxBillDocument] | None = None):
    logger.info("Starting structural annotation")

    current_chapter = None
    current_part = None

    cursor = collection.find({}).sort([
        ("content.file_name", 1),
        ("content.page_number", 1),
    ])

    updated = 0

    for doc in cursor:
        text = doc.get("content", {}).get("text", "")
        if not text:
            continue

        lines = [l.strip() for l in text.splitlines() if l.strip()]

        for line in lines[:10]:
            if CHAPTER_RE.match(line):
                current_chapter = line
            if PART_RE.match(line):
                current_part = line

        sections = list(set(SECTION_RE.findall(text)))

        collection.update_one(
            {"_id": doc["_id"]},   # UUID string
            {"$set": {
                "content.chapter": current_chapter,
                "content.part": current_part,
                "content.sections": sections,
            }}
        )

        updated += 1

    logger.info(f"Annotated {updated} pages")
