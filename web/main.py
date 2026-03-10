"""
Nigeria Tax Bill Chatbot - Combined FastAPI + Static Frontend
Single deployment for AWS App Runner
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Load .env file automatically
from dotenv import load_dotenv

# Load from parent directory (where the main .env is)
env_path = Path(__file__).resolve().parent.parent / ".env"
print(f"Loading .env from: {env_path}")
load_dotenv(env_path)

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import boto3
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer


# =============================================================================
# Configuration (loaded from .env automatically)
# =============================================================================

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY = os.environ.get("AWS_ACCESS_KEY", "")
AWS_SECRET_KEY = os.environ.get("AWS_SECRET_KEY", "")
SAGEMAKER_ENDPOINT = os.environ.get("SAGEMAKER_ENDPOINT_INFERENCE", "nigeria-tax-llama")
QDRANT_URL = os.environ.get("QDRANT_CLOUD_URL", "")
QDRANT_API_KEY = os.environ.get("QDRANT_APIKEY", "")
COLLECTION_NAME = "embedded_tax_bill_chunks"

# Static files directory (built Next.js output)
STATIC_DIR = Path(__file__).parent / "static"


# =============================================================================
# Prompt Template (matches RAG training format)
# =============================================================================

TAX_BILL_PROMPT = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
Based on the following excerpt from the Nigeria Tax Act 2025, answer the question.

Context:
{context}

Question: {query}

### Response:
"""


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="Nigeria Tax Act 2025",
    description="AI-powered assistant for Nigerian tax law",
    version="1.0.0",
)


# =============================================================================
# Request/Response Models
# =============================================================================

class ChatRequest(BaseModel):
    query: str
    k: int = 5


class Source(BaseModel):
    reference: str
    page: int
    chapter: Optional[str] = None
    part: Optional[str] = None
    section: Optional[str] = None
    subsection: Optional[str] = None
    snippet: str


class ChatResponse(BaseModel):
    answer: str
    references: List[str]
    sources: List[Source]


# =============================================================================
# Lazy-loaded Clients (for cold start optimization)
# =============================================================================

embedding_model = None
qdrant_client = None
sagemaker_runtime = None


def get_embedding_model():
    global embedding_model
    if embedding_model is None:
        print("Loading embedding model...")
        embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")
        print("Embedding model loaded.")
    return embedding_model


def get_qdrant_client():
    global qdrant_client
    if qdrant_client is None:
        print("Connecting to Qdrant...")
        qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
        print("Qdrant connected.")
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
        print("SageMaker client ready.")
    return sagemaker_runtime


# =============================================================================
# RAG Pipeline Functions
# =============================================================================

def search_tax_bill(query: str, k: int = 10) -> list:
    """Search Qdrant for relevant tax bill chunks."""
    model = get_embedding_model()
    client = get_qdrant_client()

    # Embed the query
    query_vector = model.encode(query).tolist()

    # Search Qdrant
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=k,
    )

    # Extract chunk data
    chunks = []
    for result in results:
        payload = result.payload
        chunks.append({
            "content": payload.get("content", ""),
            "page": payload.get("page_number", 0),
            "chapter": payload.get("chapter", ""),
            "part": payload.get("part", ""),
            "section": payload.get("section", ""),
            "subsection": payload.get("subsection", ""),
        })

    return chunks


def build_reference_string(chunk: dict) -> str:
    """Build reference string: Section X(Y) (p. Z) format."""
    section = chunk.get("section", "")
    subsection = chunk.get("subsection", "")
    page_num = chunk.get("page", "N/A")
    part = chunk.get("part", "")
    chapter = chunk.get("chapter", "")

    # Primary: Section with optional subsection
    if section:
        # Clean section - remove "Section" if already present
        section_clean = section if not section.lower().startswith("section") else section[7:].strip()
        if subsection:
            sub_clean = subsection if not subsection.lower().startswith("subsection") else subsection[10:].strip()
            return f"Section {section_clean}({sub_clean}) (p. {page_num})"
        return f"Section {section_clean} (p. {page_num})"

    # Fallback: Part/Chapter
    fallback = []
    if part:
        part_clean = part if not part.lower().startswith("part") else part[4:].strip()
        fallback.append(f"Part {part_clean}")
    if chapter:
        chapter_clean = chapter if not chapter.lower().startswith("chapter") else chapter[7:].strip()
        fallback.append(f"Chapter {chapter_clean}")

    if fallback:
        return f"{', '.join(fallback)} (p. {page_num})"

    return f"(p. {page_num})"


