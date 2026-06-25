FROM python:3.12-slim AS builder
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen
COPY . .
RUN uv run python -c "from definitions import defs; print('OK', len(defs.get_asset_graph().get_all_asset_keys()))"

FROM python:3.12-slim AS runner
WORKDIR /app
RUN pip install --no-cache-dir uv
COPY --from=builder /app /app
RUN uv sync --frozen --no-dev
ENV DAGSTER_HOME=/opt/dagster/dagster_home
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:3000/server_info || exit 1
CMD ["uv", "run", "dagster-webserver", "-h", "0.0.0.0", "-p", "3000", "-w", "/app"]
