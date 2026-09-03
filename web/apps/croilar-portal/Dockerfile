# =============================================================================
# Aleyum Portal - TanStack Start Application
# =============================================================================
# Build stage using Bun for fast dependency installation
FROM oven/bun:1.2-alpine AS builder

WORKDIR /app

# Copy package files
COPY package.json bun.lock* ./

# Install dependencies
RUN bun install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN bun run build

# =============================================================================
# Production stage using Node.js Alpine
# =============================================================================
FROM node:22-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Create non-root user
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 portal

# Copy built application
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/package.json ./

# Set ownership
RUN chown -R portal:nodejs /app

USER portal

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