def format_context(chunks: list, max_chars: int = 6000) -> str:
    """Format chunks into context string for the LLM, with truncation."""
    context = ""
    for i, chunk in enumerate(chunks, 1):
        reference = build_reference_string(chunk)

        chunk_text = f"""
[{reference}]
{chunk['content']}

"""
        # Stop adding chunks if we exceed the limit
        if len(context) + len(chunk_text) > max_chars:
            break

        context += chunk_text

    return context


def extract_references(chunks: list) -> list:
    """Extract unique reference strings from chunks."""
    references = []
    for chunk in chunks:
        ref = build_reference_string(chunk)
        if ref not in references:
            references.append(ref)
    return references


def build_sources(chunks: list) -> list:
    """Build detailed source objects for frontend display."""
    sources = []
    for chunk in chunks:
        reference = build_reference_string(chunk)
        content = chunk.get("content", "")
        snippet = content[:200] + "..." if len(content) > 200 else content

        sources.append({
            "reference": reference,
            "page": chunk.get("page", 0),
            "chapter": chunk.get("chapter"),
            "part": chunk.get("part"),
            "section": chunk.get("section"),
            "subsection": chunk.get("subsection"),
            "snippet": snippet,
        })

    return sources


def fix_section_na(answer: str, chunks: list) -> str:
    """
    Post-process answer to replace 'Section N/A' with actual section references from RAG chunks.

    The model sometimes outputs 'Section N/A (p. X)' because 31.7% of training data had this pattern.
    This function finds the best matching section reference from the retrieved chunks.
    """
    import re

    # Pattern to match "Section N/A (p. X)" or "Section N/A(p. X)"
    na_pattern = re.compile(r'Section N/A\s*\(p\.\s*(\d+)\)', re.IGNORECASE)

    match = na_pattern.search(answer)
    if not match:
        return answer  # No "Section N/A" found, return as-is

    page_num = int(match.group(1))

    # Find the best matching chunk based on page number
    best_section = None
    for chunk in chunks:
        chunk_page = chunk.get("page", 0)
        chunk_section = chunk.get("section", "")

        # Match by page number (within ±1 page tolerance)
        if abs(chunk_page - page_num) <= 1 and chunk_section:
            # Clean section - remove "Section" prefix if present
            section_clean = chunk_section
            if section_clean.lower().startswith("section"):
                section_clean = section_clean[7:].strip()
            best_section = section_clean
            break

    # If no section found by page, use the first chunk with a valid section
    if not best_section:
        for chunk in chunks:
            chunk_section = chunk.get("section", "")
            if chunk_section and chunk_section.lower() != "n/a":
                section_clean = chunk_section
                if section_clean.lower().startswith("section"):
                    section_clean = section_clean[7:].strip()
                best_section = section_clean
                break

    # Replace "Section N/A" with the found section
    if best_section:
        # Replace all occurrences
        answer = re.sub(
            r'Section N/A(\s*\(p\.)',
            f'Section {best_section}\\1',
            answer,
            flags=re.IGNORECASE
        )

    return answer


