# Dockerfile for oideachais/web/apps/api (Hono + oRPC API server)
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY tsconfig.json ./
COPY packages/ packages/
COPY apps/api/ apps/api/
RUN npm install

# Build the Hono server
RUN cd apps/api && npm run build

# ---------------------------------------------------------------------------
FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production
ENV PORT=8787

COPY --from=builder /app/apps/api/dist/ ./
COPY --from=builder /app/apps/api/package.json ./

EXPOSE 8787
CMD ["node", "dist/index.js"]
