# Dockerfile for croilar/apps/web (Vite SPA + Radix + i18n)
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
COPY tsconfig.json ./
COPY vite.config.ts ./
COPY wrangler.toml ./
COPY src/ src/
COPY public/ public/ 2>/dev/null || true
COPY config/ config/ 2>/dev/null || true
RUN npm install

RUN npm run build

# ---------------------------------------------------------------------------
FROM node:20-alpine AS runner

WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/dist/ ./dist/
COPY --from=builder /app/package.json ./

# Build output is a Vite SPA; serve via node static server
RUN npm install --global http-server 2>/dev/null || npm install http-server

EXPOSE 3003
CMD ["npx", "http-server", "dist", "-p", "3003", "-a", "0.0.0.0"]