def call_sagemaker(prompt: str, retry_count: int = 0) -> str:
    """Call SageMaker endpoint for LLM inference. Retries with higher temperature if empty."""
    client = get_sagemaker_client()

    temp = 0.1 + (retry_count * 0.3)

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 256,
            "temperature": temp,
            "top_p": 0.9,
            "repetition_penalty": 1.2,
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
        full_text = result[0].get("generated_text", "")

        # Try multiple extraction methods
        answer = ""

        # Method 1: Split by Alpaca response marker
        response_marker = "### Response:"
        if response_marker in full_text:
            answer = full_text.split(response_marker)[-1].strip()

        # Method 2: If no marker, try to find content after the prompt
        if not answer and len(full_text) > len(prompt):
            answer = full_text[len(prompt):].strip()

        # Clean up any special tokens
        for token in ["<|eot_id|>", "<|end_of_text|>", "<|begin_of_text|>", "</s>", "<s>"]:
            answer = answer.replace(token, "").strip()

        # RADICAL FIX: If still empty and we haven't retried too many times, retry
        if not answer and retry_count < 2:
            print(f"[RETRY {retry_count + 1}] Empty response, retrying with temp={temp + 0.3}")
            return call_sagemaker(prompt, retry_count + 1)

        # FALLBACK: If still empty, return a meaningful message
        if not answer:
            return "I found relevant sections but could not generate a complete answer. Please try rephrasing your question."

        return answer


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/api/health")
async def health_check():
    """Health check for App Runner."""
    return {"status": "healthy"}


@app.get("/api/debug")
async def debug_config():
    """Debug endpoint to check configuration."""
    return {
        "aws_region": AWS_REGION,
        "sagemaker_endpoint": SAGEMAKER_ENDPOINT,
        "qdrant_url_set": bool(QDRANT_URL),
        "qdrant_url_preview": QDRANT_URL[:30] + "..." if QDRANT_URL else "NOT SET",
        "qdrant_api_key_set": bool(QDRANT_API_KEY),
        "aws_access_key_set": bool(AWS_ACCESS_KEY),
        "aws_secret_key_set": bool(AWS_SECRET_KEY),
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a tax law query and return answer with citations.

    This is the main RAG endpoint that:
    1. Searches Qdrant for relevant chunks
    2. Formats context with references
    3. Calls SageMaker LLM
    4. Returns structured response
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # 1. Search for relevant chunks
        chunks = search_tax_bill(request.query, k=request.k)

        if not chunks:
            return ChatResponse(
                answer="I couldn't find relevant information in the Nigeria Tax Act 2025 to answer your question. Please try rephrasing.",
                references=[],
                sources=[],
            )

        # 2. Format context and extract metadata
        context = format_context(chunks)
        references = extract_references(chunks)

        # 3. Call LLM
        prompt = TAX_BILL_PROMPT.format(context=context, query=request.query)
        answer = call_sagemaker(prompt)

        # 4. Post-process: Fix "Section N/A" with actual section references
        answer = fix_section_na(answer, chunks)

        return ChatResponse(
            answer=answer,
            references=[],  # Removed references from response
            sources=[],  # Removed sources from response
        )

    except Exception as e:
        error_id = str(uuid.uuid4())[:8].upper()
        print(f"[ERROR {error_id}] {datetime.now()}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred processing your request. Reference: {error_id}"
        )


# =============================================================================
# Static File Serving (Frontend)
# =============================================================================

# Mount static assets (JS, CSS, images)
if STATIC_DIR.exists():
    app.mount("/_next", StaticFiles(directory=STATIC_DIR / "_next"), name="next-static")

    # Serve static files from root
    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        """Serve frontend static files."""
        # Try exact file match
        file_path = STATIC_DIR / path
        if file_path.is_file():
            return FileResponse(file_path)

        # Try with .html extension
        html_path = STATIC_DIR / f"{path}.html"
        if html_path.is_file():
            return FileResponse(html_path)

        # Default to index.html (SPA fallback)
        index_path = STATIC_DIR / "index.html"
        if index_path.is_file():
            return FileResponse(index_path)

        raise HTTPException(status_code=404, detail="Not found")

    @app.get("/")
    async def serve_index():
        """Serve the main page."""
        index_path = STATIC_DIR / "index.html"
        if index_path.is_file():
            return FileResponse(index_path)
        return {"message": "Frontend not built. Run: npm run build"}


# =============================================================================
# Run with: uvicorn main:app --reload
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
