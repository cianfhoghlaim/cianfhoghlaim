# =============================================================================
# BROWSER AGENTOS - Web Automation Orchestration
# =============================================================================
# Production Dockerfile for the Browser AgentOS service.
# Orchestrates Stagehand, Crawl4AI, and Skyvern backends.
#
# BUILD:
#   docker build -t browser-agentos -f agent_os/Dockerfile .
#
# RUN:
#   docker run -p 7773:7777 -e OPENAI_API_KEY=... -e BROWSERBASE_API_KEY=... browser-agentos
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

# Install dependencies (including browser automation libs)
RUN uv pip install --system --no-cache -r pyproject.toml || \
    uv pip install --system --no-cache agno openai anthropic pydantic fastapi uvicorn httpx PyJWT playwright crawl4ai

# Install Playwright browsers
RUN playwright install chromium --with-deps || true

# =============================================================================
# Production Image
# =============================================================================
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies (including browser deps)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright

# Copy application code
COPY . .

# Copy shared modules
COPY ../shared /app/sruth/shared

# Create storage directory
RUN mkdir -p /app/storage

# Environment
ENV PYTHONPATH=/app:/app/sruth
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

# Expose port
EXPOSE 7777

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7777/health || exit 1

# Run the service
CMD ["uvicorn", "agent_os.main:app", "--host", "0.0.0.0", "--port", "7777"]
