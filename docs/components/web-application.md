# Web Application

The web application provides a modern chat interface for interacting with the Nigeria Tax Bill Chatbot.

## Overview

The application consists of:

- **FastAPI Backend** - REST API with RAG pipeline
- **Next.js Frontend** - Modern chat interface

```
web/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container configuration
├── apprunner.yaml       # AWS App Runner config
├── build.sh             # Frontend build script
├── frontend/            # Next.js application
│   ├── app/             # App router pages
│   ├── components/      # React components
│   ├── package.json     # Node dependencies
│   └── tailwind.config.js
└── static/              # Built frontend assets
```

---

## Backend (FastAPI)

### Application Structure

```python title="web/main.py"
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(
    title="Nigeria Tax Bill Chatbot API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Request/Response Models

```python
class ChatRequest(BaseModel):
    """Chat endpoint request"""
    query: str
    k: int = 5  # Number of chunks to retrieve

class Source(BaseModel):
    """Source citation"""
    content: str
    section: Optional[str]
    page_number: Optional[int]
    chapter: Optional[str]

class ChatResponse(BaseModel):
    """Chat endpoint response"""
    answer: str
    references: List[str]
    sources: List[Source]
```

### API Endpoints

#### Health Check

```python
@app.get("/api/health")
async def health():
    """Liveness probe for load balancer"""
    return {"status": "healthy"}
```

#### Debug Endpoint

```python
@app.get("/api/debug")
async def debug():
    """Configuration verification (secrets masked)"""
    return {
        "qdrant_url": settings.QDRANT_CLOUD_URL[:20] + "...",
        "sagemaker_endpoint": settings.SAGEMAKER_ENDPOINT_INFERENCE,
        "embedding_model": settings.EMBEDDING_MODEL_ID,
        "aws_region": settings.AWS_REGION
    }
