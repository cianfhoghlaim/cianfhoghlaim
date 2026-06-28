# Multi-stage Bun build for croilar-hono-api
# Build context = monorepo root
FROM oven/bun:1.3-slim AS builder
WORKDIR /repo

# Copy root manifests first (for caching the install layer)
COPY package.json bun.lock ./
COPY oideachais/ ./oideachais/
COPY tuatha/ ./tuatha/
COPY croilar/ ./croilar/

# Install all workspace deps
RUN bun install

# Build with Bun
RUN cd /repo/croilar/hono-api && bun build src/index.ts --outdir dist --target bun

# ---------------------------------------------------------------------------
FROM oven/bun:1.3-slim AS runner
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=4000

COPY --from=builder /repo/croilar/hono-api/dist /app/dist
COPY --from=builder /repo/croilar/hono-api/package.json ./
COPY --from=builder /repo/node_modules /app/node_modules

EXPOSE 4000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:4000/api/health || exit 1
CMD ["bun", "run", "dist/index.js"]
