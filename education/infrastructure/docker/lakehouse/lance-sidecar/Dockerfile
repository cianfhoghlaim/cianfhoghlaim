# =============================================================================
# LANCE-NAMESPACE SIDECAR - Dockerfile
# =============================================================================
# FastAPI service wrapping the lance-namespace iceberg.py adapter.
# Registers Lance tables as "trojan horse" Iceberg tables in Lakekeeper.
# =============================================================================

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for pyarrow/lance
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security (before copying files)
RUN useradd --create-home --shell /bin/bash appuser

# Copy requirements first for layer caching (with correct ownership)
COPY --chown=appuser:appuser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code with correct ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose sidecar port
EXPOSE 8182

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:8182/health || exit 1

# Run the FastAPI server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8182"]
