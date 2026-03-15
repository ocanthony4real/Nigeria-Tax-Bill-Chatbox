#!/bin/bash
# Start script for the Nigeria Tax Chatbot

# Load environment variables - copy from .env or set these before running
export AWS_REGION=${AWS_REGION:-us-east-1}
export AWS_ACCESS_KEY=${AWS_ACCESS_KEY:-your_aws_access_key}
export AWS_SECRET_KEY=${AWS_SECRET_KEY:-your_aws_secret_key}
export QDRANT_CLOUD_URL=${QDRANT_CLOUD_URL:-your_qdrant_url}
export QDRANT_APIKEY=${QDRANT_APIKEY:-your_qdrant_api_key}
export SAGEMAKER_ENDPOINT_INFERENCE=${SAGEMAKER_ENDPOINT_INFERENCE:-nigeria-tax-llama}

# Activate venv and start server
cd "$(dirname "$0")"
source "../.venv/Scripts/activate" 2>/dev/null || source "../venv/bin/activate" 2>/dev/null
python -m uvicorn main:app --host 0.0.0.0 --port 8000
