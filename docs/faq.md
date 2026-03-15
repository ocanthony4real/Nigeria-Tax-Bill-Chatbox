# Frequently Asked Questions

Common questions about the Nigeria Tax Bill Chatbot.

---

## General Questions

??? question "What is the Nigeria Tax Bill Chatbot?"

    The Nigeria Tax Bill Chatbot is an AI-powered legal assistant that answers questions about the Nigeria Tax Act 2025. It uses:

    - **RAG (Retrieval-Augmented Generation)** to find relevant sections
    - **Fine-tuned LLaMA 3.1 8B** to generate accurate answers
    - **Citation system** to reference specific sections and pages

    Unlike generic AI assistants, it's specifically trained on Nigerian tax law and always provides citations.

??? question "Is this an official government service?"

    **No.** This is an independent project created to make Nigerian tax law more accessible. While it uses the official Nigeria Tax Act 2025 as its source, it is not affiliated with or endorsed by the Nigerian government.

    Always consult with a qualified tax professional for official advice.

??? question "How accurate is the chatbot?"

    Based on our evaluation:

    | Metric | Score |
    |--------|-------|
    | Overall Accuracy | 93.3% |
    | Citation Accuracy | 92% |
    | Hallucination Rate | <5% |

    The chatbot is designed to cite sources for every answer, allowing you to verify information.

??? question "Is my data private?"

    Yes. We do not store your questions or personal information. Each conversation is:

    - Processed in real-time
    - Not logged or saved
    - Not used for training

    The service is stateless - we don't remember previous conversations.

---

## Using the Chatbot

??? question "What types of questions can I ask?"

    You can ask about any topic covered in the Nigeria Tax Act 2025, including:

    - **Tax rates** (VAT, corporate tax, personal income tax)
    - **Exemptions** (who is exempt from various taxes)
    - **Penalties** (consequences of tax violations)
    - **Procedures** (how to file, pay, appeal)
    - **Definitions** (legal terms and their meanings)
    - **Thresholds** (income levels, registration requirements)

    **Examples:**

    - "What is the VAT rate in Nigeria?"
    - "Who is exempt from paying personal income tax?"
    - "What are the penalties for late tax filing?"
    - "How do I register for VAT?"

??? question "Why doesn't the chatbot answer my question?"

    The chatbot may not answer if:

    1. **Not in the Tax Act** - The information isn't in the Nigeria Tax Act 2025
    2. **Too vague** - Try being more specific
    3. **Recent changes** - The model is based on the 2025 Act; newer amendments may not be included
    4. **Outside scope** - Questions about other laws or general advice

    **Tips for better answers:**

    - Be specific: "VAT rate for imported goods" vs "tell me about VAT"
    - Ask one question at a time
    - Use tax terminology when possible

