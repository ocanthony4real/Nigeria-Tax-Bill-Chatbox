# Python SDK

A Python client library for the Nigeria Tax Bill Chatbot API.

## Installation

```bash
pip install requests
```

---

## Quick Start

```python
from nigeria_tax_client import TaxChatClient

client = TaxChatClient()
response = client.ask("What is the VAT rate in Nigeria?")

print(response.answer)
print(response.references)
```

---

## Client Implementation

```python title="nigeria_tax_client.py"
"""
Nigeria Tax Bill Chatbot Python Client

Usage:
    from nigeria_tax_client import TaxChatClient

    client = TaxChatClient()
    response = client.ask("What is the VAT rate?")
    print(response.answer)
"""

import requests
from dataclasses import dataclass
from typing import List, Optional
import time


@dataclass
class Source:
    """Source citation from the tax document"""
    content: str
    section: Optional[str]
    page_number: Optional[int]
    chapter: Optional[str]


@dataclass
class ChatResponse:
    """Response from the chat API"""
    answer: str
    references: List[str]
    sources: List[Source]


class TaxChatClient:
    """Client for Nigeria Tax Bill Chatbot API"""

    DEFAULT_URL = "https://r8eqkf6a2g.us-east-1.awsapprunner.com"

    def __init__(
        self,
        base_url: str = None,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        Initialize the client.

        Args:
            base_url: API base URL (default: production)
            timeout: Request timeout in seconds
            max_retries: Max retry attempts for 503 errors
        """
        self.base_url = base_url or self.DEFAULT_URL
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def health(self) -> dict:
        """
        Check API health.

        Returns:
            Health status dict

        Raises:
            requests.HTTPError: If request fails
        """
        response = self.session.get(
            f"{self.base_url}/api/health",
            timeout=self.timeout
        )
        response.raise_for_status()
        return response.json()

    def ask(
        self,
        query: str,
        k: int = 5,
        retry: bool = True
    ) -> ChatResponse:
        """
        Ask a question about Nigerian tax law.

        Args:
            query: The question to ask
            k: Number of source chunks to retrieve
            retry: Whether to retry on 503 errors

        Returns:
            ChatResponse with answer and sources

        Raises:
            requests.HTTPError: If request fails
            ValueError: If query is empty
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        payload = {"query": query.strip(), "k": k}

        for attempt in range(self.max_retries if retry else 1):
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return self._parse_response(response.json())

            if response.status_code == 503 and retry:
                wait_time = 2 ** attempt
                time.sleep(wait_time)
                continue

            response.raise_for_status()

        raise requests.HTTPError("Max retries exceeded")

    def _parse_response(self, data: dict) -> ChatResponse:
        """Parse API response into ChatResponse"""
        sources = [
            Source(
                content=s.get("content", ""),
                section=s.get("section"),
                page_number=s.get("page_number"),
                chapter=s.get("chapter")
            )
            for s in data.get("sources", [])
        ]

        return ChatResponse(
            answer=data.get("answer", ""),
            references=data.get("references", []),
            sources=sources
        )

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.session.close()
```

---

## Usage Examples

### Basic Usage

```python
from nigeria_tax_client import TaxChatClient

# Create client
client = TaxChatClient()

# Ask a question
response = client.ask("What is the corporate tax rate in Nigeria?")

# Print answer
print("Answer:", response.answer)

# Print references
print("\nReferences:")
for ref in response.references:
    print(f"  - {ref}")

# Print sources
print("\nSources:")
for source in response.sources:
    print(f"  Section {source.section} (p. {source.page_number})")
    print(f"  {source.content[:100]}...")
```

### With Context Manager

```python
with TaxChatClient() as client:
    response = client.ask("What are VAT exemptions?")
    print(response.answer)
```

### Custom Configuration

```python
# Local development
client = TaxChatClient(
    base_url="http://localhost:8000",
    timeout=120,
    max_retries=5
)

# Production with custom timeout
client = TaxChatClient(timeout=90)
```

### Error Handling

```python
from nigeria_tax_client import TaxChatClient
import requests

client = TaxChatClient()

try:
    response = client.ask("What is the penalty for tax evasion?")
    print(response.answer)

except requests.HTTPError as e:
    if e.response.status_code == 503:
        print("Model is warming up, please try again")
    else:
        print(f"API error: {e}")

except requests.Timeout:
    print("Request timed out")

except ValueError as e:
    print(f"Invalid input: {e}")
```

### Batch Questions

```python
questions = [
    "What is the VAT rate?",
    "What is the corporate tax rate?",
    "What are the penalties for late filing?",
]

client = TaxChatClient()

for question in questions:
    print(f"Q: {question}")
    response = client.ask(question)
    print(f"A: {response.answer}\n")
```

### Async Version

```python
import asyncio
import aiohttp

class AsyncTaxChatClient:
    """Async client for Nigeria Tax Bill Chatbot"""

    DEFAULT_URL = "https://r8eqkf6a2g.us-east-1.awsapprunner.com"

    def __init__(self, base_url: str = None):
        self.base_url = base_url or self.DEFAULT_URL

    async def ask(self, query: str, k: int = 5) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/chat",
                json={"query": query, "k": k}
            ) as response:
                return await response.json()


# Usage
async def main():
    client = AsyncTaxChatClient()
    response = await client.ask("What is the VAT rate?")
    print(response["answer"])

asyncio.run(main())
```

---

## Response Objects

### ChatResponse

| Attribute | Type | Description |
|-----------|------|-------------|
| `answer` | str | Generated answer with citations |
| `references` | List[str] | Section references |
| `sources` | List[Source] | Detailed source info |

### Source

| Attribute | Type | Description |
|-----------|------|-------------|
| `content` | str | Chunk text |
| `section` | str | Section number |
| `page_number` | int | Page in PDF |
| `chapter` | str | Chapter name |

---

## Best Practices

### 1. Reuse Client

```python
# Good - reuse client
client = TaxChatClient()
for q in questions:
    client.ask(q)

# Bad - create new client each time
for q in questions:
    TaxChatClient().ask(q)
```

### 2. Handle Cold Starts

```python
# Enable retries for cold start handling
client = TaxChatClient(max_retries=3)
```

### 3. Set Appropriate Timeout

```python
# Longer timeout for cold starts
client = TaxChatClient(timeout=120)
```

### 4. Use Context Manager

```python
with TaxChatClient() as client:
    # Session is properly closed
    response = client.ask("...")
```

---

## Next Steps

- [REST API Reference](rest-api.md) - Full API documentation
- [Quick Start](../getting-started/quickstart.md) - Get started
