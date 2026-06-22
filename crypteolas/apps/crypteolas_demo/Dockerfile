# Crypto Analytics Frontend
# TanStack Start + CopilotKit + Ant Design Web3

FROM oven/bun:1.3.0-alpine AS base

WORKDIR /app

# Install dependencies (using bun instead of pnpm)
COPY package.json bun.lock* ./
RUN bun install --frozen-lockfile

# Development stage
FROM base AS dev
ENV NODE_ENV=development
EXPOSE 3000
CMD ["bun", "run", "dev", "--host", "0.0.0.0"]

# Build stage
FROM base AS build
COPY . .
RUN bun run build

# Production stage
FROM nginx:alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
