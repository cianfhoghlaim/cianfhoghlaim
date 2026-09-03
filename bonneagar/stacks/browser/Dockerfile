# Browser Agent Stack Dockerfile
# Self-hosted browser automation with ADK + Agno

FROM python:3.11-slim-bookworm

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Create app directory
WORKDIR /app

# Copy project files
COPY pyproject.toml .
COPY . .

# Install dependencies with uv
RUN uv sync --frozen

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3001/health || exit 1

# Run the server
CMD ["uv", "run", "python", "-m", "sruth.browser.server"]
