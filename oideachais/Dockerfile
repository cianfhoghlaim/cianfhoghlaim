# =============================================================================
# OIDEACHAIS API - Dockerfile
# =============================================================================
# FastAPI backend for Celtic Education Platform with AG-UI streaming.
# Uses uv for fast dependency management.
#
# NOTE: As of 2026-06-11, the `api/` package was moved from
# `oideachais/data_platform/api/` up to `oideachais/api/`. The CMD below
# uses `--app-dir /app/oideachais` and `api.main_simple:app` accordingly.
# =============================================================================

FROM python:3.13-slim AS builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy all files for dependency resolution (needed for sibling uv workspace
# members like sruth-browser, codeolas declared at the repo root pyproject.toml)
COPY . .

# Sync the oideachais sub-workspace (the actual application code).
# This populates /app/.venv with FastAPI, uvicorn, dlt, dagster, etc.
# `uv sync` is non-destructive when the lock is fresh, but we delete any
# existing .venv to ensure the shebangs/python symlinks are container-correct.
RUN rm -rf /app/oideachais/.venv /app/.venv
RUN cd /app/oideachais && uv sync --no-dev --no-editable

# =============================================================================
# RUNTIME STAGE
# =============================================================================
FROM python:3.13-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create package structure for absolute oideachais imports
RUN mkdir -p /opt/packages && ln -s /app /opt/packages/oideachais

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy virtual environment from builder (uses Python 3.13 from uv).
# The runtime base image is python:3.13-slim so the venv is self-contained.
COPY --from=builder /app/.venv /app/.venv

# Make the venv readable by appuser (builder creates files as root)
RUN chmod -R a+rX /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Create data directories (writable by appuser; named volumes mount here)
# MUST be done as root before USER appuser; the data_platform/ subdir
# was moved up to oideachais/ on 2026-06-11 so it's NOT created here.
RUN mkdir -p /app/oideachais/storage/data && chown -R appuser:appuser /app/oideachais/storage

# Switch to non-root user
USER appuser

# Set PATH to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"
# Set PYTHONPATH so `api.main_simple:app` resolves from /app/oideachais/
# (api/ was moved up from data_platform/api/ on 2026-06-11)
ENV PYTHONPATH="/opt/packages:/app:/app/oideachais"

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:8000/health || exit 1

# Run the FastAPI server. `--app-dir` lets uvicorn find the `api` package
# even though WORKDIR is /app (the symlink /opt/packages/oideachais → /app
# also works but `--app-dir` is more explicit).
WORKDIR /app
CMD ["uvicorn", "--app-dir", "/app/oideachais", "api.main_simple:app", "--host", "0.0.0.0", "--port", "8000"]
