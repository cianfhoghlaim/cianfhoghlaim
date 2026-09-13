# Browser Agent Stack Dockerfile
# Self-hosted browser automation with ADK + Agno
# Per the openspec change `2026-09-06-adk-gemini-deep-research-control-plane-v1`,
# the CMD is fixed to the correct module path (`sruth_browser`, underscore).

FROM python:3.12-slim-bookworm

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

# Install dependencies with uv (browser extras for google-genai + baml-py)
RUN uv sync --frozen --extra browser --extra agents --extra baml

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3001/health || exit 1

# Run the server
CMD ["uv", "run", "python", "-m", "sruth_browser.server"]
