FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
RUN uv run marimo --version

FROM python:3.12-slim AS runner
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY --from=builder /app /app
RUN uv sync --frozen --no-dev
EXPOSE 2718
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:2718/ || exit 1
CMD ["uv", "run", "marimo", "run", "--host=0.0.0.0", "--port=2718", "notebooks/aleyum/music_analytics.py"]
