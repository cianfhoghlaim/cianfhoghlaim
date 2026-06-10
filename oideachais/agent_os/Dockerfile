# =============================================================================
# OIDEACHAIS AGENTOS - Irish Education & Curriculum
# =============================================================================
# Production Dockerfile for the Oideachais AgentOS service.
#
# BUILD:
#   docker build -t oideachais-agentos -f agent_os/Dockerfile .
#
# RUN:
#   docker run -p 7772:7777 -e OPENAI_API_KEY=... oideachais-agentos
# =============================================================================

FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install dependencies
RUN uv pip install --system --no-cache -r pyproject.toml || \
    uv pip install --system --no-cache agno openai anthropic pydantic fastapi uvicorn httpx PyJWT

# =============================================================================
# Production Image
# =============================================================================
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Copy shared modules
COPY ../shared /app/sruth/shared

# Create storage directory
RUN mkdir -p /app/storage

# Environment
ENV PYTHONPATH=/app:/app/sruth
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 7777

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7777/health || exit 1

# Run the service
CMD ["uvicorn", "agent_os.main:app", "--host", "0.0.0.0", "--port", "7777"]
