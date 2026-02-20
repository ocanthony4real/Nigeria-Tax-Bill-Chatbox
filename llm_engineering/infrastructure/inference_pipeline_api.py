from typing import List, Optional

import opik
from fastapi import FastAPI, HTTPException
from opik import opik_context
from pydantic import BaseModel

from llm_engineering import settings
from llm_engineering.application.rag.retriever import ContextRetriever
from llm_engineering.application.rag.tax_bill_retriever import TaxBillRetriever
from llm_engineering.application.utils import misc
from llm_engineering.domain.embedded_chunks import EmbeddedChunk, TaxBillEmbeddedChunk
from llm_engineering.infrastructure.opik_utils import configure_opik
from llm_engineering.model.inference import InferenceExecutor, LLMInferenceSagemakerEndpoint, TAX_BILL_PROMPT

configure_opik()

app = FastAPI()


# =============================================================================
# Request/Response Models
# =============================================================================

class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    answer: str


class TaxBillQueryRequest(BaseModel):
    query: str
    k: int = 10  # Number of chunks to retrieve (increased for comprehensive answers)


class TaxBillSource(BaseModel):
    reference: str
    page: int
    chapter: Optional[str] = None
    part: Optional[str] = None
    section: Optional[str] = None
    subsection: Optional[str] = None
    file_name: str
    snippet: str


class TaxBillQueryResponse(BaseModel):
    answer: str
    references: List[str]
    sources: List[TaxBillSource]


@opik.track
def call_llm_service(query: str, context: str | None) -> str:
    llm = LLMInferenceSagemakerEndpoint(
        endpoint_name=settings.SAGEMAKER_ENDPOINT_INFERENCE, inference_component_name=None
    )
    answer = InferenceExecutor(llm, query, context).execute()

    return answer


@opik.track
def rag(query: str) -> str:
    retriever = ContextRetriever(mock=False)
    documents = retriever.search(query, k=8)  # Increased for more context
    context = EmbeddedChunk.to_context(documents)

    answer = call_llm_service(query, context)

    opik_context.update_current_trace(
        tags=["rag"],
        metadata={
            "model_id": settings.HF_MODEL_ID,
            "embedding_model_id": settings.TEXT_EMBEDDING_MODEL_ID,
            "temperature": settings.TEMPERATURE_INFERENCE,
            "query_tokens": misc.compute_num_tokens(query),
            "context_tokens": misc.compute_num_tokens(context),
            "answer_tokens": misc.compute_num_tokens(answer),
        },
    )

    return answer


@app.post("/rag", response_model=QueryResponse)
async def rag_endpoint(request: QueryRequest):
    try:
        answer = rag(query=request.query)

        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


# =============================================================================
# Nigeria Tax Bill RAG - With References
# =============================================================================

@opik.track
def call_tax_bill_llm(query: str, context: str) -> str:
    """
    Call LLM with the specialized tax bill prompt that requires citations.
    """
    llm = LLMInferenceSagemakerEndpoint(
        endpoint_name=settings.SAGEMAKER_ENDPOINT_INFERENCE,
        inference_component_name=None,
    )
    answer = InferenceExecutor(llm, query, context, prompt=TAX_BILL_PROMPT).execute()

    return answer


@opik.track
def tax_bill_rag(query: str, k: int = 10) -> dict:
    """
    RAG pipeline specifically for Nigeria Tax Bill queries.

    Returns answer with references and detailed source information.
    """
    # 1. Retrieve relevant chunks from tax bill collection
    retriever = TaxBillRetriever(mock=False)
    chunks = retriever.search(query, k=k)

    if not chunks:
        return {
            "answer": "I couldn't find relevant information in the Nigeria Tax Act to answer your question.",
            "references": [],
            "sources": [],
        }

    # 2. Build context with references included
    context = TaxBillEmbeddedChunk.to_context(chunks)

    # 3. Extract references for the response
    references = TaxBillRetriever.extract_references(chunks)

    # 4. Build detailed source information
    sources = TaxBillRetriever.build_sources(chunks)

    # 5. Call LLM with tax bill prompt
    answer = call_tax_bill_llm(query, context)

    # 6. Log metrics
    opik_context.update_current_trace(
        tags=["tax_bill_rag"],
        metadata={
            "model_id": settings.HF_MODEL_ID,
            "embedding_model_id": settings.TEXT_EMBEDDING_MODEL_ID,
            "temperature": settings.TEMPERATURE_INFERENCE,
            "query_tokens": misc.compute_num_tokens(query),
            "context_tokens": misc.compute_num_tokens(context),
            "answer_tokens": misc.compute_num_tokens(answer),
            "num_chunks_retrieved": len(chunks),
            "references": references,
        },
    )

    return {
        "answer": answer,
        "references": references,
        "sources": sources,
    }


@app.post("/tax-query", response_model=TaxBillQueryResponse)
async def tax_bill_query_endpoint(request: TaxBillQueryRequest):
    """
    Query the Nigeria Tax Act with automatic reference generation.

    Returns:
        - answer: The LLM's response to the query
        - references: List of section references cited
        - sources: Detailed source information for each chunk
    """
    try:
        result = tax_bill_rag(query=request.query, k=request.k)

        return TaxBillQueryResponse(
            answer=result["answer"],
            references=result["references"],
            sources=[TaxBillSource(**src) for src in result["sources"]],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
