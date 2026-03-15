# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Multi-document support (Companies Act, FIRS Guidelines)
- Conversation memory for follow-up questions
- PDF export with legal citations
- Admin dashboard for usage analytics

---

## [1.0.0] - 2025-01-15

### Added
- Initial release of Nigeria Tax Bill Chatbot
- RAG pipeline with 291 document chunks
- Fine-tuned LLaMA 3.1 8B model
- Next.js chat interface
- FastAPI REST API
- AWS SageMaker deployment with auto-scaling
- AWS App Runner hosting
- GitHub Actions CI/CD
- Comprehensive documentation

### Model
- Base: meta-llama/Llama-3.1-8B-Instruct
- Training: 911 Q&A pairs with citations
- Method: SFT with LoRA (r=16)
- Published: ocanthony4real/NigeriaTaxLlama-3.1-8B-RAG-v3

### Performance
- Accuracy: 93.3%
- Style Score: 96.7%
- Citation Rate: 92%
- Response Time: 3-5 seconds

---

## [0.3.0] - 2024-12-20

### Added
- Cross-encoder reranking for improved retrieval
- Post-processing to fix citation issues
- Debug endpoint for configuration verification
- Health check endpoint

### Changed
- Upgraded to Qdrant client 1.12.0
- Improved context formatting with section references
- Reduced max context length to 6000 characters

### Fixed
- "Section N/A" pattern now replaced with actual section
- Cold start optimization with lazy loading

---

## [0.2.0] - 2024-12-10

### Added
- Model fine-tuning pipeline with ZenML
- Dataset generation from document chunks
- Evaluation pipeline with LLM-as-judge
- SageMaker endpoint deployment script
- Scale-to-zero auto-scaling

### Changed
- Upgraded to Python 3.11
- Switched from OpenAI embeddings to BAAI/bge-large-en-v1.5
- Improved chunking to preserve legal hierarchy

### Fixed
- Embedding dimension mismatch
- Token overflow in long documents

---

## [0.1.0] - 2024-11-25

### Added
- PDF extraction pipeline
- Document chunking with section detection
- Vector storage in Qdrant Cloud
- Basic FastAPI backend
- Simple HTML frontend
- Initial Docker configuration

### Technical
- PDFMiner-six for text extraction
- Tesseract OCR for scanned pages
- LangChain for text splitting

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| 1.0.0 | 2025-01-15 | Production release |
| 0.3.0 | 2024-12-20 | Reranking & optimization |
| 0.2.0 | 2024-12-10 | Model fine-tuning |
| 0.1.0 | 2024-11-25 | Initial prototype |

---

## Upgrade Guide

### 0.3.x to 1.0.0

No breaking changes. Update dependencies:

```bash
poetry update
# or
pip install -r requirements.txt
```

### 0.2.x to 0.3.x

1. Update Qdrant client:
   ```bash
   pip install qdrant-client==1.12.0
   ```

2. Update environment variables:
   ```env
   RERANKING_CROSS_ENCODER_MODEL_ID=cross-encoder/ms-marco-MiniLM-L-4-v2
   ```

### 0.1.x to 0.2.x

1. Re-run embedding pipeline (model changed):
   ```bash
   python tools/run.py --pipeline feature_engineering
   ```

2. Update Python to 3.11

---

## Contributors

Thanks to all contributors who helped with this release:

- **Anthony O.** - Project lead
- Community contributors

---

## Links

- [GitHub Releases](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox/releases)
- [Documentation](https://ocanthony4real.github.io/Nigeria-Tax-Bill-Chatbox/)
- [Live Demo](https://r8eqkf6a2g.us-east-1.awsapprunner.com)
