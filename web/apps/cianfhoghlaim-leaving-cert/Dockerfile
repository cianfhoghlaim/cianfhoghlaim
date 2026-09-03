# Cianfhoghlaim Leaving Cert Portal — Docker image
# =============================================================================
# Build context: REPO ROOT (so we can reach the sibling cianfhoghlaim/
# monorepo for the @cianfhoghlaim/* workspace deps).
#
# Uses bun (the monorepo's package manager — apps use `workspace:*` protocol
# which npm rejects but bun supports natively).
# =============================================================================

FROM oven/bun:1-alpine

WORKDIR /app/cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert

# -----------------------------------------------------------------------------
# 1. Install dependencies via bun
# -----------------------------------------------------------------------------
# Copy manifests first so the install layer caches correctly.
COPY cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/package.json cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/bun.lock* cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/turbo.json ./
COPY cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web/package.json apps/web/
COPY cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/api/package.json apps/api/
COPY cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/packages/ packages/

RUN bun install

# -----------------------------------------------------------------------------
# 2. Copy source
# -----------------------------------------------------------------------------
WORKDIR /app
COPY cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/ /app/cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/

# -----------------------------------------------------------------------------
# 3. Expose + run
# -----------------------------------------------------------------------------
EXPOSE 3082 8787

WORKDIR /app/cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/apps/web
CMD ["bunx", "vite", "dev", "--host", "0.0.0.0", "--port", "3082"]