# Dockerfile for tuatha/ui (TanStack Start + Babylon.js front-end)
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY tsconfig.json ./
COPY vite.config.ts ./
COPY src/ src/
COPY public/ public/ 2>/dev/null || true
RUN npm install

# Generate route tree
RUN npx @tanstack/router-cli generate || true

# Build
RUN npm run build

# ---------------------------------------------------------------------------
FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/.output/ ./
COPY --from=builder /app/package.json ./
COPY --from=builder /app/dist/ ./dist/

EXPOSE 3004
CMD ["node", ".output/server/index.mjs"]
