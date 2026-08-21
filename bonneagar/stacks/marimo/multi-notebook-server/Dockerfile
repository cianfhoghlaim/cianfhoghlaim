# syntax=docker/dockerfile:1.4
# =============================================================================
# Marimo Multi-Notebook FastAPI Server — Dockerfile
# =============================================================================
# Per the canonical marimo Docker pattern from
# https://docs.marimo.io/guides/deploying/deploying_docker
#
# This image hosts all marimo notebooks in /notebooks/ as separate routes
# on a single ASGI app (FastAPI + uvicorn + marimo.create_asgi_app()).
#
# Build:
#   docker build -t marimo-multinb:latest \
#     -f bonneagar/stacks/marimo/multi-notebook-server/Dockerfile \
#     bonneagar/stacks/marimo/multi-notebook-server/
# =============================================================================

# Python 3.11-slim per the marimo canonical recommendation
FROM python:3.11-slim

# uv for fast package management (per the marimo canonical pattern)
COPY --from=ghcr.io/astral-sh/uv:0.4.20 /uv /bin/uv
ENV UV_SYSTEM_PYTHON=1

# Working directory
WORKDIR /app

# Install dependencies FIRST (for layer caching)
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

# Copy the FastAPI + marimo app
COPY main.py .

# Mount the marimo notebooks at runtime (via docker compose volume)
# The /notebooks directory is read-only — the marimo app does not write here.
RUN mkdir -p /notebooks

# Expose the marimo port (per the canonical pattern)
EXPOSE 2718

# Health check (per the marimo canonical pattern)
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:2718/health || exit 1

# Create non-root user (per the marimo canonical pattern)
RUN useradd -m app_user
USER app_user

# Entrypoint — uvicorn on :2718
CMD ["uvicorn", "main:api", "--host", "0.0.0.0", "--port", "2718"]
