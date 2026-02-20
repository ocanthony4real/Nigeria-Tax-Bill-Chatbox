"""
Context Retriever for Nigeria Tax Bill Chatbot.

This retriever searches the TaxBillEmbeddedChunk collection in Qdrant
and returns relevant chunks for answering tax-related questions.
"""

import concurrent.futures

import opik
from loguru import logger

from llm_engineering.application import utils
from llm_engineering.application.preprocessing.dispatchers import EmbeddingDispatcher
from llm_engineering.domain.embedded_chunks import (
    EmbeddedChunk,
    TaxBillEmbeddedChunk,
)
from llm_engineering.domain.queries import EmbeddedQuery, Query

from .query_expanison import QueryExpansion
from .reranking import Reranker
from .self_query import SelfQuery


class ContextRetriever:
    """
    Retriever for Nigeria Tax Bill documents.

    Searches the embedded tax bill chunks and returns relevant context
    for answering user questions about Nigerian tax law.
    """

    def __init__(self, mock: bool = False) -> None:
        self._query_expander = QueryExpansion(mock=mock)
        self._metadata_extractor = SelfQuery(mock=mock)
        self._reranker = Reranker(mock=mock)

    @opik.track(name="ContextRetriever.search")
    def search(
        self,
        query: str,
        k: int = 10,  # Increased for comprehensive context
        expand_to_n_queries: int = 5,  # Increased for better recall
    ) -> list[TaxBillEmbeddedChunk]:
        query_model = Query.from_str(query)

        # Expand query for better recall
        n_generated_queries = self._query_expander.generate(query_model, expand_to_n=expand_to_n_queries)
        logger.info(
            f"Successfully generated {len(n_generated_queries)} search queries.",
        )

        # Search with all query variations in parallel
        with concurrent.futures.ThreadPoolExecutor() as executor:
            search_tasks = [executor.submit(self._search, _query_model, k) for _query_model in n_generated_queries]

            n_k_documents = [task.result() for task in concurrent.futures.as_completed(search_tasks)]
            n_k_documents = utils.misc.flatten(n_k_documents)
            n_k_documents = list(set(n_k_documents))

        logger.info(f"{len(n_k_documents)} tax bill chunks retrieved successfully")

        if len(n_k_documents) > 0:
            k_documents = self.rerank(query, chunks=n_k_documents, keep_top_k=k)
        else:
            k_documents = []

        return k_documents

    def _search(self, query: Query, k: int = 5) -> list[TaxBillEmbeddedChunk]:
        """Search the tax bill chunks collection."""

        embedded_query: EmbeddedQuery = EmbeddingDispatcher.dispatch(query)

        # Search only the tax bill collection
        tax_bill_chunks = TaxBillEmbeddedChunk.search(
            query_vector=embedded_query.embedding,
            limit=k,
        )

        return tax_bill_chunks

    def rerank(self, query: str | Query, chunks: list[EmbeddedChunk], keep_top_k: int) -> list[EmbeddedChunk]:
        if isinstance(query, str):
            query = Query.from_str(query)

        reranked_documents = self._reranker.generate(query=query, chunks=chunks, keep_top_k=keep_top_k)

        logger.info(f"{len(reranked_documents)} documents reranked successfully.")

        return reranked_documents
