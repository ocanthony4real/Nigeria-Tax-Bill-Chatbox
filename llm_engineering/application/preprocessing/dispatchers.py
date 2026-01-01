from loguru import logger

from llm_engineering.domain.base import NoSQLBaseDocument, VectorBaseDocument
from llm_engineering.domain.types import DataCategory


from .chunking_data_handlers import (
    ChunkingDataHandler,
    TaxBillChunkingHandler,
)

from .cleaning_data_handlers import (
    CleaningDataHandler,
    TaxBillCleaningHandler,
)

from .embedding_data_handlers import (
    EmbeddingDataHandler,
    QueryEmbeddingHandler,
    TaxBillEmbeddingHandler,
)


class CleaningHandlerFactory:
    @staticmethod
    def create_handler(data_category: DataCategory) -> CleaningDataHandler:
        if data_category == DataCategory.TAX_BILLS:
            return TaxBillCleaningHandler()
        else:
            raise ValueError(f"Unsupported data category for cleaning: {data_category}")


class CleaningDispatcher:
    factory = CleaningHandlerFactory()

    @classmethod
    def dispatch(cls, data_model: NoSQLBaseDocument) -> VectorBaseDocument:
        data_category = DataCategory(data_model.get_collection_name())

        handler = cls.factory.create_handler(data_category)
        clean_model = handler.clean(data_model)

        logger.info(
            "Document cleaned successfully.",
            data_category=data_category,
            cleaned_content_len=len(clean_model.content),
        )

        return clean_model


class ChunkingHandlerFactory:
    @staticmethod
    def create_handler(data_category: DataCategory) -> ChunkingDataHandler:
        if data_category == DataCategory.TAX_BILLS:
            return TaxBillChunkingHandler()
        else:
            raise ValueError(f"Unsupported data category for chunking: {data_category}")


class ChunkingDispatcher:
    factory = ChunkingHandlerFactory()

    @classmethod
    def dispatch(cls, data_model: VectorBaseDocument) -> list[VectorBaseDocument]:
        data_category = data_model.get_category()

        # logger.info(
        #     f"Chunking input size: {len(data_model.content)} characters"
        # )
        handler = cls.factory.create_handler(data_category)
        chunk_models = handler.chunk(data_model)

        # logger.info(
        #     f"Document chunked successfully | chunks={len(chunk_models)} | category={data_category}",
        #     num=len(chunk_models),
        #     data_category=data_category,
        # )

        return chunk_models


class EmbeddingHandlerFactory:
    @staticmethod
    def create_handler(data_category: DataCategory) -> EmbeddingDataHandler:
        if data_category == DataCategory.QUERIES:
            return QueryEmbeddingHandler()
        elif data_category == DataCategory.TAX_BILLS:
            return TaxBillEmbeddingHandler()
        else:
            raise ValueError(f"Unsupported data category for embedding: {data_category}")


class EmbeddingDispatcher:
    factory = EmbeddingHandlerFactory()

    @classmethod
    def dispatch(
        cls, data_model: VectorBaseDocument | list[VectorBaseDocument]
    ) -> VectorBaseDocument | list[VectorBaseDocument]:

        is_list = isinstance(data_model, list)
        if not is_list:
            data_model = [data_model]

        if len(data_model) == 0:
            return []

        data_category = data_model[0].get_category()

        assert all(
            model.get_category() == data_category for model in data_model
        ), "All data models must have the same category."

        handler = cls.factory.create_handler(data_category)
        embedded_models = handler.embed_batch(data_model)

        if not is_list:
            embedded_models = embedded_models[0]

        # logger.info(
        #     "Data embedded successfully.",
        #     data_category=data_category,
        # )

        return embedded_models