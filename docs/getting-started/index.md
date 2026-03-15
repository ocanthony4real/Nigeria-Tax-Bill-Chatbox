# Getting Started

Get up and running with the Nigeria Tax Bill Chatbot in minutes.

---

## Quick Navigation

<div class="grid cards" markdown>

-   :material-download:{ .lg .middle } **Installation**

    ---

    Set up the development environment with all dependencies

    [:octicons-arrow-right-24: Installation Guide](installation.md)

-   :material-play:{ .lg .middle } **Quick Start**

    ---

    Run the application locally and make your first query

    [:octicons-arrow-right-24: Quick Start](quickstart.md)

-   :material-cog:{ .lg .middle } **Configuration**

    ---

    Configure environment variables and settings

    [:octicons-arrow-right-24: Configuration](configuration.md)

</div>

---

## Prerequisites

Before you begin, ensure you have:

| Requirement | Version | Check Command |
|-------------|---------|---------------|
| Python | 3.11+ | `python --version` |
| Node.js | 20+ | `node --version` |
| Git | Latest | `git --version` |
| Docker | Latest | `docker --version` |

---

## Choose Your Path

=== "Just Try It"

    Use the live demo - no installation required!

    [:material-rocket-launch: Open Demo](https://r8eqkf6a2g.us-east-1.awsapprunner.com){ .md-button .md-button--primary }

=== "Use the API"

    Integrate with our REST API:

    ```bash
    curl -X POST https://r8eqkf6a2g.us-east-1.awsapprunner.com/api/chat \
      -H "Content-Type: application/json" \
      -d '{"query": "What is VAT rate?", "k": 5}'
    ```

    [:octicons-arrow-right-24: API Documentation](../api/rest-api.md)

=== "Run Locally"

    Clone and run the full stack:

    ```bash
    git clone https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox.git
    cd Nigeria-Tax-Bill-Chatbox
    pip install -r requirements.txt
    cd web && uvicorn main:app --reload
    ```

    [:octicons-arrow-right-24: Full Installation Guide](installation.md)

=== "Deploy Your Own"

    Deploy to AWS with CI/CD:

    [:octicons-arrow-right-24: Deployment Guide](../deployment/aws-setup.md)

---

## Next Steps

After getting started:

1. **Explore the architecture** - [How it works](../architecture/overview.md)
2. **Read the API docs** - [REST API Reference](../api/rest-api.md)
3. **See use cases** - [Real-world examples](../use-cases.md)
