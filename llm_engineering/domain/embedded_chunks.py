from abc import ABC
from typing import Optional

from pydantic import UUID4, Field

from llm_engineering.domain.types import DataCategory

from .base import VectorBaseDocument


class EmbeddedChunk(VectorBaseDocument, ABC):
    """
    Vector-indexed representation of a Chunk.
    """

    content: str
    embedding: list[float] | None

    platform: str
    document_id: UUID4
    author_id: UUID4
    author_full_name: str

    metadata: dict = Field(default_factory=dict)

    @classmethod
    def to_context(cls, chunks: list["EmbeddedChunk"]) -> str:
        """
        Convert retrieved chunks into an LLM-readable context block.
        """
        context = ""
        for i, chunk in enumerate(chunks):
            context += f"""
Chunk {i + 1}:
Platform: {chunk.platform}
Author: {chunk.author_full_name}
Content:
{chunk.content}

"""
        return context

class TaxBillEmbeddedChunk(EmbeddedChunk):
    """
    Embedded, vector-indexed chunk of a Nigerian tax bill.
    """

    file_name: str
    page_number: int

    chapter: Optional[str] = None
    part: Optional[str] = None
    section: Optional[str] = None

    class Config:
        name = "embedded_tax_bill_chunks"
        category = DataCategory.TAX_BILLS
        use_vector_index = True