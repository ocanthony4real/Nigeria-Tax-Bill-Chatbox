# LLM Engineering Module

The `llm_engineering` module is the core ML/AI package containing all machine learning logic.

## Module Structure

```
llm_engineering/
├── __init__.py
├── settings.py              # Centralized configuration
├── application/             # Business logic layer
│   ├── crawlers/            # Web scraping utilities
│   ├── dataset/             # Dataset generation
│   ├── networks/            # Embedding models
│   ├── preprocessing/       # Document processing
│   ├── rag/                 # RAG implementation
│   └── utils/               # Utility functions
├── domain/                  # Domain models
│   ├── base/                # Base classes
│   ├── chunks.py            # Chunk models
│   ├── cleaned_documents.py # Cleaned doc models
│   ├── dataset.py           # Dataset schemas
│   ├── documents.py         # Document models
│   ├── embedded_chunks.py   # Embedded chunk models
│   ├── inference.py         # Inference interfaces
│   ├── prompt.py            # Prompt models
│   ├── queries.py           # Query models
│   └── types.py             # Type definitions
├── model/                   # Model code
│   ├── finetuning/          # SFT training
│   ├── inference/           # Inference utilities
│   └── evaluation/          # Model evaluation
└── infrastructure/          # External integrations
    ├── aws/                 # AWS services
    ├── db/                  # Database clients
    └── files_io.py          # File operations
```

---

## Settings

The `settings.py` module provides centralized configuration:

```python title="llm_engineering/settings.py"
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Embedding Configuration
    EMBEDDING_MODEL_ID: str = "BAAI/bge-large-en-v1.5"
    EMBEDDING_MODEL_MAX_INPUT_LENGTH: int = 512
    EMBEDDING_SIZE: int = 1024

    # Reranking Configuration
    RERANKING_CROSS_ENCODER_MODEL_ID: str = "cross-encoder/ms-marco-MiniLM-L-4-v2"

    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY: str = ""
    AWS_SECRET_KEY: str = ""
    AWS_ARN_ROLE: str = ""

    # Qdrant Configuration
    QDRANT_CLOUD_URL: str = ""
    QDRANT_APIKEY: str = ""

    # SageMaker Configuration
    SAGEMAKER_ENDPOINT_INFERENCE: str = "nigeria-tax-llama-v3"

    class Config:
        env_file = ".env"

settings = Settings()
```

### Usage

```python
from llm_engineering.settings import settings

# Access settings
print(settings.EMBEDDING_MODEL_ID)
print(settings.AWS_REGION)
```

---

## Application Layer

### RAG Components

#### TaxBillRetriever

Specialized retriever for tax documents:

```python title="llm_engineering/application/rag/tax_bill_retriever.py"
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class TaxBillRetriever:
    def __init__(self):
        self._client = None
        self._embedding_model = None

    @property
    def client(self) -> QdrantClient:
        if self._client is None:
            self._client = QdrantClient(
                url=settings.QDRANT_CLOUD_URL,
                api_key=settings.QDRANT_APIKEY
            )
        return self._client

    @property
    def embedding_model(self) -> SentenceTransformer:
        if self._embedding_model is None:
            self._embedding_model = SentenceTransformer(
                settings.EMBEDDING_MODEL_ID
            )
        return self._embedding_model

    def search(
        self,
        query: str,
        k: int = 5,
        collection: str = "tax_bill_chunks"
    ) -> List[TaxBillChunk]:
        # Embed query
        query_vector = self.embedding_model.encode(query).tolist()

        # Search Qdrant
        results = self.client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=k,
            with_payload=True
        )

        return [self._to_chunk(r) for r in results]
```

#### Reranker

Cross-encoder for result reranking:

```python title="llm_engineering/application/rag/reranking.py"
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self):
        self.model = CrossEncoder(
            settings.RERANKING_CROSS_ENCODER_MODEL_ID
        )

    def rerank(
        self,
        query: str,
        chunks: List[TaxBillChunk],
        top_k: int = 5
    ) -> List[TaxBillChunk]:
        pairs = [(query, chunk.content) for chunk in chunks]
        scores = self.model.predict(pairs)

        ranked = sorted(
            zip(chunks, scores),
            key=lambda x: x[1],
            reverse=True
        )
        return [chunk for chunk, _ in ranked[:top_k]]
```

#### Prompt Templates

```python title="llm_engineering/application/rag/prompt_templates.py"
TAX_BILL_PROMPT = """You are a Nigerian tax law expert assistant.
Answer questions accurately based ONLY on the provided context
from the Nigeria Tax Act 2025.

IMPORTANT RULES:
1. Only use information from the provided context
2. Always cite the specific Section and page number
3. If the information is not in the context, say "I don't have information about that"
4. Use the format "According to Section X (p. Y), ..."

### Context:
{context}

### Question:
{query}

### Response:"""
```

### Preprocessing

#### Chunking

```python title="llm_engineering/application/preprocessing/operations/chunking.py"
from langchain.text_splitter import RecursiveCharacterTextSplitter

class TaxBillChunker:
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ". ", " "]
        )

    def chunk(self, document: Document) -> List[Chunk]:
        texts = self.splitter.split_text(document.content)
        return [
            Chunk(
                content=text,
                document_id=document.id,
                metadata=document.metadata
            )
            for text in texts
        ]
```

#### Embedding

