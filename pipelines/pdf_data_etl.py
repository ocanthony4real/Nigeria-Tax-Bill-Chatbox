
# from zenml import pipeline
# from steps.etl.extracts_pdf import extract_pdfs


# @pipeline
# def pdf_data_etl(pdf_dir: str):
#     """
#     ZenML pipeline for extracting text from Nigerian law PDFs.
#     All metadata is extracted from the PDFs themselves.
#     """
#     extracted_docs = extract_pdfs(pdf_dir=pdf_dir)
#     return extracted_docs


from zenml import pipeline

from steps.etl.extracts_pdf import extract_pdfs
from steps.etl.annotate_structure import annotate_document_structure


@pipeline
def pdf_data_etl(pdf_dir: str):
    """
    ZenML pipeline for extracting and structurally annotating Nigerian law PDFs.

    Step 1: Extract page-level text into MongoDB
    Step 2: Annotate chapters, parts, and sections in-place
    """
    extracted_docs = extract_pdfs(pdf_dir=pdf_dir)
    annotate_document_structure(extracted_docs)
