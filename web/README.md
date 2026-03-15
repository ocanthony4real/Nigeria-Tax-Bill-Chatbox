# Nigeria Tax Act 2025 - Web Application

Professional chatbot interface for querying the Nigeria Tax Act 2025.

## Architecture

```
Single App Runner Service
├── FastAPI Backend (/api/chat)
│   ├── Qdrant (vector search)
│   ├── BGE Embeddings
│   └── SageMaker LLM
└── Next.js Frontend (static)
```

## Local Development

### 1. Setup Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 2. Build Frontend

**Windows:**
```bash
build.bat
```

**Mac/Linux:**
```bash
chmod +x build.sh
./build.sh
```

### 3. Run Server

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Open http://localhost:8000

## Deploy to AWS App Runner

### Option A: Docker Image

1. Build and push to ECR:
```bash
docker build -t nigeria-tax-chatbot .
docker tag nigeria-tax-chatbot:latest <account>.dkr.ecr.<region>.amazonaws.com/nigeria-tax-chatbot:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/nigeria-tax-chatbot:latest
```

2. Create App Runner service from ECR image

### Option B: Source Code

1. Push this `web/` folder to a GitHub repo
2. Create App Runner service → Source: GitHub
3. Set environment variables in App Runner console

### Environment Variables (Secrets)

Set these in App Runner console:
- `AWS_ACCESS_KEY`
- `AWS_SECRET_KEY`
- `QDRANT_CLOUD_URL`
- `QDRANT_APIKEY`
- `SAGEMAKER_ENDPOINT_INFERENCE` (default: nigeria-tax-llama)

## API Endpoints

- `GET /` - Serves the chat UI
- `GET /api/health` - Health check
- `POST /api/chat` - Query the tax act

### POST /api/chat

Request:
```json
{
  "query": "What is the VAT rate?",
  "k": 10
}
```

Response:
```json
{
  "answer": "The VAT rate is 7.5%...",
  "references": ["Section 95 (Page 123)"],
  "sources": [{"reference": "...", "page": 123, "snippet": "..."}]
}
```
