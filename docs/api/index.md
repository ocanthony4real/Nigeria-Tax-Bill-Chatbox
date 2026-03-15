# API Reference

Complete API documentation for the Nigeria Tax Bill Chatbot.

---

## Base URL

| Environment | URL |
|-------------|-----|
| **Production** | `https://r8eqkf6a2g.us-east-1.awsapprunner.com` |
| **Local** | `http://localhost:8000` |

---

## Quick Start

```bash
# Check if API is running
curl https://r8eqkf6a2g.us-east-1.awsapprunner.com/api/health

# Ask a question
curl -X POST https://r8eqkf6a2g.us-east-1.awsapprunner.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the VAT rate?", "k": 5}'
```

---

## Documentation Sections

<div class="grid cards" markdown>

-   :material-api:{ .lg .middle } **REST API**

    ---

    Complete REST endpoint documentation with examples

    [:octicons-arrow-right-24: REST API](rest-api.md)

-   :material-language-python:{ .lg .middle } **Python SDK**

    ---

    Python client library for easy integration

    [:octicons-arrow-right-24: Python SDK](python-sdk.md)

</div>

---

## Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/debug` | Configuration info |
| POST | `/api/chat` | Ask a question |

---

## Authentication

Currently, the API is **public** and does not require authentication.

!!! note
    API key authentication may be added in future versions.

---

## Rate Limits

| Limit | Value |
|-------|-------|
| Requests/minute | Unlimited |
| Request body size | 1MB |
| Response timeout | 30s |
