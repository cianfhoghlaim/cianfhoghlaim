# Stagehand Local Server
# Multi-stage build for Node.js 20 with Chromium

FROM node:20-slim AS base

# Install dependencies for Chromium
RUN apt-get update && apt-get install -y \
    chromium \
    fonts-ipafont-gothic \
    fonts-wqy-zenhei \
    fonts-thai-tlwg \
    fonts-kacst \
    fonts-freefont-ttf \
    fonts-liberation \
    libxss1 \
    libgbm1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Set Chromium path for Playwright
ENV CHROME_BIN=/usr/bin/chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=true
ENV PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app

# Build stage
FROM base AS builder

COPY package*.json ./
RUN npm ci

COPY tsconfig.json ./
COPY src ./src

RUN npm run build

# Production stage
FROM base AS production

COPY package*.json ./
RUN npm ci --only=production

COPY --from=builder /app/dist ./dist

# Environment defaults
ENV PORT=3100
ENV HEADLESS=true
ENV MAX_SESSIONS=10
ENV SESSION_TTL_MS=300000

EXPOSE 3100

# Run as non-root user for security
RUN groupadd -r stagehand && useradd -r -g stagehand stagehand
RUN chown -R stagehand:stagehand /app
USER stagehand

CMD ["node", "dist/index.js"]
