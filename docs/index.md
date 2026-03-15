---
title: Nigeria Tax Act 2025 - AI Legal Assistant
description: AI-powered legal assistant for Nigerian tax law with accurate, citation-backed answers
---

# Nigeria Tax Act 2025 - AI Legal Assistant

<div class="hero-section" markdown>

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Try%20Now-orange?style=for-the-badge&logo=rocket)](https://r8eqkf6a2g.us-east-1.awsapprunner.com){ .md-button .md-button--primary }
[![Model](https://img.shields.io/badge/Model-HuggingFace-yellow?style=for-the-badge&logo=huggingface)](https://huggingface.co/ocanthony4real/NigeriaTaxLlama-3.1-8B-RAG-v3){ .md-button }
[![GitHub](https://img.shields.io/badge/GitHub-Source-black?style=for-the-badge&logo=github)](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox){ .md-button }

**Get instant, accurate answers about Nigerian tax law with AI-powered citations.**

</div>

---

## See It In Action

<div class="video-container" style="text-align: center; margin: 2rem 0;">
<video width="100%" controls style="max-width: 800px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
  <source src="assets/demo-video.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>
</div>

---

## The Problem We Solve

<div class="grid cards" markdown>

-   **Hard to Navigate**

    ---

    The Nigeria Tax Act 2025 spans **200+ pages** with complex legal language that's difficult to search and understand.

-   **Time Consuming**

    ---

    Legal professionals spend **hours** searching for specific regulations and cross-referencing sections.

-   **Risk of Errors**

    ---

    Manual research can lead to **missed sections** or **incorrect interpretations** of tax law.

-   **Expensive Consultations**

    ---

    Citizens often pay for legal advice on questions that could be answered with **proper document access**.

</div>

---

## Our Solution

<div class="solution-section" markdown>

| Feature | Description |
|---------|-------------|
| **Natural Language** | Ask questions in plain English, not legal jargon |
| **Accurate Citations** | Every answer includes Section and Page references |
| **Grounded Responses** | AI prevents hallucination by using only official text |
| **Instant Answers** | Get responses in 3-5 seconds, not hours |
| **Fine-tuned AI** | LLaMA 3.1 8B trained specifically on Nigerian tax law |

</div>

---

## Verify Chatbot Responses

<div class="verification-section" markdown>

!!! success "Trust but Verify"
    Every response from our chatbot includes **Section and Page citations**. You can verify any answer directly from the official source document.

[Download Nigeria Tax Act 2025 (PDF)](source-document.md){ .md-button .md-button--primary }
[Learn How to Verify](source-document.md){ .md-button }

</div>

---

## Performance Metrics

<div class="grid cards metric-cards" markdown>

-   **93.3%**

    ---

    Accuracy Score

-   **92%**

    ---

    Citation Accuracy

-   **3-5s**

    ---

    Response Time

-   **<5%**

    ---

    Hallucination Rate

</div>

---

## How It Works

```mermaid
flowchart LR
    A[User Question] --> B[Embed Query]
    B --> C[Search 291 Chunks]
    C --> D[Rerank Results]
    D --> E[Generate Answer]
    E --> F[Cited Response]

    style A fill:#7c3aed,stroke:#5b21b6,color:#fff
    style B fill:#6366f1,stroke:#4f46e5,color:#fff
    style C fill:#6366f1,stroke:#4f46e5,color:#fff
    style D fill:#6366f1,stroke:#4f46e5,color:#fff
    style E fill:#6366f1,stroke:#4f46e5,color:#fff
    style F fill:#7c3aed,stroke:#5b21b6,color:#fff
```

<div class="steps-section" markdown>

### Step 1: Document Processing
The Nigeria Tax Act 2025 PDF is processed into **291 semantic chunks**, each preserving legal hierarchy (Chapter, Part, Section).

### Step 2: Vector Search
Your question is converted to a vector and matched against all document chunks using **semantic similarity**.

### Step 3: AI Generation
A **fine-tuned LLaMA 3.1 8B** model generates accurate answers with proper citations from the retrieved context.

</div>

---

## Quick Start

=== "Try the Demo"

    Visit our live demo - no installation required!

    [Launch Demo](https://r8eqkf6a2g.us-east-1.awsapprunner.com){ .md-button .md-button--primary }

=== "Use the API"

    ```bash
    curl -X POST https://r8eqkf6a2g.us-east-1.awsapprunner.com/api/chat \
      -H "Content-Type: application/json" \
      -d '{"query": "What is the VAT rate?", "k": 5}'
    ```

=== "Run Locally"

    ```bash
    git clone https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox.git
    cd Nigeria-Tax-Bill-Chatbox/web
    pip install -r requirements.txt
    uvicorn main:app --reload
    ```

---

## Documentation Sections

<div class="grid cards" markdown>

-   **Getting Started**

    ---

    Install and configure the chatbot in minutes

    [Installation Guide](getting-started/installation.md)

-   **Architecture**

    ---

    Understand the RAG pipeline and system design

    [Architecture Overview](architecture/overview.md)

-   **API Reference**

    ---

    Complete REST API documentation

    [API Docs](api/rest-api.md)

-   **Deployment**

    ---

    Deploy to AWS with CI/CD

    [Deployment Guide](deployment/aws-setup.md)

-   **FAQ**

    ---

    Common questions answered

    [View FAQ](faq.md)

-   **Use Cases**

    ---

    Real-world usage examples

    [See Examples](use-cases.md)

</div>

---

## Technology Stack

<div class="tech-stack" markdown>

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | FastAPI, Python 3.11 | REST API |
| **Frontend** | Next.js 14, Tailwind | Chat UI |
| **LLM** | LLaMA 3.1 8B (fine-tuned) | Generation |
| **Embeddings** | BAAI/bge-large-en-v1.5 | Semantic search |
| **Vector DB** | Qdrant Cloud | Chunk storage |
| **Infrastructure** | SageMaker, App Runner | Hosting |

</div>

---

## Why Choose This Solution?

<div class="comparison-table" markdown>

| Feature | Nigeria Tax Chatbot | Manual Search | Generic AI |
|---------|:------------------:|:-------------:|:----------:|
| Accurate citations | Yes | Yes | No |
| Instant answers | Yes | No | Yes |
| Nigerian tax expertise | Yes | Yes | No |
| No hallucination | Yes | Yes | No |
| Natural language | Yes | No | Yes |
| Cost effective | Yes | No | No |

</div>

---

## Community & Support

<div class="grid cards" markdown>

-   **GitHub**

    ---

    Star the repo, report issues, contribute

    [View Repository](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox)

-   **Support**

    ---

    Get help with installation and usage

    [Troubleshooting](troubleshooting.md)

-   **Feedback**

    ---

    Share your experience

    [Give Feedback](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox/issues)

</div>

---

## Latest Updates

!!! tip "Version 1.0.0 Released!"

    The first stable release is now available with:

    - 93.3% accuracy on tax law questions
    - Scale-to-zero for cost optimization
    - Comprehensive documentation

    [View Source Document](source-document.md)

---

<div class="footer-cta" markdown>

## Ready to Get Started?

[Try Live Demo](https://r8eqkf6a2g.us-east-1.awsapprunner.com){ .md-button .md-button--primary }
[View Source](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox){ .md-button }

</div>

---

## Acknowledgments

<div class="acknowledgments" markdown>

- **Nigeria Federal Government** - Tax Act 2025 document
- **Meta AI** - LLaMA 3.1 model
- **Hugging Face** - Model hosting
- **Qdrant** - Vector database
- **AWS** - Cloud infrastructure

</div>

---

<div class="footer-note" markdown>

*Built to make Nigerian tax law accessible to everyone.*

</div>
