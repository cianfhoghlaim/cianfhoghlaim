# =============================================================================
# Cianfhoghlaim Locket Shim — Dockerfile
# =============================================================================
# Drop-in replacement for bpbradley/locket:infisical that uses the correct
# camelCase field names for the Infisical v0.161+ REST API.
#
# Why this exists: locket v0.17.3 ships snake_case query params
# (project_id, secret_path, secret_type) but Infisical v0.161+ requires
# camelCase (projectId, secretPath, secretType). Every call returns 422,
# the locket falls back to "passthrough" mode, and writes the raw
# {{ infisical://... }} template to disk instead of the resolved values.
#
# Build:
#   docker build -t ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0 \
#     -f bonneagar/locket-shim/Dockerfile bonneagar/locket-shim
#
# Push:
#   docker push ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0
# =============================================================================

FROM python:3.12-alpine

LABEL org.opencontainers.image.title="cianfhoghlaim-locket-shim" \
      org.opencontainers.image.description="Cianfhoghlaim-internal Locket shim with camelCase Infisical v0.161+ compatibility" \
      org.opencontainers.image.source="https://github.com/cianfhoghlaim/cianfhoghlaim" \
      org.opencontainers.image.licenses="AGPL-3.0"

# Create non-root user matching locket's default (65532:65532)
RUN addgroup -g 65532 -S shim && adduser -u 65532 -S shim -G shim

WORKDIR /app

# Copy the shim source
COPY cianfhoghlaim-locket-shim.py /app/locket-shim.py

# Drop privileges
USER shim

# Default command is "watch" mode; can be overridden to "one-shot"
ENTRYPOINT ["python3", "/app/locket-shim.py"]
CMD ["watch"]