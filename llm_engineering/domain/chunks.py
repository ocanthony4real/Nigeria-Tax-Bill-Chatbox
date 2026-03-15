"""
Chunk domain models for document segmentation.

Defines chunk structures used to represent segmented portions
of documents for embedding and retrieval.
"""

from abc import ABC
from typing import Optional

from pydantic import UUID4, Field

from llm_engineering.domain.base import VectorBaseDocument
from llm_engineering.domain.types import DataCategory


class Chunk(VectorBaseDocument, ABC):
    """
    Vector-level representation of a slice of a Document.
    """

    content: str
    platform: str

    document_id: UUID4
    author_id: UUID4
    author_full_name: str

    metadata: dict = Field(default_factory=dict)


class TaxBillChunk(Chunk):
    """
    Chunk representation of a Nigerian tax bill section or paragraph.
    """

    file_name: str
    page_number: int

    chapter: Optional[str] = None
    part: Optional[str] = None
    section: Optional[str] = None

    class Config:
        category = DataCategory.TAX_BILLS