# pipelines/pdf_data_etl.py
from zenml import pipeline
from steps.etl.extracts_pdf import extract_pdfs


@pipeline
def pdf_data_etl(pdf_dir: str):
    """
    ZenML pipeline for extracting text from Nigerian law PDFs.
    All metadata is extracted from the PDFs themselves.
    """
    extracted_docs = extract_pdfs(pdf_dir=pdf_dir)
    return extracted_docs
