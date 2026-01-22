# =====================================================
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04



#FROM python:3.11-slim-bullseye AS release

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
# System dependencies
# =========================
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        python3-dev \
        libglib2.0-0 \
        libnss3 \
        curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =========================
# Install Poetry
# =========================
RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}" && \
    poetry config installer.max-workers 20 && \
    poetry config virtualenvs.create false

# =========================
# Jupyter kernel registration (REQUIRED)
# =========================
RUN pip install --no-cache-dir jupyter ipykernel \
 && python -m ipykernel install \
      --sys-prefix \
      --name python3 \
      --display-name "Python 3 (Custom Image)"

# =========================
# Application setup
# =========================
WORKDIR ${WORKSPACE_ROOT}

# Copy dependency definitions first (better layer caching)
COPY pyproject.toml poetry.lock ./

# Install only runtime dependencies
RUN poetry config virtualenvs.create false \
    && poetry install \
        --no-root \
        --only main \
        --no-interaction \
        --no-ansi \
    && rm -rf ~/.cache/pypoetry

# =========================
# Copy application source
# =========================
COPY . .

# =========================
# Default command (override in ZenML / docker run)
# =========================
CMD ["python", "-m", "llm_engineering"]
