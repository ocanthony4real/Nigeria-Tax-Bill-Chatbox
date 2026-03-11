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
            # Try to get reference if available (for TaxBillEmbeddedChunk)
            reference = getattr(chunk, 'get_reference', lambda: f"pg. {getattr(chunk, 'page_number', 'N/A')}")()
            context += f"""
Chunk {i + 1}:
Reference: {reference}
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

    # Hierarchical structure metadata
    chapter: Optional[str] = None       # e.g., "Chapter 1", "Chapter 2"
    part: Optional[str] = None          # e.g., "Part I", "Part IV"
    section: Optional[str] = None       # e.g., "20" (from "20. Deductions allowed")
    subsection: Optional[str] = None    # e.g., "(1)", "(1)(a)", "(2)(b)(ii)"

    class Config:
        name = "embedded_tax_bill_chunks"
        category = DataCategory.TAX_BILLS
        use_vector_index = True

    def get_reference(self) -> str:
        """Build a human-readable reference string for this chunk.
        Format: Section X, Subsection Y (p. Z)
        """
        parts = []
        if self.section:
            parts.append(f"Section {self.section}")
        if self.subsection:
            parts.append(f"Subsection {self.subsection}")

        # Always include page number at the end
        ref = ", ".join(parts) if parts else ""
        if ref:
            return f"{ref} (p. {self.page_number})"
        else:
            return f"pg. {self.page_number}"