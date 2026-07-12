# marimo-portal/Dockerfile
#
# Canonical marimo notebook deployment container for the British Isles
# Portal (per openspec/changes/2026-07-18-british-isles-portal-activation-v3/
# spec R15). Mirrors the official-media-marimo spec R4 deployment pattern.
#
# Usage:
#   docker build --build-arg NOTEBOOK_PATH=notebooks/12_subject_study_tools/mathematics.py \
#                --build-arg SUBJECT=mathematics \
#                --tag cianfhoghlaim/marimo-mathematics:latest .
#   docker run --rm -p 8080:8080 -e NOTEBOOK_PATH=notebooks/12_subject_study_tools/mathematics.py \
#                -e MARIMO_SERVER_HOST=0.0.0.0 \
#                cianfhoghlaim/marimo-mathematics:latest
#
# On Cloudflare Workers + Container, the container is bound to TCP 8080;
# wrangler.jsonc declares `port: 8080`.

ARG NOTEBOOK_PATH=notebooks/12_subject_study_tools/mathematics.py
ARG SUBJECT=mathematics

# ---------- builder stage: install uv + the marimo + BIEP dependencies ----------
FROM python:3.12-slim AS builder

# Install uv
RUN pip install --no-cache-dir uv==0.4.18

WORKDIR /app

# Copy the full repo so notebook `from notebooks...` imports work
COPY . /app

# PEP 723 inline-dep extraction: marimo is declared in the notebook's
# `# /// script` header per the CI pattern in
# `oideachais-marimo-dashboards/spec.md`. We rebuild that file into a
# pyproject.toml that uv can install from.
RUN uv venv /app/.venv && \
    uv pip install --no-cache \
        "marimo>=0.9.0" \
        "duckdb>=0.10.0" \
        "pandas>=2.0.0" \
        "ibis-framework[duckdb]>=9.0.0" \
        "lancedb>=0.4.0" \
        "pyarrow>=14.0.0" \
        "polars>=0.20.0" \
        "marimo[recommended]" \
        "altair>=5.0.0"

# ---------- runtime stage: minimal image with just marimo + uv ----------
FROM python:3.12-slim AS runtime

ARG NOTEBOOK_PATH
ARG SUBJECT

ENV NOTEBOOK_PATH=$NOTEBOOK_PATH
ENV SUBJECT=$SUBJECT
ENV MARIMO_SERVER_HOST=0.0.0.0
ENV MARIMO_SERVER_PORT=8080

# Install uv + copy the prebuilt venv from the builder
RUN pip install --no-cache-dir uv==0.4.18
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app
WORKDIR /app

EXPOSE 8080

# Health check — Cloudflare Container plumbing verifies TCP 8080
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('127.0.0.1', 8080)); s.close()" \
    || exit 1

# Run the per-subject marimo notebook
CMD ["sh", "-c", "PATH=/app/.venv/bin:$PATH exec marimo run --headless --host 0.0.0.0 --port 8080 /app/$NOTEBOOK_PATH"]
