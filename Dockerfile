# =========================
# Base image: CUDA for GPU training support
# =========================
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# =========================
# Environment configuration
# =========================
ENV WORKSPACE_ROOT=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Poetry configuration
ENV POETRY_VERSION=1.8.3
ENV POETRY_NO_INTERACTION=1

# =========================
# System dependencies + Python 3.11
# =========================
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        software-properties-common \
        ca-certificates \
        curl \
        build-essential \
        gcc \
        python3-dev \
        libglib2.0-dev \
        libnss3-dev \
        # Tesseract OCR for PDF processing
        tesseract-ocr \
        tesseract-ocr-eng \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update -y \
    && apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3.11-distutils \
        python3.11-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Make python3.11 the default and install pip
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 && \
    python3.11 -m pip install --upgrade pip setuptools wheel

# =========================
# Install Poetry and configure
# =========================
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION" && \
    poetry config installer.max-workers 20

WORKDIR $WORKSPACE_ROOT

# =========================
# Copy dependency files first (better layer caching)
# =========================
COPY pyproject.toml poetry.lock $WORKSPACE_ROOT

# =========================
# Install dependencies
# =========================
RUN poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-cache --only main && \
    poetry self add 'poethepoet[poetry_plugin]' && \
    rm -rf ~/.cache/pypoetry/cache/ && \
    rm -rf ~/.cache/pypoetry/artifacts/

# =========================
# Copy application source
# =========================
COPY . $WORKSPACE_ROOT
