# Domain Models

This document describes the core domain models used throughout the Nigeria Tax Bill Chatbot.

## Overview

The domain models are defined in `llm_engineering/domain/` and represent the core business entities.

```
domain/
├── __init__.py
├── base/
│   ├── nosql.py       # MongoDB base
│   └── vector.py      # Qdrant base
├── chunks.py          # Document chunks
├── cleaned_documents.py
├── dataset.py         # Training datasets
├── documents.py       # Raw documents
├── embedded_chunks.py # Chunks with embeddings
├── inference.py       # Inference types
├── prompt.py          # Prompt models
├── queries.py         # Query models
├── types.py           # Type definitions
└── exceptions.py      # Custom exceptions
```

---

## Core Models

### Document

Represents a raw document from the PDF.

```python title="llm_engineering/domain/documents.py"
from pydantic import BaseModel
from typing import Optional, Dict, Any

class Document(BaseModel):
    """Raw document extracted from PDF"""

    id: str
    content: str
    source: str  # File path or URL
    metadata: Dict[str, Any] = {}

    # Legal document specific
    title: Optional[str] = None
    chapter: Optional[str] = None
    part: Optional[str] = None

    class Config:
        frozen = True
```

### CleanedDocument

Document after preprocessing.

```python title="llm_engineering/domain/cleaned_documents.py"
class CleanedDocument(BaseModel):
    """Document after cleaning and normalization"""

    id: str
    content: str
    original_id: str

    # Cleaning metadata
    tokens_removed: int = 0
    whitespace_normalized: bool = False

    class Config:
        frozen = True
```

### TaxBillChunk

A semantic chunk of the tax document.

```python title="llm_engineering/domain/chunks.py"
from pydantic import BaseModel
from typing import Optional

class TaxBillChunk(BaseModel):
    """
    Semantic chunk from Nigeria Tax Act 2025.

    Contains content and metadata for citation.
    """

    id: str
    content: str

    # Citation metadata
    section: Optional[str] = None
    page_number: Optional[int] = None
    chapter: Optional[str] = None
    part: Optional[str] = None

    # Processing metadata
    document_id: Optional[str] = None
    chunk_index: Optional[int] = None

    class Config:
        frozen = True

    def citation(self) -> str:
        """Generate citation string"""
        parts = []
        if self.section:
            parts.append(f"Section {self.section}")
        if self.page_number:
            parts.append(f"(p. {self.page_number})")
        return " ".join(parts)
```

### TaxBillEmbeddedChunk

Chunk with vector embedding.

```python title="llm_engineering/domain/embedded_chunks.py"
from qdrant_client.models import PointStruct
from typing import List

class TaxBillEmbeddedChunk(BaseModel):
    """Chunk with embedding vector for storage"""

    chunk: TaxBillChunk
    embedding: List[float]

    class Config:
        frozen = True

    def to_qdrant_point(self) -> PointStruct:
        """Convert to Qdrant storage format"""
        return PointStruct(
            id=self.chunk.id,
            vector=self.embedding,
            payload={
                "content": self.chunk.content,
                "section": self.chunk.section,
                "page_number": self.chunk.page_number,
                "chapter": self.chunk.chapter,
                "part": self.chunk.part,
                "document_id": self.chunk.document_id,
                "chunk_index": self.chunk.chunk_index
            }
        )

    @classmethod
    def from_qdrant_point(cls, point: PointStruct) -> "TaxBillEmbeddedChunk":
        """Create from Qdrant point"""
        chunk = TaxBillChunk(
            id=str(point.id),
            content=point.payload["content"],
            section=point.payload.get("section"),
            page_number=point.payload.get("page_number"),
            chapter=point.payload.get("chapter"),
            part=point.payload.get("part")
        )
        return cls(chunk=chunk, embedding=point.vector)
```

---

## Dataset Models

### InstructDatasetSample

Training sample for instruction tuning.

```python title="llm_engineering/domain/dataset.py"
class InstructDatasetSample(BaseModel):
    """
    Single sample for instruction fine-tuning.

    Format follows Alpaca/Llama instruction format.
    """

    instruction: str  # The question
    context: str      # Retrieved document context
    response: str     # Answer with citations

    # Metadata
    source_chunk_id: Optional[str] = None
    difficulty: Optional[str] = None  # easy, medium, hard

    def to_text(self, template: str = None) -> str:
        """Format as training text"""
        if template is None:
            template = """### Instruction:
{instruction}

### Context:
{context}

### Response:
{response}"""

        return template.format(
            instruction=self.instruction,
            context=self.context,
            response=self.response
        )

    class Config:
        frozen = True
```

### PreferenceDatasetSample

Sample for RLHF preference training.

```python
class PreferenceDatasetSample(BaseModel):
    """
    Sample for preference/RLHF training.

    Contains chosen (preferred) and rejected responses.
    """

    instruction: str
    context: str
    chosen: str    # Preferred response
    rejected: str  # Non-preferred response

    class Config:
        frozen = True
```

---

## Query Models

### Query

User query representation.

