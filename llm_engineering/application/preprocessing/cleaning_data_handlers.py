from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from llm_engineering.domain.cleaned_documents import (
    CleanedDocument,
    TaxBillCleanedDocument,
)
from llm_engineering.domain.documents import (
    Document,
    TaxBillDocument,
)

from .operations import clean_text

DocumentT = TypeVar("DocumentT", bound=Document)
CleanedDocumentT = TypeVar("CleanedDocumentT", bound=CleanedDocument)


class CleaningDataHandler(ABC, Generic[DocumentT, CleanedDocumentT]):
    """
    Abstract class for all cleaning data handlers.
    All data transformations logic for the cleaning step is done here
    """

    @abstractmethod
    def clean(self, data_model: DocumentT) -> CleanedDocumentT:
        pass


class TaxBillCleaningHandler(CleaningDataHandler[TaxBillDocument, TaxBillCleanedDocument]):
    """
    Cleaning handler for Nigerian tax bills.
    """

    def clean(self, data_model: TaxBillDocument) -> TaxBillCleanedDocument:
        # Collect valid content fields
        valid_content = [value for value in data_model.content.values() if value]

        cleaned_text = clean_text(" #### ".join(valid_content))

        return TaxBillCleanedDocument(
            id=data_model.id,
            content=cleaned_text,
            platform=data_model.platform,
            author_id=data_model.author_id,
            author_full_name=data_model.author_full_name,
            file_name=data_model.file_name,
            chapter=data_model.chapter,
            part=data_model.part,
            sections=data_model.sections,
            page_number=data_model.page_number,

        )
