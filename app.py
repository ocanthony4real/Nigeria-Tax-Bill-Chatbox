"""
Nigeria Tax Bill Chatbot - Standalone HF Spaces Version
No complex dependencies - just what's needed for the chatbot.
"""

import os
import json
import uuid
from datetime import datetime

import gradio as gr
import boto3
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


# =============================================================================
# Configuration from Environment Variables
# =============================================================================

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY", "")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY", "")
SAGEMAKER_ENDPOINT = os.environ.get("SAGEMAKER_ENDPOINT_INFERENCE", "nigeria-tax-llama")
QDRANT_URL = os.environ.get("QDRANT_CLOUD_URL", "")
QDRANT_API_KEY = os.environ.get("QDRANT_APIKEY", "")
COLLECTION_NAME = "embedded_tax_bill_chunks"


# =============================================================================
# Prompt Template
# =============================================================================

TAX_BILL_PROMPT = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a legal assistant for the Nigeria Tax Act 2025. You MUST follow these rules strictly:

CRITICAL RULES - NEVER VIOLATE THESE:
1. ONLY use information from the CONTEXT provided below. Do NOT use any external knowledge.
2. NEVER make up URLs, websites, or external references.
3. NEVER mention services, platforms, or tools not in the context.
4. If the context does not contain information to answer the question, say: "The provided sections of the Nigeria Tax Act do not contain specific information about this topic."
5. ONLY cite sections, chapters, and parts that appear in the context.

RESPONSE FORMAT:
1. Answer based STRICTLY on the context provided.
2. Quote the exact text from the Act when relevant, using quotation marks.
3. Cite specific Section numbers, Parts, and Chapters from the context.
4. Explain the legal provisions in clear, practical terms.
5. End with "References:" listing only sections actually quoted from the context.

If you cannot answer from the context, do NOT make up information.<|eot_id|><|start_header_id|>user<|end_header_id|>

CONTEXT FROM NIGERIA TAX ACT (use ONLY this information):
{context}

QUESTION: {query}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

Based on the Nigeria Tax Act 2025 excerpts provided:

"""


# =============================================================================
# Initialize Clients (lazy loading)
# =============================================================================

embedding_model = None
qdrant_client = None
sagemaker_runtime = None


def get_embedding_model():
    global embedding_model
    if embedding_model is None:
        print("Loading embedding model...")
        embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")
    return embedding_model


def get_qdrant_client():
    global qdrant_client
    if qdrant_client is None:
        print("Connecting to Qdrant...")
        qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
    return qdrant_client


def get_sagemaker_client():
    global sagemaker_runtime
    if sagemaker_runtime is None:
        print("Setting up SageMaker client...")
        sagemaker_runtime = boto3.client(
            "sagemaker-runtime",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
        )
    return sagemaker_runtime


# =============================================================================
# Core Functions
# =============================================================================

def search_tax_bill(query: str, k: int = 10) -> list:
    """Search Qdrant for relevant tax bill chunks."""
    model = get_embedding_model()
    client = get_qdrant_client()

    query_vector = model.encode(query).tolist()

    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=k,
    )

    chunks = []
    for result in results:
        payload = result.payload
        chunks.append({
            "content": payload.get("content", ""),
            "page": payload.get("page_number", 0),
            "chapter": payload.get("chapter", ""),
            "part": payload.get("part", ""),
            "section": payload.get("section", ""),
        })

    return chunks


def format_context(chunks: list) -> str:
    """Format chunks into context string."""
    context = ""
    for i, chunk in enumerate(chunks, 1):
        ref_parts = []
        if chunk.get("chapter"):
            ref_parts.append(f"Chapter {chunk['chapter']}")
        if chunk.get("part"):
            ref_parts.append(f"Part {chunk['part']}")
        if chunk.get("section"):
            ref_parts.append(f"Section {chunk['section']}")

        reference = ", ".join(ref_parts) if ref_parts else f"Page {chunk.get('page', 'N/A')}"

        context += f"""
Chunk {i}:
Reference: {reference}
Content:
{chunk['content']}

"""
    return context


def format_sources(chunks: list) -> str:
    """Format source citations."""
    sources = []
    for i, chunk in enumerate(chunks, 1):
        ref_parts = []
        if chunk.get("chapter"):
            ref_parts.append(f"Ch. {chunk['chapter']}")
        if chunk.get("part"):
            ref_parts.append(f"Part {chunk['part']}")
        if chunk.get("section"):
            ref_parts.append(f"Sec. {chunk['section']}")

        reference = ", ".join(ref_parts) if ref_parts else "N/A"
        sources.append(f"[{i}] {reference} (Page {chunk.get('page', 'N/A')})")

    return "\n".join(sources)


def call_sagemaker(prompt: str) -> str:
    """Call SageMaker endpoint for inference."""
    client = get_sagemaker_client()

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.01,
            "top_p": 0.7,
            "repetition_penalty": 1.1,
            "do_sample": True,
        }
    }

    response = client.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT,
        ContentType="application/json",
        Body=json.dumps(payload),
    )

    result = json.loads(response["Body"].read().decode())

    if isinstance(result, list) and len(result) > 0:
        return result[0].get("generated_text", "")
    return str(result)


# =============================================================================
# Chat Function
# =============================================================================

def chat(message: str, history: list) -> str:
    """Process user query and return answer."""
    if not message.strip():
        return "Please enter a question about Nigerian tax law."

    try:
        # 1. Search for relevant chunks
        chunks = search_tax_bill(message, k=10)

        if not chunks:
            return "I couldn't find relevant information in the Nigeria Tax Act 2025. Please try rephrasing your question."

        # 2. Format context
        context = format_context(chunks)

        # 3. Create prompt and call SageMaker
        prompt = TAX_BILL_PROMPT.format(context=context, query=message)
        answer = call_sagemaker(prompt)

        # 4. Format response with sources
        sources = format_sources(chunks)
        response = f"{answer}\n\n---\n**Sources:**\n{sources}"

        return response

    except Exception as e:
        error_id = str(uuid.uuid4())[:8].upper()
        print(f"[ERROR {error_id}] {datetime.now()}: {str(e)}")
        return f"Something went wrong. Please try again.\n\n(Reference ID: {error_id})"


# =============================================================================
# Gradio Interface
# =============================================================================

demo = gr.ChatInterface(
    fn=chat,
    title="Nigeria Tax Act 2025 - AI Assistant",
    description="Ask questions about the Nigeria Tax Act 2025. Get answers with citations.",
    examples=[
        "What is the VAT rate in Nigeria?",
        "What are the penalties for tax evasion?",
        "How is company income tax calculated?",
        "What are the exemptions for capital gains tax?",
    ],
)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=False,
    )
