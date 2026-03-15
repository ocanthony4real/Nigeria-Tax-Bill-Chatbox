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

## :movie_camera: See It In Action

<div class="demo-container" markdown>

!!! tip "Live Demo Available"
    Try the chatbot live at [r8eqkf6a2g.us-east-1.awsapprunner.com](https://r8eqkf6a2g.us-east-1.awsapprunner.com)

</div>

<div class="demo-example" markdown>

!!! example "Example Conversation"

    **You:** What is the VAT rate in Nigeria?

    **Assistant:** According to **Section 148 (p. 88)**, the VAT rate in Nigeria is **7.5 percent**. This rate applies to all taxable supplies as specified in the Nigeria Tax Act 2025.

    ---

    :material-link: **Sources:** Section 148 (p. 88), Section 149 (p. 89)

</div>

---

## :dart: The Problem We Solve

<div class="grid cards" markdown>

-   :material-file-search:{ .lg .middle } **Hard to Navigate**

    ---

    The Nigeria Tax Act 2025 spans **200+ pages** with complex legal language that's difficult to search and understand.

-   :material-clock-alert:{ .lg .middle } **Time Consuming**

    ---

    Legal professionals spend **hours** searching for specific regulations and cross-referencing sections.

-   :material-alert-circle:{ .lg .middle } **Risk of Errors**

    ---

    Manual research can lead to **missed sections** or **incorrect interpretations** of tax law.

-   :material-currency-usd:{ .lg .middle } **Expensive Consultations**

    ---

    Citizens often pay for legal advice on questions that could be answered with **proper document access**.

</div>

---

## :white_check_mark: Our Solution

<div class="solution-section" markdown>

| Feature | Description |
|---------|-------------|
| :speech_balloon: **Natural Language** | Ask questions in plain English, not legal jargon |
| :bookmark_check: **Accurate Citations** | Every answer includes Section and Page references |
| :shield: **Grounded Responses** | AI prevents hallucination by using only official text |
| :zap: **Instant Answers** | Get responses in 3-5 seconds, not hours |
| :brain: **Fine-tuned AI** | LLaMA 3.1 8B trained specifically on Nigerian tax law |

</div>

---

## :material-file-check: Verify Chatbot Responses

<div class="verification-section" markdown>

!!! success "Trust but Verify"
    Every response from our chatbot includes **Section and Page citations**. You can verify any answer directly from the official source document.

[:material-file-pdf-box: Download Nigeria Tax Act 2025 (PDF)](source-document.md){ .md-button .md-button--primary }
[:octicons-arrow-right-24: Learn How to Verify](source-document.md){ .md-button }

</div>

---

## :bar_chart: Performance Metrics

<div class="grid cards metric-cards" markdown>

-   :material-check-circle:{ .lg .middle }

    ---

    **93.3%**

    Accuracy Score

-   :material-format-quote-close:{ .lg .middle }

    ---

    **92%**

    Citation Accuracy

-   :material-clock-fast:{ .lg .middle }

    ---

    **3-5s**

    Response Time

-   :material-shield-check:{ .lg .middle }

    ---

    **<5%**

    Hallucination Rate

</div>

---

## :building_construction: How It Works

```mermaid
flowchart LR
    A[👤 User Question] --> B[🔍 Embed Query]
    B --> C[📚 Search 291 Chunks]
    C --> D[🎯 Rerank Results]
    D --> E[🤖 Generate Answer]
    E --> F[✨ Cited Response]

    style A fill:#f9f,stroke:#333
    style F fill:#9f9,stroke:#333
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

## :rocket: Quick Start

=== "Try the Demo"

    Visit our live demo - no installation required!

    [:material-rocket-launch: Launch Demo](https://r8eqkf6a2g.us-east-1.awsapprunner.com){ .md-button .md-button--primary }

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

## :books: Documentation Sections

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } **Getting Started**

    ---

    Install and configure the chatbot in minutes

    [:octicons-arrow-right-24: Installation Guide](getting-started/installation.md)

-   :material-chart-box:{ .lg .middle } **Architecture**

    ---

    Understand the RAG pipeline and system design

    [:octicons-arrow-right-24: Architecture Overview](architecture/overview.md)

-   :material-api:{ .lg .middle } **API Reference**

    ---

    Complete REST API documentation

    [:octicons-arrow-right-24: API Docs](api/rest-api.md)

-   :material-cloud-upload:{ .lg .middle } **Deployment**

    ---

    Deploy to AWS with CI/CD

    [:octicons-arrow-right-24: Deployment Guide](deployment/aws-setup.md)

-   :material-frequently-asked-questions:{ .lg .middle } **FAQ**

    ---

    Common questions answered

    [:octicons-arrow-right-24: View FAQ](faq.md)

-   :material-book-open-variant:{ .lg .middle } **Use Cases**

    ---

    Real-world usage examples

    [:octicons-arrow-right-24: See Examples](use-cases.md)

</div>

---

## :gear: Technology Stack

<div class="tech-stack" markdown>

| Layer | Technology | Purpose |
|-------|------------|---------|
| :material-language-python: **Backend** | FastAPI, Python 3.11 | REST API |
| :material-react: **Frontend** | Next.js 14, Tailwind | Chat UI |
| :material-brain: **LLM** | LLaMA 3.1 8B (fine-tuned) | Generation |
| :material-vector-polygon: **Embeddings** | BAAI/bge-large-en-v1.5 | Semantic search |
| :material-database: **Vector DB** | Qdrant Cloud | Chunk storage |
| :material-aws: **Infrastructure** | SageMaker, App Runner | Hosting |

</div>

---

## :star: Why Choose This Solution?

<div class="comparison-table" markdown>

| Feature | Nigeria Tax Chatbot | Manual Search | Generic AI |
|---------|:------------------:|:-------------:|:----------:|
| Accurate citations | :white_check_mark: | :white_check_mark: | :x: |
| Instant answers | :white_check_mark: | :x: | :white_check_mark: |
| Nigerian tax expertise | :white_check_mark: | :white_check_mark: | :x: |
| No hallucination | :white_check_mark: | :white_check_mark: | :x: |
| Natural language | :white_check_mark: | :x: | :white_check_mark: |
| Cost effective | :white_check_mark: | :x: | :x: |

</div>

---

## :people_holding_hands: Community & Support

<div class="grid cards" markdown>

-   :material-github:{ .lg .middle } **GitHub**

    ---

    Star the repo, report issues, contribute

    [:octicons-arrow-right-24: View Repository](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox)

-   :material-help-circle:{ .lg .middle } **Support**

    ---

    Get help with installation and usage

    [:octicons-arrow-right-24: Troubleshooting](troubleshooting.md)

-   :material-message:{ .lg .middle } **Feedback**

    ---

    Share your experience

    [:octicons-arrow-right-24: Give Feedback](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox/issues)

</div>

---

## :newspaper: Latest Updates

!!! tip "Version 1.0.0 Released!"

    The first stable release is now available with:

    - 93.3% accuracy on tax law questions
    - Scale-to-zero for cost optimization
    - Comprehensive documentation

    [:octicons-arrow-right-24: View Source Document](source-document.md)

---

<div class="footer-cta" markdown>

## Ready to Get Started?

[:material-rocket-launch: Try Live Demo](https://r8eqkf6a2g.us-east-1.awsapprunner.com){ .md-button .md-button--primary }
[:material-github: View Source](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox){ .md-button }

</div>

---

## :pray: Acknowledgments

<div class="acknowledgments" markdown>

- **Nigeria Federal Government** - Tax Act 2025 document
- **Meta AI** - LLaMA 3.1 model
- **Hugging Face** - Model hosting
- **Qdrant** - Vector database
- **AWS** - Cloud infrastructure

</div>

---

<div class="footer-note" markdown>

*Built with :green_heart: to make Nigerian tax law accessible to everyone.*

</div>
