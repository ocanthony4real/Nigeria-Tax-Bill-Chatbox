from loguru import logger
from qdrant_client.http import exceptions
from typing_extensions import Annotated
from zenml import step

from llm_engineering.domain.base.nosql import NoSQLBaseDocument
from llm_engineering.domain.cleaned_documents import (
    CleanedDocument,
    TaxBillCleanedDocument,
)


@step(enable_cache=False)
def query_feature_store() -> Annotated[list[NoSQLBaseDocument], "queried_cleaned_documents"]:
    """
    Fetch all cleaned tax bill documents from the feature store.
    """
    logger.info("Querying feature store for cleaned tax bill documents.")

    cleaned_documents = _fetch_cleaned_tax_bills()

    logger.info(
        "Feature store query completed.",
        num_documents=len(cleaned_documents),
    )

    return cleaned_documents


def _fetch_cleaned_tax_bills(limit: int = 100) -> list[CleanedDocument]:
    """
    Fetch all cleaned tax bill documents using pagination.
    """
    try:
        cleaned_documents, next_offset = TaxBillCleanedDocument.bulk_find(limit=limit)
    except exceptions.UnexpectedResponse:
        logger.exception("Failed to fetch cleaned tax bill documents.")
        return []

    while next_offset:
        documents, next_offset = TaxBillCleanedDocument.bulk_find(
            limit=limit,
            offset=next_offset,
        )
        cleaned_documents.extend(documents)

    return cleaned_documents
