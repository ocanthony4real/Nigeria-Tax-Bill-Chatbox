# Troubleshooting

Solutions to common issues with the Nigeria Tax Bill Chatbot.

---

## Quick Diagnostics

Run this checklist first:

- [ ] Is the demo site accessible? [Test here](https://r8eqkf6a2g.us-east-1.awsapprunner.com/api/health)
- [ ] Are your environment variables set correctly?
- [ ] Is your Python version 3.11+?
- [ ] Do you have an active internet connection?

---

## Installation Issues

### Python version mismatch

!!! failure "Error"
    ```
    Python 3.10 is not supported. Please use Python 3.11+
    ```

!!! success "Solution"
    Install Python 3.11:

    === "Windows"
        ```bash
        # Download from python.org
        # Or use pyenv-win
        pyenv install 3.11.0
        pyenv local 3.11.0
        ```

    === "macOS"
        ```bash
        brew install python@3.11
        # Or use pyenv
        pyenv install 3.11.0
        ```

    === "Linux"
        ```bash
        sudo apt install python3.11
        # Or use pyenv
        pyenv install 3.11.0
        ```

---

### Poetry not found

!!! failure "Error"
    ```
    poetry: command not found
    ```

!!! success "Solution"
    Install Poetry and add to PATH:

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    export PATH="$HOME/.local/bin:$PATH"
    ```

    Add the export line to your shell profile (`~/.bashrc` or `~/.zshrc`).

---

### Dependency conflicts

!!! failure "Error"
    ```
    ERROR: Cannot install package-x and package-y because these package versions have conflicting dependencies.
    ```

!!! success "Solution"
    Use a fresh virtual environment:

    ```bash
    # Remove existing venv
    rm -rf venv .venv

    # Create new environment
    python -m venv venv
    source venv/bin/activate  # Linux/macOS
    # OR
    venv\Scripts\activate     # Windows

    # Install dependencies
    pip install -r requirements.txt
    ```

---

## Runtime Issues

### Connection to Qdrant failed

!!! failure "Error"
    ```
    QdrantConnectionError: Failed to connect to Qdrant at https://xyz.qdrant.io
    ```

!!! success "Solution"
    1. **Verify your Qdrant URL and API key:**
        ```bash
        curl -X GET "$QDRANT_CLOUD_URL/collections" \
          -H "api-key: $QDRANT_APIKEY"
        ```

    2. **Check if the cluster is active** in [Qdrant Cloud Console](https://cloud.qdrant.io/)

    3. **Verify environment variables:**
        ```python
        import os
        print(os.environ.get('QDRANT_CLOUD_URL'))
        print(os.environ.get('QDRANT_APIKEY')[:5] + '...')
        ```

---

### SageMaker endpoint not found

!!! failure "Error"
    ```
    ValidationError: Could not find endpoint 'nigeria-tax-llama-v3'
    ```

!!! success "Solution"
    1. **Check endpoint exists:**
        ```bash
        aws sagemaker describe-endpoint --endpoint-name nigeria-tax-llama-v3
        ```

    2. **If scaled to zero**, the endpoint may need to warm up. Wait 30 seconds and retry.

    3. **Verify AWS credentials:**
        ```bash
        aws sts get-caller-identity
        ```

    4. **Check region matches:**
        ```bash
        echo $AWS_REGION
        aws configure get region
        ```

---

### Endpoint warming up (503 error)

!!! failure "Error"
    ```
    HTTP 503: Model is warming up, please try again
    ```

!!! success "Solution"
    This is expected behavior with scale-to-zero. The endpoint needs time to start:

    1. **Wait 15-30 seconds** and retry
    2. **Implement retry logic:**
        ```python
        import time
        import requests

        for attempt in range(3):
            response = requests.post(url, json=data)
            if response.status_code == 200:
                break
            time.sleep(10 * (attempt + 1))
        ```

    3. **Keep warm** by pinging the endpoint periodically (adds cost)

---

### Out of memory

!!! failure "Error"
    ```
    CUDA out of memory. Tried to allocate X GiB
    ```

!!! success "Solution"
    1. **Reduce batch size** in inference:
        ```python
        # In main.py
        MAX_BATCH_SIZE = 1
        ```

    2. **Use a larger instance** (ml.g5.2xlarge instead of ml.g5.xlarge)

    3. **Enable model quantization** (already done by default)

---

### Embedding model download stuck

!!! failure "Error"
    ```
    Downloading: 100%|████████████| 1.34G/1.34G [stalled]
    ```

!!! success "Solution"
    1. **Check internet connection**

    2. **Use a mirror:**
        ```bash
        export HF_ENDPOINT=https://hf-mirror.com
        ```

    3. **Download manually:**
        ```bash
        huggingface-cli download BAAI/bge-large-en-v1.5 --local-dir ./models
        ```

---

## API Issues

### Invalid JSON response

!!! failure "Error"
    ```
    json.decoder.JSONDecodeError: Expecting value
    ```

!!! success "Solution"
    1. **Check request format:**
        ```bash
        curl -X POST http://localhost:8000/api/chat \
          -H "Content-Type: application/json" \
          -d '{"query": "What is VAT?", "k": 5}'
        ```

    2. **Verify Content-Type header** is `application/json`

    3. **Check for empty responses** - model may have returned nothing

---

### CORS errors in browser

!!! failure "Error"
    ```
    Access to fetch at 'http://localhost:8000' has been blocked by CORS policy
    ```

!!! success "Solution"
    The FastAPI app includes CORS middleware. If you still see errors:

    1. **Check your frontend URL** is allowed:
        ```python
        # In main.py
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "https://yourdomain.com"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
        ```

    2. **Clear browser cache** and retry

---

### Request timeout

!!! failure "Error"
    ```
    TimeoutError: Request timed out after 30 seconds
    ```

!!! success "Solution"
    1. **Increase timeout** on client side:
        ```python
        response = requests.post(url, json=data, timeout=120)
        ```

    2. **Check if cold start** - first requests take longer

    3. **Reduce number of chunks** retrieved:
        ```json
        {"query": "...", "k": 3}
        ```

---

## Deployment Issues

### Docker build fails

!!! failure "Error"
    ```
    ERROR: failed to solve: npm ERR! 404 Not Found
    ```

!!! success "Solution"
    1. **Check npm registry** is accessible:
        ```bash
        npm ping
        ```

    2. **Use npm mirror:**
        ```dockerfile
        RUN npm config set registry https://registry.npmmirror.com
        ```

    3. **Clear Docker cache:**
        ```bash
        docker builder prune -a
        docker build --no-cache -t app .
        ```

---

### App Runner deployment stuck

!!! failure "Error"
    ```
    Service status: OPERATION_IN_PROGRESS for > 30 minutes
    ```

!!! success "Solution"
    1. **Check operation status:**
        ```bash
        aws apprunner list-operations --service-arn YOUR_ARN
        ```

    2. **View logs:**
        ```bash
        aws logs tail /aws/apprunner/SERVICE_NAME/service --follow
        ```

    3. **Cancel and retry:**
        ```bash
        aws apprunner delete-service --service-arn YOUR_ARN
        # Then recreate
        ```

---

### GitHub Actions failing

!!! failure "Error"
    ```
    Error: Process completed with exit code 1
    ```

!!! success "Solution"
    1. **Check workflow logs** in GitHub Actions tab

    2. **Verify secrets are set:**
        - `AWS_ACCESS_KEY_ID`
        - `AWS_SECRET_ACCESS_KEY`
        - `APPRUNNER_SERVICE_ARN`

    3. **Test locally:**
        ```bash
        act -j build-and-push  # Using act CLI
        ```

---

## Performance Issues

### Slow response times

!!! warning "Symptom"
    Responses take >10 seconds consistently

!!! success "Solutions"

    1. **Check SageMaker instance** isn't overwhelmed:
        ```bash
        aws cloudwatch get-metric-statistics \
          --namespace AWS/SageMaker \
          --metric-name CPUUtilization \
          --dimensions Name=EndpointName,Value=nigeria-tax-llama-v3 \
          --start-time $(date -u -v-1H +%Y-%m-%dT%H:%M:%SZ) \
          --end-time $(date -u +%Y-%m-%dT%H:%M:%SZ) \
          --period 300 \
          --statistics Average
        ```

    2. **Reduce context size:**
        ```python
        MAX_CONTEXT_LENGTH = 4000  # Instead of 6000
        ```

    3. **Use fewer chunks:**
        ```json
        {"query": "...", "k": 3}  # Instead of 5
        ```

---

### High memory usage

!!! warning "Symptom"
    Application crashes with OOM or uses >90% memory

!!! success "Solutions"

    1. **Implement lazy loading** (already default)

    2. **Reduce batch sizes:**
        ```python
        EMBEDDING_BATCH_SIZE = 16  # Instead of 32
        ```

    3. **Increase App Runner memory:**
        ```yaml
        InstanceConfiguration:
          Memory: "8 GB"  # Instead of 4 GB
        ```

---

## Getting More Help

If your issue isn't listed here:

1. **Search existing issues:** [GitHub Issues](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox/issues)

2. **Check the logs:**
    ```bash
    # Local
    uvicorn main:app --log-level debug

    # App Runner
    aws logs tail /aws/apprunner/SERVICE/service --follow
    ```

3. **Create a new issue** with:
    - Error message (full traceback)
    - Steps to reproduce
    - Environment details (OS, Python version, etc.)
    - Relevant configuration

[:octicons-arrow-right-24: Report an Issue](https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox/issues/new){ .md-button }
