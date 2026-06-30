# =============================================================================
# HF WATCHDOG — Multi-stage Dockerfile
# =============================================================================
# Stage 1: build the cianfhoghlaim image (or pull the published dev image)
# Stage 2: minimal runtime that imports cianfhoghlaim.ci.hf_watchdog from
#           the cianfhoghlaim image
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: cianfhoghlaim (the code)
# -----------------------------------------------------------------------------
# In dev: use the local repo. In production: pin to a known good tag.
ARG CIANFHOGHLAIM_VERSION=dev
FROM ghcr.io/cianfhoghlaim/cianfhoghlaim:${CIANFHOGHLAIM_VERSION} AS cianfhoghlaim

# -----------------------------------------------------------------------------
# Stage 2: hf-watchdog runtime
# -----------------------------------------------------------------------------
FROM python:3.13-slim

WORKDIR /app

# Install curl (for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the watchdog code from the cianfhoghlaim image
# (the cianfhoghlaim/ci/hf_watchdog.py module is part of the package)
COPY --from=cianfhoghlaim /app/cianfhoghlaim/ci/hf_watchdog.py /app/watchdog.py

# Install the cianfhoghlaim package from the same image so the watchdog
# can import cianfhoghlaim.ocr.models.VISION_MODELS
COPY --from=cianfhoghlaim /app /app
RUN pip install --no-cache-dir /app || true

# Locket secrets are mounted at /run/secrets/locket/secrets.env
# (see sidecar.yaml). The watchdog reads SLACK_WEBHOOK_URL from there.

HEALTHCHECK --interval=24h --timeout=30s --retries=1 \
    CMD python /app/watchdog.py --once || exit 1

CMD ["python", "/app/watchdog.py", "--watch", "--interval", "86400"]