```python title="llm_engineering/application/preprocessing/embedding_data_handlers.py"
class EmbeddingHandler:
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL_ID)

    def embed_chunks(
        self,
        chunks: List[Chunk],
        batch_size: int = 32
    ) -> List[EmbeddedChunk]:
        embeddings = self.model.encode(
            [c.content for c in chunks],
            batch_size=batch_size,
            show_progress_bar=True
        )

        return [
            EmbeddedChunk(
                chunk=chunk,
                embedding=embedding.tolist()
            )
            for chunk, embedding in zip(chunks, embeddings)
        ]
```

---

## Domain Layer

### Chunk Models

```python title="llm_engineering/domain/chunks.py"
from pydantic import BaseModel

class TaxBillChunk(BaseModel):
    id: str
    content: str
    section: Optional[str] = None
    page_number: Optional[int] = None
    chapter: Optional[str] = None
    part: Optional[str] = None

    class Config:
        frozen = True
```

### Dataset Models

```python title="llm_engineering/domain/dataset.py"
class InstructDatasetSample(BaseModel):
    """Single training sample for instruction tuning"""
    instruction: str  # The question
    context: str      # Retrieved context
    response: str     # Expected answer with citations

class PreferenceDatasetSample(BaseModel):
    """Sample for RLHF preference training"""
    instruction: str
    chosen: str       # Preferred response
    rejected: str     # Non-preferred response
```

### Embedded Chunks

```python title="llm_engineering/domain/embedded_chunks.py"
class TaxBillEmbeddedChunk(BaseModel):
    chunk: TaxBillChunk
    embedding: List[float]

    def to_qdrant_point(self) -> PointStruct:
        return PointStruct(
            id=self.chunk.id,
            vector=self.embedding,
            payload={
                "content": self.chunk.content,
                "section": self.chunk.section,
                "page_number": self.chunk.page_number,
                "chapter": self.chunk.chapter,
                "part": self.chunk.part
            }
        )
```

---

## Infrastructure Layer

### Qdrant Client

```python title="llm_engineering/infrastructure/db/qdrant.py"
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

class QdrantDatabase:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.QDRANT_CLOUD_URL,
            api_key=settings.QDRANT_APIKEY
        )

    def create_collection(
        self,
        name: str,
        vector_size: int = 1024
    ):
        self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )

    def upsert(
        self,
        collection: str,
        chunks: List[TaxBillEmbeddedChunk]
    ):
        points = [c.to_qdrant_point() for c in chunks]
        self.client.upsert(
            collection_name=collection,
            points=points
        )
```

### SageMaker Client

```python title="llm_engineering/infrastructure/inference_pipeline_api.py"
import boto3
import json

class SageMakerInference:
    def __init__(self):
        self.client = boto3.client(
            "sagemaker-runtime",
            region_name=settings.AWS_REGION,
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY
        )

    def invoke(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.9,
                "do_sample": True
            }
        }

        response = self.client.invoke_endpoint(
            EndpointName=settings.SAGEMAKER_ENDPOINT_INFERENCE,
            ContentType="application/json",
            Body=json.dumps(payload)
        )

        result = json.loads(response["Body"].read().decode())
        return result[0]["generated_text"]
```

---

## Model Layer

### Fine-tuning

```python title="llm_engineering/model/finetuning/sft.py"
from unsloth import FastLanguageModel
from trl import SFTTrainer

class TaxLawFineTuner:
    def __init__(self, config: TrainingConfig):
        self.config = config
        self.model = None
        self.tokenizer = None

    def load_model(self):
        self.model, self.tokenizer = FastLanguageModel.from_pretrained(
            model_name=self.config.base_model,
            max_seq_length=self.config.max_seq_length,
            load_in_4bit=True
        )

        # Add LoRA adapters
        self.model = FastLanguageModel.get_peft_model(
            self.model,
            r=self.config.lora_rank,
            lora_alpha=self.config.lora_alpha,
            lora_dropout=self.config.lora_dropout,
            target_modules=self.config.target_modules
        )

    def train(self, dataset):
        trainer = SFTTrainer(
            model=self.model,
            tokenizer=self.tokenizer,
            train_dataset=dataset,
            args=self.config.training_args,
            dataset_text_field="text",
            max_seq_length=self.config.max_seq_length
        )
        trainer.train()

    def save_and_push(self, repo_id: str):
        merged = self.model.merge_and_unload()
        merged.push_to_hub(repo_id)
        self.tokenizer.push_to_hub(repo_id)
```

---

## Usage Examples

### Running RAG Query

```python
from llm_engineering.application.rag import TaxBillRetriever, Reranker
from llm_engineering.infrastructure import SageMakerInference

# Initialize components
retriever = TaxBillRetriever()
reranker = Reranker()
llm = SageMakerInference()

# Search
chunks = retriever.search("What is the VAT rate?", k=10)

# Rerank
ranked = reranker.rerank("What is the VAT rate?", chunks, top_k=5)

# Generate
context = format_context(ranked)
prompt = build_prompt("What is the VAT rate?", context)
answer = llm.invoke(prompt)
```

### Processing New Documents

```python
from llm_engineering.application.preprocessing import (
    TaxBillChunker,
    EmbeddingHandler
)
from llm_engineering.infrastructure.db import QdrantDatabase

# Process document
chunker = TaxBillChunker()
chunks = chunker.chunk(document)

# Embed
embedder = EmbeddingHandler()
embedded = embedder.embed_chunks(chunks)

# Store
db = QdrantDatabase()
db.upsert("tax_bill_chunks", embedded)
```

---

## Next Steps

- [Web Application](web-application.md) - Frontend and API
- [ML Pipelines](ml-pipelines.md) - Pipeline orchestration
