# Configuration

This guide covers all configuration options for the Nigeria Tax Bill Chatbot.

## Configuration Overview

The application uses a centralized configuration system based on Pydantic BaseSettings, which supports:

- Environment variables
- `.env` file loading
- ZenML secret store integration (optional)
- Sensible defaults

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `AWS_ACCESS_KEY` | AWS access key ID | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_KEY` | AWS secret access key | `wJalrXUtnFEMI/K7MDENG/...` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `QDRANT_CLOUD_URL` | Qdrant cluster URL | `https://xyz.qdrant.io` |
| `QDRANT_APIKEY` | Qdrant API key | `your_api_key` |
| `SAGEMAKER_ENDPOINT_INFERENCE` | SageMaker endpoint name | `nigeria-tax-llama-v3` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HUGGINGFACE_ACCESS_TOKEN` | HuggingFace API token | `None` |
| `MONGO_DATABASE_HOST` | MongoDB connection string | `None` |
| `COMET_API_KEY` | Comet ML API key | `None` |
| `ANTHROPIC_API_KEY` | Anthropic API key | `None` |
| `DEBUG` | Enable debug mode | `false` |

---

## Settings File

The main configuration is defined in `llm_engineering/settings.py`:

```python title="llm_engineering/settings.py"
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Model Configuration
    EMBEDDING_MODEL_ID: str = "BAAI/bge-large-en-v1.5"
    EMBEDDING_MODEL_MAX_INPUT_LENGTH: int = 512
    EMBEDDING_SIZE: int = 1024

    # Reranking Configuration
    RERANKING_CROSS_ENCODER_MODEL_ID: str = "cross-encoder/ms-marco-MiniLM-L-4-v2"

    # RAG Configuration
    RAG_TOP_K: int = 5
    RAG_TEMPERATURE: float = 0.7
    RAG_MAX_TOKENS: int = 1024

    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY: str = ""
    AWS_SECRET_KEY: str = ""
    AWS_ARN_ROLE: str = ""

    # Qdrant Configuration
    QDRANT_CLOUD_URL: str = ""
    QDRANT_APIKEY: str = ""
    QDRANT_DATABASE_HOST: str = "localhost"
    QDRANT_DATABASE_PORT: int = 6333

    # SageMaker Configuration
    SAGEMAKER_ENDPOINT_INFERENCE: str = "nigeria-tax-llama-v3"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

---

## Model Configuration

### Embedding Model

The default embedding model is `BAAI/bge-large-en-v1.5`:

```env
EMBEDDING_MODEL_ID=BAAI/bge-large-en-v1.5
EMBEDDING_MODEL_MAX_INPUT_LENGTH=512
EMBEDDING_SIZE=1024
```

!!! info "Changing Embedding Models"
    If you change the embedding model, you'll need to re-embed all documents and update the Qdrant collection.

### Reranking Model

The cross-encoder model for reranking search results:

```env
RERANKING_CROSS_ENCODER_MODEL_ID=cross-encoder/ms-marco-MiniLM-L-4-v2
```

---

## RAG Configuration

Fine-tune the RAG pipeline behavior:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `RAG_TOP_K` | Number of chunks to retrieve | `5` |
| `RAG_TEMPERATURE` | LLM generation temperature | `0.7` |
| `RAG_MAX_TOKENS` | Maximum tokens in response | `1024` |
| `RAG_CONTEXT_MAX_LENGTH` | Max context characters | `6000` |

```env
RAG_TOP_K=5
RAG_TEMPERATURE=0.7
RAG_MAX_TOKENS=1024
```

---

## AWS Configuration

### IAM Permissions

Your AWS IAM user/role needs the following permissions:

```json title="iam-policy.json"
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sagemaker:InvokeEndpoint",
        "sagemaker:DescribeEndpoint"
      ],
      "Resource": "arn:aws:sagemaker:*:*:endpoint/nigeria-tax-*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken",
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "*"
    }
  ]
}
```

### SageMaker Endpoint

Configure the SageMaker endpoint:

```env
SAGEMAKER_ENDPOINT_INFERENCE=nigeria-tax-llama-v3
AWS_ARN_ROLE=arn:aws:iam::123456789:role/sagemaker-execution-role
```

---

## Qdrant Configuration

### Cloud Setup

For Qdrant Cloud:

```env
QDRANT_CLOUD_URL=https://your-cluster-id.us-east-1.aws.cloud.qdrant.io
QDRANT_APIKEY=your_api_key_here
```

### Local Setup

For local development with Docker:

```bash
docker run -p 6333:6333 qdrant/qdrant
```

```env
QDRANT_DATABASE_HOST=localhost
QDRANT_DATABASE_PORT=6333
```

---

## Pipeline Configuration

Pipeline-specific configurations are stored in `configs/`:

### Feature Engineering

```yaml title="configs/feature_engineering.yaml"
parameters:
  pdf_processor:
    source_file: "data/pdfs/Nigeria-Tax-Act-2025.pdf"
    chunk_size: 1000
    chunk_overlap: 200

  embedding:
    model_id: "BAAI/bge-large-en-v1.5"
    batch_size: 32
```

### Training

```yaml title="configs/training.yaml"
parameters:
  model:
    base_model: "meta-llama/Llama-3.1-8B-Instruct"

  training:
    num_epochs: 3
    learning_rate: 2e-4
    batch_size: 4
    gradient_accumulation_steps: 4

  lora:
    rank: 16
    alpha: 32
    dropout: 0.1
```

---

## Web Application Configuration

### FastAPI Settings

```python title="web/main.py"
# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### App Runner Configuration

```yaml title="web/apprunner.yaml"
version: 1.0
runtime: python311
build:
  commands:
    build:
      - pip install -r requirements.txt
run:
  command: uvicorn main:app --host 0.0.0.0 --port 8000
  network:
    port: 8000
  env:
    - name: AWS_REGION
      value: us-east-1
```

---

## Security Best Practices

!!! danger "Production Security"
    Follow these security practices for production deployments:

1. **Never commit secrets** - Use environment variables or secret managers
2. **Rotate credentials regularly** - Update API keys periodically
3. **Use IAM roles** - Prefer IAM roles over access keys in AWS
4. **Enable HTTPS** - Always use TLS in production
5. **Restrict CORS** - Configure specific allowed origins

```env title="Production .env"
# Use AWS Secrets Manager or Parameter Store instead
AWS_ACCESS_KEY=${aws-ssm:/prod/aws-access-key}
AWS_SECRET_KEY=${aws-ssm:/prod/aws-secret-key}
```

---

## Troubleshooting Configuration

??? question "Settings not loading from .env"
    Ensure the `.env` file is in the project root and properly formatted:
    ```bash
    # Check file exists
    ls -la .env

    # Verify format (no spaces around =)
    cat .env | head -5
    ```

??? question "AWS credentials not working"
    Verify credentials with the AWS CLI:
    ```bash
    aws sts get-caller-identity
    ```

??? question "Qdrant connection timeout"
    Check if the Qdrant URL is correct and the cluster is active:
    ```bash
    curl -X GET "$QDRANT_CLOUD_URL/collections" \
      -H "api-key: $QDRANT_APIKEY"
    ```

---

## Next Steps

- [Architecture Overview](../architecture/overview.md) - Understand the system design
- [Deployment Guide](../deployment/aws-setup.md) - Deploy to production
