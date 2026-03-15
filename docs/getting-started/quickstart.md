# Quick Start

Get the Nigeria Tax Bill Chatbot running in under 5 minutes.

## Prerequisites

Make sure you've completed the [Installation](installation.md) guide first.

---

## Running the Application

### Step 1: Start the Backend Server

```bash
cd web
uvicorn main:app --reload --port 8000
```

You should see:

```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Access the Application

Open your browser and navigate to:

```
http://localhost:8000
```

You'll see the chat interface where you can start asking questions about Nigerian tax law.

---

## Testing the API

### Health Check

```bash
curl http://localhost:8000/api/health
```

**Expected Response:**
```json
{"status": "healthy"}
```

### Ask a Question

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the corporate tax rate in Nigeria?", "k": 5}'
```

**Expected Response:**
```json
{
  "answer": "According to Section 23 (p. 15), the corporate income tax rate in Nigeria is 30% for large companies...",
  "references": ["Section 23 (p. 15)"],
  "sources": [
    {
      "content": "...",
      "section": "23",
      "page_number": 15,
      "chapter": "Companies Income Tax"
    }
  ]
}
```

---

## Example Questions to Try

Here are some example questions you can ask:

| Question | Expected Citation |
|----------|-------------------|
| What is the VAT rate? | Section 148 |
| Who is exempt from paying taxes? | Section 25 |
| What are the penalties for tax evasion? | Section 93 |
| How do I file a tax return? | Section 55 |
| What is withholding tax? | Section 78 |

---

## Using the Chat Interface

1. **Type your question** in the input field at the bottom
2. **Press Enter** or click the Send button
3. **Wait for the response** (3-5 seconds on first query due to model warm-up)
4. **View citations** - Each response includes section and page references
5. **Click on sources** to see the original document chunks

!!! tip "Pro Tip"
    Be specific in your questions. Instead of "Tell me about taxes", ask "What is the VAT rate for imported goods?"

---

## Running with Docker

If you prefer Docker:

```bash
# Build the image
docker build -t nigeria-tax-chatbot -f web/Dockerfile web/

# Run the container
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY=your_key \
  -e AWS_SECRET_KEY=your_secret \
  -e QDRANT_CLOUD_URL=your_url \
  -e QDRANT_APIKEY=your_api_key \
  -e SAGEMAKER_ENDPOINT_INFERENCE=nigeria-tax-llama-v3 \
  nigeria-tax-chatbot
```

---

## Development Mode

For development with hot-reload:

=== "Backend Only"

    ```bash
    cd web
    uvicorn main:app --reload --port 8000
    ```

=== "Frontend Development"

    ```bash
    # Terminal 1: Run backend
    cd web
    uvicorn main:app --reload --port 8000

    # Terminal 2: Run frontend dev server
    cd web/frontend
    npm run dev
    ```

    The frontend dev server runs on `http://localhost:3000` and proxies API requests to the backend.

---

## Debugging

Enable debug mode to see detailed logs:

```bash
cd web
DEBUG=true uvicorn main:app --reload --port 8000
```

Access the debug endpoint:

```bash
curl http://localhost:8000/api/debug
```

This shows the current configuration (with secrets masked).

---

## Next Steps

- [Configuration Guide](configuration.md) - Customize settings
- [Architecture Overview](../architecture/overview.md) - Understand how it works
- [API Reference](../api/rest-api.md) - Full API documentation
