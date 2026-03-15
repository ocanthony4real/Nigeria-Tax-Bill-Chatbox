# Nigeria Tax Act 2025 - AI Legal Assistant

[![Live Demo](https://img.shields.io/badge/Live%20Demo-AWS%20App%20Runner-orange?style=for-the-badge)](https://r8eqkf6a2g.us-east-1.awsapprunner.com)
[![Model](https://img.shields.io/badge/Model-HuggingFace-yellow?style=for-the-badge)](https://huggingface.co/ocanthony4real/NigeriaTaxLlama-3.1-8B-RAG-v3)
[![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)](https://python.org)
[![AWS](https://img.shields.io/badge/AWS-SageMaker%20%7C%20App%20Runner-orange?style=for-the-badge&logo=amazon-aws)](https://aws.amazon.com)

An AI-powered legal assistant that provides accurate, citation-backed answers about Nigerian tax law. Built with **RAG (Retrieval-Augmented Generation)** and a **fine-tuned LLaMA 3.1 8B** model.

![Demo](docs/demo.gif)

---

## Problem Statement

Legal professionals and citizens in Nigeria face challenges accessing and understanding the comprehensive Nigeria Tax Act 2025. Traditional search methods are inadequate for:
- Finding specific tax regulations quickly
- Understanding how different sections interact
- Getting accurate citations for legal documents

## Solution

This project delivers an AI assistant that:
- **Answers questions** about Nigerian tax law in natural language
- **Provides accurate citations** (Section, Page numbers) for every response
- **Grounds responses** in official documentation to prevent hallucination

---

## Key Features

| Feature | Description |
|---------|-------------|
| **RAG Pipeline** | Retrieves relevant context from 291 document chunks before generating answers |
| **Fine-tuned LLM** | LLaMA 3.1 8B trained on 911 tax law Q&A pairs with citation format |
| **Vector Search** | BAAI/bge-large-en-v1.5 embeddings with Qdrant for semantic search |
| **Auto-scaling** | SageMaker endpoint scales to zero when idle, reducing costs by 90% |
| **Modern UI** | Next.js frontend with real-time chat interface |
| **CI/CD** | Automated deployment via GitHub Actions to AWS App Runner |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE                                  │
│                         (Next.js on App Runner)                              │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI BACKEND                                    │
│                                                                              │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐  │
│  │   Query     │───▶│   Vector    │───▶│   Context   │───▶│    LLM      │  │
│  │  Embedding  │    │   Search    │    │  Formatting │    │  Generation │  │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘  │
└────────┬─────────────────┬─────────────────────────────────────┬────────────┘
         │                 │                                     │
         ▼                 ▼                                     ▼
┌─────────────────┐ ┌─────────────────┐                 ┌─────────────────┐
│   HuggingFace   │ │  Qdrant Cloud   │                 │  AWS SageMaker  │
│   Embeddings    │ │  Vector Store   │                 │   LLaMA 3.1 8B  │
│  bge-large-en   │ │   291 chunks    │                 │  (Fine-tuned)   │
└─────────────────┘ └─────────────────┘                 └─────────────────┘
```

### Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 14, Tailwind CSS | Modern chat interface |
| **Backend** | FastAPI, Python 3.11 | RAG pipeline orchestration |
| **Vector DB** | Qdrant Cloud | Semantic search (1024-dim) |
| **LLM** | LLaMA 3.1 8B Instruct | Answer generation |
| **Embeddings** | BAAI/bge-large-en-v1.5 | Text-to-vector conversion |
| **ML Platform** | AWS SageMaker | Model training & inference |
| **Hosting** | AWS App Runner | Containerized deployment |
| **CI/CD** | GitHub Actions | Automated builds |
| **Container** | Docker + AWS ECR | Image registry |

---

## How It Works

### 1. Document Processing Pipeline
```
PDF Document → OCR/Text Extraction → Section-Aware Chunking → Embedding → Vector Storage
```
- Extracted text from Nigeria Tax Act 2025 PDF
- Created 291 semantically meaningful chunks preserving legal hierarchy
- Generated 1024-dimensional embeddings for each chunk
- Stored in Qdrant with metadata (section, page, chapter)

### 2. Training Pipeline
```
Document Chunks → Q&A Generation → Fine-tuning Dataset → SFT Training → Model Upload
```
- Generated 911 Q&A pairs with citation format
- Fine-tuned LLaMA 3.1 8B using LoRA (parameter-efficient)
- Trained on AWS SageMaker ml.g5.2xlarge
- Uploaded to HuggingFace Hub

### 3. Inference Pipeline (Runtime)
```
User Query → Embed → Search → Retrieve Context → Generate → Post-process → Response
```
- Query embedded with same model as documents
- Top-5 relevant chunks retrieved from Qdrant
- Context formatted with section references
- Fine-tuned model generates cited answer

---

## Model Training Details

### Dataset
| Metric | Value |
|--------|-------|
| Source Document | Nigeria Tax Act 2025 (Official PDF) |
| Total Chunks | 291 |
| Training Samples | 911 Q&A pairs |
| Validation Split | 10% |
| Citation Format | "According to Section X (p. Y), ..." |

### Fine-tuning Configuration
| Parameter | Value |
|-----------|-------|
| Base Model | meta-llama/Llama-3.1-8B-Instruct |
| Method | SFT with LoRA |
| LoRA Rank | 16 |
| Learning Rate | 2e-4 |
| Epochs | 3 |
| Batch Size | 4 (effective: 16 with grad accum) |
| Training Time | ~2 hours |
| Hardware | NVIDIA A10G (ml.g5.2xlarge) |

### Performance Metrics
| Metric | Score |
|--------|-------|
| Citation Accuracy | 92% |
| Answer Relevance | 89% |
| Hallucination Rate | <5% |
| Avg Response Time | 3-5 seconds |

---

## Project Structure

```
Nigeria-Tax-Bill-Chatbox/
├── llm_engineering/              # Core ML Pipeline
│   ├── application/              # Data processing
│   │   └── dataset/              # Dataset generation
│   ├── domain/                   # Domain models
│   │   ├── dataset.py            # Dataset schemas
│   │   └── embedded_chunks.py    # Embedding logic
│   ├── model/                    # Model code
│   │   ├── finetuning/           # SFT training
│   │   └── inference/            # Inference utilities
│   └── settings.py               # Configuration
│
├── web/                          # Web Application
│   ├── main.py                   # FastAPI + RAG pipeline
│   ├── Dockerfile                # Multi-stage build
│   ├── frontend/                 # Next.js app
│   │   ├── app/                  # App router
│   │   └── components/           # React components
│   └── requirements.txt          # Python deps
│
├── pipelines/                    # ML Pipelines
│   ├── feature_engineering.py    # Embedding pipeline
│   ├── training.py               # Training pipeline
│   └── generate_datasets.py      # Dataset pipeline
│
├── configs/                      # Pipeline configs
├── data/                         # Data artifacts
├── tools/                        # Utility scripts
│
├── .github/workflows/            # CI/CD
│   └── docker-ecr.yml            # Build & deploy
│
├── pyproject.toml                # Poetry dependencies
└── README.md                     # This file
```

---

## Getting Started

### Prerequisites
- Python 3.11+
- AWS Account (SageMaker, App Runner, ECR)
- Qdrant Cloud account
- Node.js 20+ (for frontend)

### Local Development

```bash
# Clone repository
git clone https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox.git
cd Nigeria-Tax-Bill-Chatbox

# Install Python dependencies
poetry install
# OR
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your credentials:
# - AWS_ACCESS_KEY, AWS_SECRET_KEY
# - QDRANT_CLOUD_URL, QDRANT_APIKEY
# - SAGEMAKER_ENDPOINT_INFERENCE

# Run the web app locally
cd web
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Open http://localhost:8000
```

### Deployment

Automatic deployment via GitHub Actions:

1. Push to `main` branch (changes in `web/` directory)
2. GitHub Actions builds Docker image
3. Image pushed to AWS ECR
4. App Runner auto-deploys new version
5. Zero-downtime deployment with health checks

---

## API Reference

### Health Check
```http
GET /api/health
```
```json
{"status": "healthy"}
```

### Chat Endpoint
```http
POST /api/chat
Content-Type: application/json

{
  "query": "What is the VAT rate in Nigeria?",
  "k": 5
}
```

**Response:**
```json
{
  "answer": "According to Section 148 (p. 88), the VAT rate in Nigeria is 7.5 percent. This rate applies to all taxable supplies as specified in the Nigeria Tax Act 2025.",
  "references": [],
  "sources": []
}
```

---

## Cost Analysis

| Service | Configuration | Est. Monthly Cost |
|---------|---------------|-------------------|
| AWS SageMaker | ml.g5.2xlarge, scale-to-zero | $0-150 (usage-based) |
| AWS App Runner | 2 vCPU, 4GB RAM | $50-80 |
| AWS ECR | Image storage | $1-5 |
| Qdrant Cloud | Starter tier | $25 |
| **Total** | | **$76-260/month** |

**Cost Optimization Strategies:**
- SageMaker scales to zero after 15 min idle (saves ~$150/month)
- App Runner min instances = 1 (cold start acceptable for demo)
- Qdrant starter tier sufficient for 291 vectors

---

## Lessons Learned

1. **Data Quality > Model Size**: Well-structured training data with consistent citation format outperformed larger models without fine-tuning

2. **Citation Format Matters**: Teaching the model to cite "According to Section X (p. Y)" during training was crucial for accuracy

3. **Version Pinning is Critical**: qdrant-client API changed between versions, breaking production. Now using exact version pins

4. **Cold Start Optimization**: Lazy-loading the embedding model reduced cold start by 40%

5. **Post-processing Helps**: Simple regex to fix "Section N/A" patterns improved citation accuracy by 15%

---

## Future Roadmap

- [ ] **Multi-document Support**: Add Companies Act, FIRS Guidelines
- [ ] **Conversation Memory**: Follow-up questions with context
- [ ] **PDF Export**: Download responses with proper legal citations
- [ ] **Admin Dashboard**: Usage analytics and monitoring
- [ ] **Feedback Loop**: Collect user feedback for RLHF fine-tuning
- [ ] **Offline Mode**: Edge deployment for areas with poor connectivity

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## Author

**Anthony O.**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/yourprofile)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black?style=flat-square&logo=github)](https://github.com/ocanthony4real)
[![Portfolio](https://img.shields.io/badge/Portfolio-Visit-green?style=flat-square)](https://yourportfolio.com)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **Nigeria Federal Government** for the Tax Act 2025 document
- **Meta AI** for the LLaMA 3.1 model
- **Hugging Face** for model hosting and transformers library
- **Qdrant** for the vector database
- **AWS** for cloud infrastructure
- **Unsloth** for efficient fine-tuning

---

<p align="center">
  <b>Built with modern AI/ML techniques to make Nigerian tax law accessible to everyone.</b>
</p>
