# Use CUDA runtime base image (Ubuntu 22.04 -> system python is 3.10)
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

# =========================
# Environment configuration
# =========================
ENV WORKSPACE_ROOT=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Poetry
ENV POETRY_VERSION=2.2.1
ENV POETRY_NO_INTERACTION=1

# =========================
# System dependencies + install Python 3.11
# =========================
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        software-properties-common \
        ca-certificates \
        curl \
        build-essential \
        gcc \
        lsb-release \
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt-get update -y && \
    apt-get install -y --no-install-recommends \
        python3.11 \
        python3.11-dev \
        python3.11-distutils \
        python3.11-venv \
        libglib2.0-0 \
        libnss3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Make python3 point to python3.11 and install pip for python3.11
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 2 && \
    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11 && \
    python3.11 -m pip install --upgrade pip setuptools wheel

# =========================
# Install Poetry using python3.11's pip and configure it
# =========================
RUN python3.11 -m pip install --no-cache-dir "poetry==${POETRY_VERSION}" && \
    python3.11 -m poetry config installer.max-workers 20 && \
    python3.11 -m poetry config virtualenvs.create false

# =========================
# Jupyter kernel registration (REQUIRED) using python3.11
# =========================
RUN python3.11 -m pip install --no-cache-dir jupyter ipykernel && \
    python3.11 -m ipykernel install \
      --sys-prefix \
      --name tax-bill \
      --display-name "tax-bill-kernel"

# =========================
# Application setup
# =========================
WORKDIR ${WORKSPACE_ROOT}

# Copy dependency definitions first (better layer caching)
COPY pyproject.toml poetry.lock ./

# Install only runtime dependencies (use poetry installed for python3.11)
RUN python3.11 -m poetry config virtualenvs.create false && \
    python3.11 -m poetry install \
        --no-root \
        --only main \
        --no-interaction \
        --no-ansi && \
    rm -rf /root/.cache/pypoetry

# =========================
# Copy application source
# =========================
COPY . .

# =========================
# Default command (override in ZenML / docker run)
# =========================
CMD ["python", "-m", "llm_engineering"]