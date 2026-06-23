# =============================================================================
# MLX-OMNI - Apple Silicon MLX model server
# =============================================================================
# Builds madroidmaq/mlx-omni-server with FastAPI + MLX
# =============================================================================

FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        git build-essential curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python dependency management
RUN pip install --no-cache-dir uv

WORKDIR /app

# Clone mlx-omni-server
RUN git clone https://github.com/madroidmaq/mlx-omni-server.git /app/src

WORKDIR /app/src

# Install dependencies
RUN uv pip install --system --no-cache -e ".[server]"

# MLX is Apple-Silicon-only; this Dockerfile will only run on macOS hosts
# (or via docker buildx --platform=linux/arm64 with MLX emulated — not for prod)
RUN python -c "import mlx.core as mx; print(f'mlx version: {mx.__version__}')" || \
    echo "WARNING: mlx not available — this image will not start on non-Apple hosts"

EXPOSE 10240

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=60s \
    CMD curl -sf http://localhost:10240/v1/models || exit 1

CMD ["mlx-omni", "serve", "--host", "0.0.0.0", "--port", "10240"]
