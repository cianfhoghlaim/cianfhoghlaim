FROM oven/bun:1.3-slim AS builder
WORKDIR /app
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile
COPY . .
RUN bun run build

FROM oven/bun:1.3-slim AS runner
WORKDIR /app
COPY --from=builder /app/dist /app/dist
COPY --from=builder /app/node_modules /app/node_modules
EXPOSE 3003
HEALTHCHECK --interval=30s --timeout=5s CMD curl -f http://localhost:3003/ || exit 1
CMD ["bun", "run", "start"]
