# Crypteolas AgentOS Dockerfile
# =============================
# Multi-stage build for production-ready DeFi agent service

# Stage 1: Build dependencies
FROM python:3.12-slim as builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files
COPY pyproject.toml ./
COPY ../shared/pyproject.toml ./shared/

# Create virtual environment and install dependencies
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install crypteolas dependencies
RUN uv pip install -e . --no-cache-dir


# Stage 2: Runtime
FROM python:3.12-slim as runtime

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . /app/sruth/crypteolas
COPY ../shared /app/sruth/shared

# Create storage directory
RUN mkdir -p /app/storage/sessions

# Set Python path
ENV PYTHONPATH="/app"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7777/health || exit 1

# Expose port (internal container port)
EXPOSE 7777

# Run the service
CMD ["uvicorn", "tuatha.crypteolas.agent_os.main:app", "--host", "0.0.0.0", "--port", "7777"]
