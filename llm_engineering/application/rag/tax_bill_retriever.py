"""
Dedicated retriever for Nigeria Tax Bill documents.

This retriever searches the embedded_tax_bill_chunks collection in Qdrant
and returns chunks with full structural metadata (chapter, part, section, subsection).
"""

from typing import List, Optional

from loguru import logger

# opik is optional - used for tracing
try:
    import opik
    HAS_OPIK = True
except ImportError:
    HAS_OPIK = False

    # Create a no-op decorator
    class opik:
        @staticmethod
        def track(name=None):
            def decorator(func):
                return func
            return decorator

from llm_engineering.application.preprocessing.dispatchers import EmbeddingDispatcher
from llm_engineering.domain.embedded_chunks import TaxBillEmbeddedChunk
from llm_engineering.domain.queries import Query

from .reranking import Reranker


class TaxBillRetriever:
    """
    Retriever specialized for Nigeria Tax Bill documents.

    Features:
    - Searches only the tax bill chunks collection
    - Preserves structural metadata (chapter, part, section, subsection)
    - Reranks results for better precision using CrossEncoder
    """

    def __init__(self, mock: bool = False) -> None:
        self._reranker = Reranker(mock=mock)

    @opik.track(name="TaxBillRetriever.search")
    def search(
        self,
        query: str,
        k: int = 10,
    ) -> List[TaxBillEmbeddedChunk]:
        """
        Search for relevant tax bill chunks.

        Args:
            query: The user's question
            k: Number of chunks to return

        Returns:
            List of TaxBillEmbeddedChunk with structural metadata
        """
        query_model = Query.from_str(query)

        # Search with embedding similarity (retrieve more for reranking)
        chunks = self._search_tax_bills(query_model, limit=k * 3)
        logger.info(f"Retrieved {len(chunks)} tax bill chunks.")

        # Rerank and return top k
        if len(chunks) > 0:
            reranked_chunks = self._rerank(query, chunks, keep_top_k=k)
        else:
            reranked_chunks = []

        return reranked_chunks

    def _search_tax_bills(
        self, query: Query, limit: int = 10
    ) -> List[TaxBillEmbeddedChunk]:
        """
        Perform vector search on the tax bill chunks collection.
        """
        # Embed the query
        embedded_query = EmbeddingDispatcher.dispatch(query)

        # Search Qdrant
        chunks = TaxBillEmbeddedChunk.search(
            query_vector=embedded_query.embedding,
            limit=limit,
        )

        return chunks

    def _rerank(
        self,
        query: str,
        chunks: List[TaxBillEmbeddedChunk],
        keep_top_k: int,
    ) -> List[TaxBillEmbeddedChunk]:
        """
        Rerank chunks using cross-encoder for better precision.
        """
        if isinstance(query, str):
            query_model = Query.from_str(query)
        else:
            query_model = query

        reranked = self._reranker.generate(
            query=query_model,
            chunks=chunks,
            keep_top_k=keep_top_k,
        )

        logger.info(f"Reranked to top {len(reranked)} tax bill chunks.")

        return reranked

    @staticmethod
    def extract_references(chunks: List[TaxBillEmbeddedChunk]) -> List[str]:
        """
        Extract human-readable references from chunks.

        Returns:
            List of reference strings like "Chapter 2, Part 4, Section 20, (1)"
        """
        references = []
        for chunk in chunks:
            ref = chunk.get_reference()
            if ref not in references:
                references.append(ref)
        return references

    @staticmethod
    def build_sources(chunks: List[TaxBillEmbeddedChunk]) -> List[dict]:
        """
        Build detailed source information for each chunk.

        Returns:
            List of source dictionaries with full metadata
        """
        sources = []
        for chunk in chunks:
            sources.append({
                "reference": chunk.get_reference(),
                "page": chunk.page_number,
                "chapter": chunk.chapter,
                "part": chunk.part,
                "section": chunk.section,
                "subsection": chunk.subsection,
                "file_name": chunk.file_name,
                "snippet": chunk.content[:300] + "..." if len(chunk.content) > 300 else chunk.content,
            })
        return sources