```python title="llm_engineering/domain/queries.py"
class Query(BaseModel):
    """User query for RAG pipeline"""

    text: str
    embedding: Optional[List[float]] = None

    # Search parameters
    top_k: int = 5
    include_metadata: bool = True

    class Config:
        frozen = True

    def with_embedding(self, embedding: List[float]) -> "Query":
        """Return new query with embedding"""
        return Query(
            text=self.text,
            embedding=embedding,
            top_k=self.top_k,
            include_metadata=self.include_metadata
        )
```

### SearchResult

Result from vector search.

```python
class SearchResult(BaseModel):
    """Single search result"""

    chunk: TaxBillChunk
    score: float
    rank: int

    class Config:
        frozen = True
```

---

## Prompt Models

### Prompt

Structured prompt for LLM.

```python title="llm_engineering/domain/prompt.py"
class Prompt(BaseModel):
    """Structured prompt for LLM generation"""

    system: Optional[str] = None
    context: str
    query: str

    # Generation parameters
    max_tokens: int = 1024
    temperature: float = 0.7

    def format(self, template: str) -> str:
        """Format prompt using template"""
        return template.format(
            system=self.system or "",
            context=self.context,
            query=self.query
        )

    class Config:
        frozen = True
```

---

## Inference Models

### InferenceRequest

Request to inference endpoint.

```python title="llm_engineering/domain/inference.py"
class InferenceRequest(BaseModel):
    """Request to SageMaker inference endpoint"""

    prompt: str
    max_new_tokens: int = 1024
    temperature: float = 0.7
    top_p: float = 0.9
    do_sample: bool = True

    def to_payload(self) -> dict:
        """Convert to SageMaker payload format"""
        return {
            "inputs": self.prompt,
            "parameters": {
                "max_new_tokens": self.max_new_tokens,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "do_sample": self.do_sample
            }
        }
```

### InferenceResponse

Response from inference endpoint.

```python
class InferenceResponse(BaseModel):
    """Response from SageMaker inference"""

    generated_text: str
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None

    @classmethod
    def from_sagemaker(cls, response: dict) -> "InferenceResponse":
        """Parse SageMaker response"""
        return cls(
            generated_text=response[0]["generated_text"]
        )
```

---

## Base Classes

### NoSQLModel

Base for MongoDB documents.

```python title="llm_engineering/domain/base/nosql.py"
from pydantic import BaseModel, Field
from bson import ObjectId

class NoSQLModel(BaseModel):
    """Base class for MongoDB documents"""

    id: str = Field(default_factory=lambda: str(ObjectId()))

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

    def to_mongo(self) -> dict:
        """Convert to MongoDB document"""
        data = self.model_dump()
        data["_id"] = ObjectId(data.pop("id"))
        return data

    @classmethod
    def from_mongo(cls, data: dict) -> "NoSQLModel":
        """Create from MongoDB document"""
        data["id"] = str(data.pop("_id"))
        return cls(**data)
```

### VectorModel

Base for Qdrant vectors.

```python title="llm_engineering/domain/base/vector.py"
from pydantic import BaseModel
from typing import List
import uuid

class VectorModel(BaseModel):
    """Base class for Qdrant vectors"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    embedding: List[float]

    class Config:
        frozen = True

    def to_point(self) -> PointStruct:
        """Convert to Qdrant point"""
        raise NotImplementedError

    @classmethod
    def from_point(cls, point: PointStruct) -> "VectorModel":
        """Create from Qdrant point"""
        raise NotImplementedError
```

---

## Type Definitions

```python title="llm_engineering/domain/types.py"
from typing import TypeVar, List

# Generic types
T = TypeVar("T")
ChunkType = TypeVar("ChunkType", bound="TaxBillChunk")

# Collection aliases
ChunkList = List[TaxBillChunk]
EmbeddedChunkList = List[TaxBillEmbeddedChunk]
SearchResults = List[SearchResult]

# Embedding type
Embedding = List[float]
EmbeddingBatch = List[Embedding]
```

---

## Exceptions

```python title="llm_engineering/domain/exceptions.py"
class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class ChunkNotFoundError(DomainException):
    """Chunk not found in storage"""
    pass

class EmbeddingError(DomainException):
    """Error generating embeddings"""
    pass

class InferenceError(DomainException):
    """Error during model inference"""
    pass
```

---

## Usage Examples

### Creating Chunks

```python
from llm_engineering.domain import TaxBillChunk

chunk = TaxBillChunk(
    id="chunk_001",
    content="The VAT rate shall be 7.5 percent...",
    section="148",
    page_number=88,
    chapter="Value Added Tax"
)

print(chunk.citation())  # "Section 148 (p. 88)"
```

### Creating Training Samples

```python
from llm_engineering.domain import InstructDatasetSample

sample = InstructDatasetSample(
    instruction="What is the VAT rate in Nigeria?",
    context="[Section 148 (p. 88)] The VAT rate shall be 7.5 percent...",
    response="According to Section 148 (p. 88), the VAT rate in Nigeria is 7.5 percent."
)

text = sample.to_text()
```

### Building Queries

```python
from llm_engineering.domain import Query

query = Query(
    text="What are the penalties for tax evasion?",
    top_k=5
)

# Add embedding
embedded_query = query.with_embedding(embedding_model.encode(query.text))
```

---

## Next Steps

- [LLM Engineering Module](llm-engineering.md) - Full module overview
- [RAG Pipeline](../architecture/rag-pipeline.md) - How models are used in RAG
