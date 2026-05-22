# =============================================================================
# OIDEACHAIS FRONTEND - Dockerfile
# =============================================================================
# Vite + React frontend for Celtic Education Platform.
# Multi-stage build for production optimization.
# =============================================================================

FROM oven/bun:1-alpine AS builder

WORKDIR /app

# Copy dependency files first for layer caching
COPY package.json bun.lock* ./

# Install dependencies
RUN bun install

# Copy source code
COPY . .

# Build arguments for environment
ARG VITE_API_URL=http://localhost:8000
ARG VITE_API_PUBLIC_URL=http://localhost:8000

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_API_PUBLIC_URL=$VITE_API_PUBLIC_URL

# Build the application
RUN bunx vite build

# =============================================================================
# PRODUCTION STAGE - Serve with lightweight server
# =============================================================================
FROM node:20-alpine

WORKDIR /app

# Install serve for static file serving
RUN npm install -g serve

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S -u 1001 -G nodejs appuser

# Copy built assets from builder
COPY --from=builder --chown=appuser:nodejs /app/dist ./dist

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Serve the built application
CMD ["serve", "-s", "dist", "-l", "3000"]
