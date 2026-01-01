import hashlib
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import uuid4

from llm_engineering.domain.chunks import Chunk, TaxBillChunk
from llm_engineering.domain.cleaned_documents import CleanedDocument, TaxBillCleanedDocument
#from llm_engineering.domain.chunking.handlers import ChunkingDataHandler
#from llm_engineering.domain.chunking.operations import chunk_text
from .operations import chunk_text


CleanedDocumentT = TypeVar("CleanedDocumentT", bound=CleanedDocument)
ChunkT = TypeVar("ChunkT", bound=Chunk)


class ChunkingDataHandler(ABC, Generic[CleanedDocumentT, ChunkT]):
    """
    Abstract class for all Chunking data handlers.
    All data transformations logic for the chunking step is done here
    """

    @property
    def metadata(self) -> dict:
        return {
            "chunk_size": 500,
            "chunk_overlap": 50,
        }

    @abstractmethod
    def chunk(self, data_model: CleanedDocumentT) -> list[ChunkT]:
        pass


class TaxBillChunkingHandler(
    ChunkingDataHandler[TaxBillCleanedDocument, TaxBillChunk]
):
    """
    Chunking handler for Nigerian tax bills.
    """

    @property
    def metadata(self) -> dict:
        return {
            "chunk_size": 800,
            "chunk_overlap": 100,
        }

    def chunk(self, data_model: TaxBillCleanedDocument) -> list[TaxBillChunk]:
        data_models_list: list[TaxBillChunk] = []

        cleaned_content = data_model.content

        chunks = chunk_text(
            cleaned_content,
            chunk_size=self.metadata["chunk_size"],
            chunk_overlap=self.metadata["chunk_overlap"],
        )

        for idx, chunk in enumerate(chunks, start=1):
            model = TaxBillChunk(
                id=uuid4(),
                content=chunk,
                platform=data_model.platform,
                document_id=data_model.id,
                author_id=data_model.author_id,
                author_full_name=data_model.author_full_name,
                file_name=data_model.file_name,
                page_number=data_model.page_number,
                chapter=data_model.chapter,
                part=data_model.part,
                section=None,
                metadata={
                    **self.metadata,
                    "chunk_index": idx,
                    "total_chunks": len(chunks),
                },
            )

            data_models_list.append(model)

        return data_models_list
