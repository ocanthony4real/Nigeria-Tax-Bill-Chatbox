# Docker Guide

This guide covers Docker configuration for the Nigeria Tax Bill Chatbot.

## Overview

The project uses a multi-stage Docker build for efficient image creation.

---

## Dockerfile

```dockerfile title="web/Dockerfile"
# =============================================================================
# Stage 1: Frontend Build
# =============================================================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci --only=production

# Build frontend
COPY frontend/ ./
RUN npm run build

# =============================================================================
# Stage 2: Production Image
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Copy built frontend
COPY --from=frontend-builder /app/frontend/out ./static

# Environment configuration
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Building the Image

### Local Build

```bash
cd web
docker build -t nigeria-tax-chatbot .
```

### With Build Arguments

```bash
docker build \
  --build-arg PYTHON_VERSION=3.11 \
  --build-arg NODE_VERSION=20 \
  -t nigeria-tax-chatbot .
```

### Multi-platform Build

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t nigeria-tax-chatbot .
```

---

## Running the Container

### Basic Run

```bash
docker run -p 8000:8000 nigeria-tax-chatbot
```

### With Environment Variables

```bash
docker run -p 8000:8000 \
  -e AWS_ACCESS_KEY=your_key \
  -e AWS_SECRET_KEY=your_secret \
  -e AWS_REGION=us-east-1 \
  -e QDRANT_CLOUD_URL=https://xyz.qdrant.io \
  -e QDRANT_APIKEY=your_api_key \
  -e SAGEMAKER_ENDPOINT_INFERENCE=nigeria-tax-llama-v3 \
  nigeria-tax-chatbot
```

### With Environment File

```bash
docker run -p 8000:8000 --env-file .env nigeria-tax-chatbot
```

### Detached Mode

```bash
docker run -d -p 8000:8000 --name tax-chatbot --env-file .env nigeria-tax-chatbot
```

---

## Docker Compose

```yaml title="docker-compose.yml"
version: '3.8'

services:
  web:
    build:
      context: ./web
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - AWS_ACCESS_KEY=${AWS_ACCESS_KEY}
      - AWS_SECRET_KEY=${AWS_SECRET_KEY}
      - AWS_REGION=${AWS_REGION}
      - QDRANT_CLOUD_URL=${QDRANT_CLOUD_URL}
      - QDRANT_APIKEY=${QDRANT_APIKEY}
      - SAGEMAKER_ENDPOINT_INFERENCE=${SAGEMAKER_ENDPOINT_INFERENCE}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 5s
      retries: 3
    restart: unless-stopped

  # Optional: Local Qdrant for development
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    profiles:
      - dev

volumes:
  qdrant_data:
```

### Running with Compose

```bash
# Production
docker-compose up -d

# Development with local Qdrant
docker-compose --profile dev up -d
```

---

## Image Optimization

### .dockerignore

```text title=".dockerignore"
# Git
.git
.gitignore

# Python
__pycache__
*.pyc
*.pyo
.pytest_cache
.mypy_cache
venv
.venv

# Node
node_modules
.next

# IDE
.idea
.vscode
*.swp

# Build artifacts
dist
build
*.egg-info

# Documentation
docs
*.md
!README.md

# Tests
tests
*_test.py
test_*.py

# Environment
.env
.env.*

# Misc
*.log
.DS_Store
Thumbs.db
```

### Layer Caching

Order Dockerfile commands from least to most frequently changing:

```dockerfile
# 1. System dependencies (rarely change)
RUN apt-get update && apt-get install -y ...

# 2. Python dependencies (change occasionally)
COPY requirements.txt .
RUN pip install -r requirements.txt

# 3. Application code (changes frequently)
COPY . .
```

### Image Size Reduction

```dockerfile
# Use slim base image
FROM python:3.11-slim

# Install and cleanup in one layer
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Use --no-cache-dir for pip
RUN pip install --no-cache-dir -r requirements.txt
```

---

## Development Workflow

### Local Development

```bash
# Build
docker build -t nigeria-tax-chatbot:dev .

# Run with volume mount for hot reload
docker run -p 8000:8000 \
  -v $(pwd):/app \
  --env-file .env \
  nigeria-tax-chatbot:dev \
  uvicorn main:app --reload --host 0.0.0.0
```

### Testing

```bash
# Run tests in container
docker run --rm nigeria-tax-chatbot pytest

# Interactive shell
docker run -it --rm nigeria-tax-chatbot /bin/bash
```

---

## Pushing to ECR

```bash
# Authenticate
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Tag
docker tag nigeria-tax-chatbot:latest \
  YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/nigeria-tax-chatbot:latest

# Push
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/nigeria-tax-chatbot:latest
```

---

## Troubleshooting

### View Logs

```bash
docker logs nigeria-tax-chatbot
docker logs -f nigeria-tax-chatbot  # Follow
```

### Debug Container

```bash
# Enter running container
docker exec -it nigeria-tax-chatbot /bin/bash

# Start container with shell
docker run -it --entrypoint /bin/bash nigeria-tax-chatbot
```

### Common Issues

??? question "Container exits immediately"
    Check logs for errors:
    ```bash
    docker logs nigeria-tax-chatbot
    ```
    Often caused by missing environment variables.

??? question "Port already in use"
    Use a different port:
    ```bash
    docker run -p 8001:8000 nigeria-tax-chatbot
    ```

??? question "Out of memory"
    Increase Docker memory limit in Docker Desktop settings, or add:
    ```bash
    docker run -m 4g nigeria-tax-chatbot
    ```

---

## Next Steps

- [CI/CD Guide](cicd.md) - Automated builds
- [AWS Setup](aws-setup.md) - Deploy to AWS
