# Installation

This guide walks you through setting up the Nigeria Tax Bill Chatbot for local development.

## Prerequisites

Before you begin, ensure you have the following installed:

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.11+ | Backend runtime |
| Node.js | 20+ | Frontend build |
| Poetry | Latest | Python dependency management |
| Docker | Latest | Containerization (optional) |
| Git | Latest | Version control |

## Cloud Accounts Required

You'll need accounts with the following services:

- [x] **AWS Account** - SageMaker, App Runner, ECR
- [x] **Qdrant Cloud** - Vector database (free tier available)
- [x] **HuggingFace** - Model hosting
- [x] **MongoDB Atlas** - Document storage (optional)

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/ocanthony4real/Nigeria-Tax-Bill-Chatbox.git
cd Nigeria-Tax-Bill-Chatbox
```

## Step 2: Install Python Dependencies

=== "Using Poetry (Recommended)"

    ```bash
    # Install Poetry if not already installed
    curl -sSL https://install.python-poetry.org | python3 -

    # Install dependencies
    poetry install

    # Activate virtual environment
    poetry shell
    ```

=== "Using pip"

    ```bash
    # Create virtual environment
    python -m venv venv

    # Activate virtual environment
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate

    # Install dependencies
    pip install -r requirements.txt
    ```

## Step 3: Install Frontend Dependencies

```bash
cd web/frontend
npm install
cd ../..
```

## Step 4: Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit the `.env` file with your credentials:

```env title=".env"
# AWS Configuration
AWS_ACCESS_KEY=your_access_key
AWS_SECRET_KEY=your_secret_key
AWS_REGION=us-east-1
AWS_ARN_ROLE=arn:aws:iam::YOUR_ACCOUNT:role/sagemaker-execution-role

# Qdrant Configuration
QDRANT_CLOUD_URL=https://your-cluster.qdrant.io
QDRANT_APIKEY=your_qdrant_api_key

# HuggingFace Configuration
HUGGINGFACE_ACCESS_TOKEN=hf_your_token

# SageMaker Endpoint
SAGEMAKER_ENDPOINT_INFERENCE=nigeria-tax-llama-v3

# Optional: MongoDB
MONGO_DATABASE_HOST=mongodb+srv://user:pass@cluster.mongodb.net/
```

!!! warning "Security Note"
    Never commit your `.env` file to version control. The `.gitignore` file should already exclude it.

---

## Step 5: Verify Installation

Run the following command to verify your installation:

```bash
python -c "from llm_engineering.settings import settings; print('Settings loaded successfully!')"
```

You should see:

```
Settings loaded successfully!
```

---

## Step 6: Build the Frontend

```bash
cd web
./build.sh  # On macOS/Linux
# OR
build.bat   # On Windows
```

---

## Optional: Docker Setup

If you prefer using Docker:

```bash
# Build the Docker image
docker build -t nigeria-tax-chatbot .

# Run the container
docker run -p 8000:8000 --env-file .env nigeria-tax-chatbot
```

---

## Troubleshooting

??? question "Poetry not found after installation"
    Add Poetry to your PATH:
    ```bash
    export PATH="$HOME/.local/bin:$PATH"
    ```

??? question "CUDA not available for PyTorch"
    For GPU support, install PyTorch with CUDA:
    ```bash
    pip install torch --index-url https://download.pytorch.org/whl/cu121
    ```

??? question "Qdrant connection failed"
    Verify your Qdrant Cloud URL and API key. Ensure the cluster is running and accessible.

??? question "SageMaker endpoint not responding"
    The endpoint may be scaled to zero. First request will take longer as the endpoint warms up.

---

## Next Steps

Now that you have the project installed, proceed to the [Quick Start](quickstart.md) guide to run the application.
