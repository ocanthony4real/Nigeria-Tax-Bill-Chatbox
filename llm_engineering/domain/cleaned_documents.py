from abc import ABC
from typing import Optional

from pydantic import UUID4

from .base import VectorBaseDocument
from .types import DataCategory


class CleanedDocument(VectorBaseDocument, ABC):
    """
    Cleaned, normalized version of a Document.
    Not vector-indexed.
    """

    content: str
    platform: str
    author_id: UUID4
    author_full_name: str


class TaxBillCleanedDocument(CleanedDocument):
    """
    Cleaned and normalized representation of a Nigerian tax bill.
    """

    file_name: str
    page_number: int

    chapter: Optional[str] = None
    part: Optional[str] = None
    section: list[str] = []

    class Config:
        name = "cleaned_tax_bills"
        category = DataCategory.TAX_BILLS
        use_vector_index = False
