# Multi-stage Bun build for croilar-hono-api
FROM oven/bun:1.3-slim AS builder
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile --production
COPY . .
RUN bun build src/index.ts --outdir dist --target bun

FROM oven/bun:1.3-slim AS runner
WORKDIR /app
COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/node_modules /app/node_modules
EXPOSE 4000
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:4000/api/health || exit 1
CMD ["bun", "run", "dist/index.js"]
