# -------- GPU base (CUDA runtime, small & stable) --------
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04

# -------- Environment hygiene --------
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# -------- System deps --------
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# -------- Make python default --------
RUN ln -sf /usr/bin/python3 /usr/bin/python

# -------- Minimal Python deps --------
RUN pip install --no-cache-dir \
    ipykernel \
    jupyter-client

# -------- Register kernel (THIS IS THE KEY PART) --------
RUN python -m ipykernel install \
    --sys-prefix \
    --name gpu-minimal \
    --display-name "GPU Minimal Kernel"

# -------- SageMaker Studio expectations --------
# Studio runs as root by default, so no USER switch needed
WORKDIR /root

# -------- Keep container alive --------
CMD ["bash"]
