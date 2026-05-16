# =============================================================================
# OIDEACHAIS API - Dockerfile
# =============================================================================
# FastAPI backend for Celtic Education Platform with AG-UI streaming.
# Uses uv for fast dependency management.
# =============================================================================

FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy all files for dependency resolution (needed for local paths like ./browser)
COPY . .

# Create virtual environment and install dependencies
RUN uv sync --frozen --no-dev --no-editable

# =============================================================================
# RUNTIME STAGE
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create package structure for absolute oideachais imports
RUN mkdir -p /opt/packages && ln -s /app /opt/packages/oideachais

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser . .

# Create data directories
RUN mkdir -p /app/storage/data && chown -R appuser:appuser /app/storage

# Switch to non-root user
USER appuser

# Set PATH to use virtual environment
ENV PATH="/app/.venv/bin:$PATH"
# Set PYTHONPATH to include the packages directory and current app
ENV PYTHONPATH="/opt/packages:/app"

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:8000/health || exit 1

# Run the FastAPI server
CMD ["uvicorn", "api.main_simple:app", "--host", "0.0.0.0", "--port", "8000"]
