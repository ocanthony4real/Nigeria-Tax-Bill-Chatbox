"""
Gradio Chat UI for Nigeria Tax Bill Chatbot.

This provides a simple web interface for users to ask questions
about the Nigeria Tax Act 2025 and get answers with citations.
"""

import uuid
import traceback
from datetime import datetime

import gradio as gr
from loguru import logger

from llm_engineering.application.rag.tax_bill_retriever import TaxBillRetriever
from llm_engineering.domain.embedded_chunks import TaxBillEmbeddedChunk
from llm_engineering.infrastructure.opik_utils import configure_opik
from llm_engineering.model.inference import InferenceExecutor, LLMInferenceSagemakerEndpoint, TAX_BILL_PROMPT
from llm_engineering.settings import settings

# Initialize components
configure_opik()
retriever = TaxBillRetriever(mock=False)


# =============================================================================
# Secure Error Handling
# =============================================================================

class SecureErrorHandler:
    """
    Handles errors securely by:
    - Logging full details internally with unique error IDs
    - Returning only generic messages to users
    - Never exposing stack traces, file paths, or system details
    """

    # Generic user-facing error messages
    ERROR_MESSAGES = {
        "retrieval": "We're having trouble searching the database. Please try again in a moment.",
        "inference": "The AI service is temporarily unavailable. Please try again shortly.",
        "connection": "We're experiencing connectivity issues. Please try again in a moment.",
        "validation": "There was an issue processing your request. Please rephrase your question.",
        "general": "Something went wrong. Please try again.",
    }

    @classmethod
    def handle_error(cls, error: Exception, context: str = "") -> str:
        """
        Log error details securely and return a safe user message.

        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred

        Returns:
            A generic, safe error message for the user
        """
        # Generate unique error ID for tracking
        error_id = str(uuid.uuid4())[:8].upper()
        timestamp = datetime.now().isoformat()

        # Log full details internally (never shown to user)
        logger.error(f"[ERROR_ID: {error_id}] Timestamp: {timestamp}")
        logger.error(f"[ERROR_ID: {error_id}] Context: {context}")
        logger.error(f"[ERROR_ID: {error_id}] Error Type: {type(error).__name__}")
        logger.error(f"[ERROR_ID: {error_id}] Error Message: {str(error)}")
        logger.error(f"[ERROR_ID: {error_id}] Stack Trace:\n{traceback.format_exc()}")

        # Determine error category (without exposing details)
        error_type = cls._categorize_error(error)
        user_message = cls.ERROR_MESSAGES.get(error_type, cls.ERROR_MESSAGES["general"])

        # Return safe message with reference ID
        return f"{user_message}\n\n(Reference ID: {error_id})"

    @classmethod
    def _categorize_error(cls, error: Exception) -> str:
        """Categorize error type without exposing details."""
        error_str = str(type(error).__name__).lower()
        error_msg = str(error).lower()

        # Check for connection/network errors
        if any(term in error_str or term in error_msg for term in
               ["connection", "timeout", "network", "socket", "endpoint"]):
            return "connection"

        # Check for inference/model errors
        if any(term in error_str or term in error_msg for term in
               ["sagemaker", "inference", "model", "invoke"]):
            return "inference"

        # Check for retrieval/database errors
        if any(term in error_str or term in error_msg for term in
               ["qdrant", "retriev", "search", "vector", "embed"]):
            return "retrieval"

        # Check for validation errors
        if any(term in error_str or term in error_msg for term in
               ["valid", "format", "parse", "value"]):
            return "validation"

        return "general"


def format_sources(chunks: list[TaxBillEmbeddedChunk]) -> str:
    """Format source chunks as citations."""
    if not chunks:
        return "No sources found."

    sources = []
    for i, chunk in enumerate(chunks, 1):
        ref = chunk.get_reference()
        sources.append(f"[{i}] {ref} (Page {chunk.page_number})")

    return "\n".join(sources)


def chat(message: str, history: list) -> str:
    """Process user query and return answer with citations."""
    if not message.strip():
        return "Please enter a question about Nigerian tax law."

    try:
        # 1. Retrieve relevant chunks (k=10 for comprehensive context)
        logger.info(f"Processing query (length: {len(message)} chars)")
        chunks = retriever.search(message, k=10)

        if not chunks:
            return "I couldn't find any relevant information in the Nigeria Tax Act 2025 for your question. Please try rephrasing your question."

        # 2. Build context from chunks
        context = TaxBillEmbeddedChunk.to_context(chunks)
        logger.debug(f"Retrieved {len(chunks)} chunks")

        # 3. Call LLM via SageMaker
        llm = LLMInferenceSagemakerEndpoint(
            endpoint_name=settings.SAGEMAKER_ENDPOINT_INFERENCE,
            inference_component_name=None,
        )
        answer = InferenceExecutor(llm, message, context, prompt=TAX_BILL_PROMPT).execute()
        logger.info("Query processed successfully")

        # 4. Format response with sources
        sources = format_sources(chunks)
        response = f"{answer}\n\n---\n**Sources (for manual verification):**\n{sources}"

        return response

    except Exception as e:
        return SecureErrorHandler.handle_error(e, context=f"Query: {message[:100]}")


# Create Gradio interface
demo = gr.ChatInterface(
    fn=chat,
    title="Nigeria Tax Act 2025 - AI Assistant",
    description="""Ask questions about the Nigeria Tax Act 2025.
    The assistant will provide answers with citations to specific chapters, parts, sections, and page numbers for manual verification.""",
    examples=[
        "What are the royalty rates for offshore oil production?",
        "What is the VAT rate in Nigeria?",
        "What are the penalties for tax evasion?",
        "How is petroleum profit tax calculated?",
        "What are the exemptions for capital gains tax?",
    ],
)

if __name__ == "__main__":
    import os

    # Get port from environment (App Runner uses 8080, local uses 7860)
    port = int(os.environ.get("PORT", 7860))

    # Security settings:
    # - share=False: Don't create public URL
    # - show_error=False: Don't show detailed errors in UI
    # - show_api=False: Hide API documentation
    demo.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=port,
        show_error=False,
        show_api=False,
    )
