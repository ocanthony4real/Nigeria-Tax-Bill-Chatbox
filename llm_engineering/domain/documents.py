"""
Document domain models for tax bill storage and representation.

Defines the document structures used for storing and processing
Nigerian tax bill pages extracted from PDF documents.
"""

from abc import ABC
from typing import Optional, List

from pydantic import Field, UUID4

from .base import NoSQLBaseDocument
from .types import DataCategory


class Document(NoSQLBaseDocument, ABC):
    content: dict
    platform: str
    author_id: UUID4 = Field(alias="author_id")
    author_full_name: str = Field(alias="file_name")

class TaxBillPageDocument(NoSQLBaseDocument):
    """
    Represents a single stored page of a Nigerian tax bill PDF.
    This is a storage-level document.
    """

    content: dict

    class Settings:
        name = "tax_bills"

    @classmethod
    def bulk_find_by_pdf(cls, file_name: str) -> list["TaxBillPageDocument"]:
        return cls.bulk_find(file_name=file_name)
    
class TaxBillDocument(Document):
    """
    Domain-level representation of a Nigerian tax bill page.
    """

    file_name: str
    page_number: int
    link: str

    content: dict
    platform: str
    author_id: UUID4
    author_full_name: str

    chapter: Optional[str] = None
    part: Optional[str] = None
    sections: List[str] = []

    class Settings:
        name = DataCategory.TAX_BILLS