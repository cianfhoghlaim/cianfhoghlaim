# Dockerfile for oideachais/web/apps/web (TanStack Start front-end)
# Builds the front-end, serves via Node standalone server.
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
COPY tsconfig.json ./
COPY packages/ packages/
COPY apps/web/ apps/web/
RUN npm install

# Generate route tree
RUN cd apps/web && npx @tanstack/router-cli generate || true

# Build
RUN cd apps/web && npm run build

# ---------------------------------------------------------------------------
FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production

# Copy the built app
COPY --from=builder /app/apps/web/.output/ ./
COPY --from=builder /app/apps/web/package.json ./
COPY --from=builder /app/apps/web/dist/ ./dist/

EXPOSE 3001
CMD ["node", ".output/server/index.mjs"]
