# Crypto Analytics Frontend
# TanStack Start + CopilotKit + Ant Design Web3

FROM node:22-alpine AS base

WORKDIR /app

# Install dependencies
COPY package.json pnpm-lock.yaml* ./
RUN corepack enable pnpm && pnpm install --frozen-lockfile

# Development stage
FROM base AS dev
ENV NODE_ENV=development
EXPOSE 3000
CMD ["pnpm", "dev", "--host", "0.0.0.0"]

# Build stage
FROM base AS build
COPY . .
RUN pnpm build

# Production stage
FROM nginx:alpine AS prod
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
