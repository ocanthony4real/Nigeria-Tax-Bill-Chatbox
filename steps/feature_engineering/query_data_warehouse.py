from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Annotated, List
from uuid import UUID

from loguru import logger
from zenml import get_step_context, step

from llm_engineering.domain.base.nosql import NoSQLBaseDocument
# from llm_engineering.domain.documents.tax_bill import TaxBillDocument
from llm_engineering.domain.documents import TaxBillDocument
from llm_engineering.domain.documents import TaxBillPageDocument



FGN_AUTHOR_ID = UUID("11111111-1111-4444-8888-111111111111")
FGN_AUTHOR_NAME = "Federal Government of Nigeria"
PLATFORM = "nigerian_legislation"


@step(enable_cache=False)
def query_data_warehouse(
    pdf_names: list[str],
) -> Annotated[List[TaxBillDocument], "raw_documents"]:
    """
    Query the data warehouse for Nigerian tax bill PDFs and return
    normalized TaxBillDocument objects.
    """

    logger.info(f"Querying warehouse for {len(pdf_names)} tax bill PDFs")

    documents: list[TaxBillDocument] = []

    with ThreadPoolExecutor() as executor:
        future_to_pdf = {
            executor.submit(fetch_pdf_pages, pdf_name): pdf_name
            for pdf_name in pdf_names
        }

        for future in as_completed(future_to_pdf):
            pdf_name = future_to_pdf[future]

            try:
                pages = future.result()
                bills = normalize_pages_to_tax_bills(pages, pdf_name)
                documents.extend(bills)

                logger.info(
                    f"Processed {len(bills)} pages from PDF: {pdf_name}"
                )

            except Exception:
                logger.exception(f"Failed processing PDF: {pdf_name}")

    # ---- FAIL FAST (NO SILENT PIPELINES) ----

    if not documents:
        raise RuntimeError(
            "Query step completed successfully but produced zero documents. "
            "Check PDF names or warehouse contents."
        )

    # ---- METADATA (ZenML observability) ----
    step_context = get_step_context()
    step_context.add_output_metadata(
        output_name="raw_documents",
        metadata=build_metadata(documents),
    )
    
    return documents



def fetch_pdf_pages(pdf_name: str) -> list[TaxBillPageDocument]:
    """
    Fetch all stored pages belonging to a tax bill PDF.
    """
    pages = TaxBillPageDocument.bulk_find_by_pdf(pdf_name)

    if not pages:
        raise ValueError(f"No pages found for PDF: {pdf_name}")

    return pages


def normalize_pages_to_tax_bills(
    pages: list[TaxBillPageDocument],
    pdf_name: str,
) -> list[TaxBillDocument]:
    """
    Normalize storage-level page documents into domain-level tax bill documents.
    """

    bills: list[TaxBillDocument] = []

    for page in pages:
        content = page.content

        bills.append(
            TaxBillDocument(
                content={
                    "text": content.get("text", ""),
                    "source": content.get("source", "official_gazette"),
                    "extraction_method": content.get(
                        "extraction_method", "ocr"
                    ),
                },
                platform=PLATFORM,
                author_id=FGN_AUTHOR_ID,
                author_full_name=FGN_AUTHOR_NAME,
                file_name=pdf_name,
                page_number=content.get("page_number", 1),
                chapter=content.get("chapter"),
                part=content.get("part"),
                sections=content.get("sections", []),
                link=f"{pdf_name}#page={content.get('page_number', 1)}",
            )
        )

    return bills


def build_metadata(documents: list[TaxBillDocument]) -> dict:
    """
    Build structured metadata for ZenML observability.
    """

    metadata = {
        "num_documents": len(documents),
        "pdfs": {},
    }

    for doc in documents:
        metadata["pdfs"].setdefault(
            doc.file_name, {"num_pages": 0}
        )
        metadata["pdfs"][doc.file_name]["num_pages"] += 1

    return metadata