??? question "How do I interpret the citations?"

    Citations follow this format: **Section X (p. Y)**

    - **Section**: The specific section number in the Tax Act
    - **p.**: Page number in the official PDF

    Example: "Section 148 (p. 88)" means Section 148, found on page 88.

    You can verify any citation by downloading the [official Tax Act PDF](https://example.com/tax-act.pdf).

??? question "Can I have a conversation with follow-up questions?"

    Currently, **no**. Each question is independent - the chatbot doesn't remember previous questions in the conversation.

    This feature is planned for a future release. For now, include all necessary context in each question.

---

## Technical Questions

??? question "How does the RAG pipeline work?"

    The pipeline has 5 stages:

    ```mermaid
    flowchart LR
        A[Query] --> B[Embed]
        B --> C[Search]
        C --> D[Rerank]
        D --> E[Generate]
    ```

    1. **Embed**: Convert your question to a vector
    2. **Search**: Find similar chunks in the vector database
    3. **Rerank**: Use a cross-encoder to improve relevance
    4. **Generate**: LLM creates an answer from the context
    5. **Post-process**: Clean up and verify citations

    [:octicons-arrow-right-24: Learn more](architecture/rag-pipeline.md)

??? question "What model is being used?"

    We use a fine-tuned version of **LLaMA 3.1 8B Instruct**:

    | Property | Value |
    |----------|-------|
    | Base Model | meta-llama/Llama-3.1-8B-Instruct |
    | Fine-tuning | SFT with LoRA (r=16) |
    | Training Data | 911 Q&A pairs |
    | Published | [HuggingFace Hub](https://huggingface.co/ocanthony4real/NigeriaTaxLlama-3.1-8B-RAG-v3) |

    [:octicons-arrow-right-24: Training details](architecture/model-training.md)

??? question "Why is the first response slow?"

    The SageMaker endpoint uses **scale-to-zero** to reduce costs. When there's no traffic, it scales down. The first request triggers a "cold start" which can take 15-30 seconds.

    Subsequent requests are much faster (3-5 seconds).

    **Workaround**: The demo site has a keep-warm mechanism that reduces cold starts during business hours.

??? question "Can I run this locally?"

    Yes! You can run the full stack locally:

    ```bash
    # Clone
    git clone https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox.git
    cd Nigeria-Tax-Bill-Chatbox

    # Install
    pip install -r requirements.txt

    # Configure
    cp .env.example .env
    # Edit .env with your API keys

    # Run
    cd web
    uvicorn main:app --reload
    ```

    You'll need accounts with Qdrant Cloud and either:

    - Deploy your own SageMaker endpoint, OR
    - Use the HuggingFace Inference API

    [:octicons-arrow-right-24: Installation guide](getting-started/installation.md)

??? question "What's the API rate limit?"

    Currently, there are **no rate limits** on the public API. However:

    - Be respectful of shared resources
    - Implement client-side rate limiting for production apps
    - Contact us for high-volume use cases

    Rate limiting may be added in future versions.

---

## Deployment Questions

??? question "How much does it cost to run?"

    Estimated monthly costs:

    | Service | Low Traffic | High Traffic |
    |---------|-------------|--------------|
    | SageMaker | $20-50 | $150-300 |
    | App Runner | $30-50 | $80-150 |
    | Other | $5 | $10 |
    | **Total** | **$55-105** | **$240-460** |

    With scale-to-zero enabled, costs are usage-based.

    [:octicons-arrow-right-24: Cost optimization](deployment/cost-optimization.md)

??? question "Can I deploy to other cloud providers?"

    Yes, though our documentation focuses on AWS. The application is containerized, so you can deploy to:

    - **Google Cloud**: Cloud Run + Vertex AI
    - **Azure**: Container Apps + Azure ML
    - **Self-hosted**: Any Kubernetes cluster with GPU

    You'll need to adapt the infrastructure code for your provider.

??? question "Is there a managed/hosted option?"

    Not currently. Options:

    1. **Use the public demo** - Free, but shared resources
    2. **Self-deploy** - Full control, you pay infrastructure costs
    3. **Contact us** - For enterprise deployment assistance

    A managed SaaS version may be offered in the future.

---

## Legal & Compliance

??? question "Can I use this for commercial purposes?"

    The project is licensed under **MIT License**, which allows commercial use. However:

    - The underlying LLaMA model has its own license terms
    - You are responsible for compliance with Nigerian law
    - This is not a substitute for professional legal advice

    Review all licenses before commercial deployment.

??? question "Who is liable for incorrect information?"

    This tool is provided **as-is** without warranty. The MIT License includes:

    > THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND...

    Users should:

    - Verify important information with official sources
    - Consult qualified professionals for legal advice
    - Not rely solely on AI-generated content for compliance

---

## Getting Help

??? question "How do I report a bug?"

    1. Check existing [GitHub Issues](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox/issues)
    2. If not found, create a new issue with:
        - Description of the bug
        - Steps to reproduce
        - Expected vs actual behavior
        - Screenshots if applicable

??? question "How do I request a feature?"

    Create a [GitHub Issue](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox/issues/new) with:

    - Feature description
    - Use case / why it's needed
    - Any implementation ideas

??? question "How can I contribute?"

    We welcome contributions! Visit our [GitHub repository](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox) to:

    - Fork the repository
    - Submit pull requests
    - Report issues
    - Suggest improvements

---

## Still Have Questions?

If your question isn't answered here:

1. Check the [Troubleshooting Guide](troubleshooting.md)
2. Search [GitHub Issues](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox/issues)
3. Create a new issue if needed

[:octicons-arrow-right-24: Go to Troubleshooting](troubleshooting.md){ .md-button }
