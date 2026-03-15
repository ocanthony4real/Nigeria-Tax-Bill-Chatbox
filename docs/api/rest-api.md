# REST API Reference

Complete reference for the Nigeria Tax Bill Chatbot REST API.

## Base URL

| Environment | URL |
|-------------|-----|
| Production | `https://r8eqkf6a2g.us-east-1.awsapprunner.com` |
| Local | `http://localhost:8000` |

---

## Authentication

Currently, the API is public and does not require authentication.

!!! note "Future Enhancement"
    API key authentication will be added in a future release.

---

## Endpoints

### Health Check

Check if the service is running.

```http
GET /api/health
```

#### Response

```json
{
  "status": "healthy"
}
```

#### Status Codes

| Code | Description |
|------|-------------|
| 200 | Service is healthy |
| 503 | Service unavailable |

---

### Debug

Get current configuration (secrets masked).

```http
GET /api/debug
```

#### Response

```json
{
  "qdrant_url": "https://xyz.qdrant.io...",
  "sagemaker_endpoint": "nigeria-tax-llama-v3",
  "embedding_model": "BAAI/bge-large-en-v1.5",
  "aws_region": "us-east-1",
  "collection_name": "tax_bill_chunks"
}
```

---

### Chat

Ask a question about Nigerian tax law.

```http
POST /api/chat
Content-Type: application/json
```

#### Request Body

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | Yes | - | The question to ask |
| `k` | integer | No | 5 | Number of chunks to retrieve |

```json
{
  "query": "What is the VAT rate in Nigeria?",
  "k": 5
}
```

#### Response

```json
{
  "answer": "According to Section 148 (p. 88), the VAT rate in Nigeria is 7.5 percent. This rate applies to all taxable supplies as specified in the Nigeria Tax Act 2025.",
  "references": [
    "Section 148 (p. 88)",
    "Section 149 (p. 89)"
  ],
  "sources": [
    {
      "content": "The standard VAT rate applicable to all taxable supplies in Nigeria shall be 7.5 percent (7.5%) of the value of the taxable supplies...",
      "section": "148",
      "page_number": 88,
      "chapter": "Value Added Tax"
    },
    {
      "content": "The following goods and services shall be exempt from VAT...",
      "section": "149",
      "page_number": 89,
      "chapter": "Value Added Tax"
    }
  ]
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Generated answer with citations |
| `references` | array[string] | List of section references |
| `sources` | array[Source] | Detailed source information |

#### Source Object

| Field | Type | Description |
|-------|------|-------------|
| `content` | string | Chunk text content |
| `section` | string | Section number |
| `page_number` | integer | Page number in PDF |
| `chapter` | string | Chapter name |

#### Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Invalid request body |
| 500 | Internal server error |
| 503 | Model endpoint unavailable |

#### Errors

```json
{
  "detail": "Error message here"
}
```

---

## Usage Examples

### cURL

```bash
# Health check
curl https://r8eqkf6a2g.us-east-1.awsapprunner.com/api/health

# Ask a question
curl -X POST https://r8eqkf6a2g.us-east-1.awsapprunner.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the corporate tax rate?", "k": 5}'
```

### Python

```python
import requests

BASE_URL = "https://r8eqkf6a2g.us-east-1.awsapprunner.com"

# Health check
response = requests.get(f"{BASE_URL}/api/health")
print(response.json())

# Chat
response = requests.post(
    f"{BASE_URL}/api/chat",
    json={
        "query": "What is the corporate tax rate?",
        "k": 5
    }
)
data = response.json()
print(f"Answer: {data['answer']}")
print(f"References: {data['references']}")
```

### JavaScript

```javascript
const BASE_URL = "https://r8eqkf6a2g.us-east-1.awsapprunner.com";

// Health check
const health = await fetch(`${BASE_URL}/api/health`);
console.log(await health.json());

// Chat
const response = await fetch(`${BASE_URL}/api/chat`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json"
  },
  body: JSON.stringify({
    query: "What is the corporate tax rate?",
    k: 5
  })
});

const data = await response.json();
console.log("Answer:", data.answer);
console.log("References:", data.references);
```

### HTTPie

```bash
# Health check
http GET https://r8eqkf6a2g.us-east-1.awsapprunner.com/api/health

# Chat
http POST https://r8eqkf6a2g.us-east-1.awsapprunner.com/api/chat \
  query="What is the corporate tax rate?" \
  k:=5
```

---

## Rate Limiting

Currently, no rate limiting is implemented.

| Limit | Value |
|-------|-------|
| Requests per minute | Unlimited |
| Request body size | 1MB |
| Response timeout | 30 seconds |

!!! warning "Production Use"
    For production applications, implement client-side rate limiting to avoid overloading the service.

---

## Response Times

Expected response times:

| Operation | Time |
|-----------|------|
| Health check | <100ms |
| Debug | <100ms |
| Chat (cold start) | 10-30s |
| Chat (warm) | 3-5s |

!!! info "Cold Start"
    The SageMaker endpoint may scale to zero after inactivity. The first request will trigger a cold start, which takes longer.

---

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Errors

| Error | Status | Solution |
|-------|--------|----------|
| Invalid JSON | 400 | Check request body format |
| Missing query | 400 | Ensure `query` field is present |
| Endpoint warming up | 503 | Retry after a few seconds |
| Internal error | 500 | Check server logs |

### Retry Strategy

For 503 errors (endpoint warming up):

```python
import time
import requests

def chat_with_retry(query, max_retries=3):
    for attempt in range(max_retries):
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"query": query}
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 503:
            wait_time = 2 ** attempt  # Exponential backoff
            print(f"Endpoint warming up, retrying in {wait_time}s...")
            time.sleep(wait_time)
            continue

        response.raise_for_status()

    raise Exception("Max retries exceeded")
```

---

## OpenAPI Specification

The API documentation is available via Swagger UI:

```
https://r8eqkf6a2g.us-east-1.awsapprunner.com/docs
```

Or ReDoc:

```
https://r8eqkf6a2g.us-east-1.awsapprunner.com/redoc
```

---

## Next Steps

- [Python SDK](python-sdk.md) - Python client library
- [Quick Start](../getting-started/quickstart.md) - Get started quickly
