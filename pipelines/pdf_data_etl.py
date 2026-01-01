from zenml import pipeline

from steps.etl.extracts_pdf import extract_pdfs
from steps.etl.annotate_structure import annotate_document_structure


@pipeline
def pdf_data_etl(pdf_dir: str):
    """
    ZenML pipeline for extracting and structurally annotating Nigerian law PDFs.

    Step 1: Extract page-level text into MongoDB
    Step 2: Annotate chapters, parts, and sections
    """
    extracted_docs = extract_pdfs(pdf_dir=pdf_dir)

    annotated_docs = annotate_document_structure(extracted_docs)

    return annotated_docs