```

#### Chat Endpoint

```python
@app.post("/api/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Main RAG endpoint for answering tax questions.

    1. Embed the user's query
    2. Search Qdrant for relevant chunks
    3. Format context with section references
    4. Generate answer using SageMaker
    5. Post-process and return
    """
    try:
        # Step 1: Embed query
        query_vector = embedding_model.encode(request.query).tolist()

        # Step 2: Search Qdrant
        results = qdrant_client.search(
            collection_name="tax_bill_chunks",
            query_vector=query_vector,
            limit=request.k,
            with_payload=True
        )

        # Step 3: Format context
        chunks = [to_chunk(r) for r in results]
        context = format_context(chunks)

        # Step 4: Generate answer
        prompt = build_prompt(request.query, context)
        raw_answer = invoke_sagemaker(prompt)

        # Step 5: Post-process
        answer = post_process(raw_answer, chunks)

        return ChatResponse(
            answer=answer,
            references=extract_references(chunks),
            sources=[to_source(c) for c in chunks]
        )

    except Exception as e:
        logger.exception("Chat endpoint error")
        raise HTTPException(500, str(e))
```

### Helper Functions

```python
def format_context(chunks: List[Chunk], max_length: int = 6000) -> str:
    """Format chunks into prompt context"""
    parts = []
    for chunk in chunks:
        ref = f"[Section {chunk.section} (p. {chunk.page_number})]"
        parts.append(f"{ref}\n{chunk.content}")

    context = "\n\n".join(parts)
    return context[:max_length]

def post_process(response: str, chunks: List[Chunk]) -> str:
    """Clean up model response"""
    # Extract after response marker
    if "### Response:" in response:
        response = response.split("### Response:")[-1].strip()

    # Fix N/A section references
    response = fix_section_references(response, chunks)

    return response

def fix_section_references(text: str, chunks: List[Chunk]) -> str:
    """Replace N/A sections with actual section numbers"""
    pattern = r'[Ss]ection\s+N/?A'
    sections = [c.section for c in chunks if c.section]

    if sections and re.search(pattern, text):
        text = re.sub(pattern, f"Section {sections[0]}", text)

    return text
```

### Static File Serving

```python
# Serve Next.js static build
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

---

## Frontend (Next.js)

### Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14 | React framework |
| React | 18 | UI library |
| TypeScript | 5 | Type safety |
| Tailwind CSS | 3 | Styling |

### Project Structure

```
frontend/
├── app/
│   ├── layout.tsx       # Root layout
│   ├── page.tsx         # Chat page
│   └── globals.css      # Global styles
├── components/
│   ├── ChatInput.tsx    # Message input
│   ├── ChatMessage.tsx  # Message display
│   └── SourceCard.tsx   # Citation display
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

### Main Chat Page

```tsx title="frontend/app/page.tsx"
'use client';

import { useState } from 'react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

interface Source {
  content: string;
  section: string;
  page_number: number;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input, k: 5 })
      });

      const data = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        sources: data.sources
      };
      setMessages(prev => [...prev, assistantMessage]);

    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <header className="bg-green-600 text-white p-4">
        <h1 className="text-xl font-bold">
          Nigeria Tax Act 2025 Assistant
        </h1>
      </header>

      {/* Messages */}
      <main className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <ChatMessage key={i} message={msg} />
        ))}
        {loading && <LoadingIndicator />}
      </main>

      {/* Input */}
      <footer className="border-t p-4">
        <ChatInput
          value={input}
          onChange={setInput}
          onSubmit={sendMessage}
          disabled={loading}
        />
      </footer>
    </div>
  );
}
```

### Chat Message Component

```tsx title="frontend/components/ChatMessage.tsx"
interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-3xl rounded-lg p-4 ${
          isUser
            ? 'bg-green-600 text-white'
            : 'bg-gray-100 text-gray-900'
        }`}
      >
        <p className="whitespace-pre-wrap">{message.content}</p>

        {/* Show sources for assistant messages */}
        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="mt-4 border-t pt-4">
            <h4 className="text-sm font-semibold mb-2">Sources:</h4>
            <div className="space-y-2">
              {message.sources.map((source, i) => (
                <SourceCard key={i} source={source} />
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
```

### Chat Input Component

```tsx title="frontend/components/ChatInput.tsx"
interface ChatInputProps {
  value: string;
  onChange: (value: string) => void;
  onSubmit: () => void;
  disabled: boolean;
}

export function ChatInput({
  value,
  onChange,
  onSubmit,
  disabled
}: ChatInputProps) {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSubmit();
    }
  };

  return (
    <div className="flex gap-2">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask about Nigerian tax law..."
        disabled={disabled}
        className="flex-1 rounded-lg border p-3 focus:outline-none focus:ring-2 focus:ring-green-500"
      />
      <button
        onClick={onSubmit}
        disabled={disabled || !value.trim()}
        className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50"
      >
        Send
      </button>
    </div>
  );
}
```

---

## Building the Frontend

### Development Mode

```bash
cd web/frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:3000`.

### Production Build

```bash
cd web/frontend
npm run build
npm run export
```

This generates static files in `out/` directory.

### Build Script

```bash title="web/build.sh"
#!/bin/bash
cd frontend
npm install
npm run build
cp -r out/* ../static/
cd ..
echo "Frontend build complete!"
```

---

## Configuration

### Next.js Configuration

```javascript title="frontend/next.config.js"
/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true
  }
}

module.exports = nextConfig
```

### Tailwind Configuration

```javascript title="frontend/tailwind.config.js"
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
        }
      }
    },
  },
  plugins: [],
}
```

---

## Running Locally

### Start Backend

```bash
cd web
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Start Frontend (Development)

```bash
cd web/frontend
npm run dev
```

### Full Stack (Production)

```bash
cd web
./build.sh  # Build frontend
uvicorn main:app --port 8000
```

Access at `http://localhost:8000`

---

## Environment Variables

```env title="web/.env"
# AWS Configuration
AWS_ACCESS_KEY=your_key
AWS_SECRET_KEY=your_secret
AWS_REGION=us-east-1

# Qdrant Configuration
QDRANT_CLOUD_URL=https://your-cluster.qdrant.io
QDRANT_APIKEY=your_api_key

# SageMaker Configuration
SAGEMAKER_ENDPOINT_INFERENCE=nigeria-tax-llama-v3

# Optional
DEBUG=false
```

---

## Next Steps

- [ML Pipelines](ml-pipelines.md) - Pipeline orchestration
- [REST API Reference](../api/rest-api.md) - API documentation
- [Docker Guide](../deployment/docker.md) - Containerization
