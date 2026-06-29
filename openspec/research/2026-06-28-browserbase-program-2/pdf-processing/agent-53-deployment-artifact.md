# Unstract Stack — Full Compose YAML (Deployment Artifact)

**Companion to:** [`53-unstract-edu-extract-benchmark.md`](./53-unstract-edu-extract-benchmark.md) §6.1
**Date:** 2026-06-29

This file holds the verbatim Docker Compose YAML referenced from §6.1 of the benchmark
document. It is the full rewrite of the 2-service placeholder at
`infrastructure/stacks/unstract/compose.yaml`.

## `infrastructure/stacks/unstract/compose.yaml`

```yaml
name: unstract

x-unstract-env: &unstract-env
  DB_HOST: unstract-pg
  DB_PORT: 5432
  DB_USER: ${UNSTRACT_DB_USER:-unstract}
  DB_PASSWORD: ${UNSTRACT_DB_PASSWORD}
  DB_NAME: ${UNSTRACT_DB_NAME:-unstract}
  REDIS_HOST: unstract-redis
  REDIS_PORT: 6379
  CELERY_BROKER_URL: redis://unstract-redis:6379/0
  CELERY_RESULT_BACKEND: redis://unstract-redis:6379/1
  S3_ENDPOINT: ${S3_ENDPOINT:-http://garage:3900}
  S3_ACCESS_KEY: ${S3_ACCESS_KEY}
  S3_SECRET_KEY: ${S3_SECRET_KEY}
  S3_BUCKET: ${UNSTRACT_S3_BUCKET:-oideachais-unstract}
  LLM_DEFAULT_PROVIDER: litellm
  LLM_DEFAULT_MODEL: ${UNSTRACT_DEFAULT_MODEL:-claude-sonnet-4-20250514}
  LLM_API_KEY: ${LITELLM_MASTER_KEY}
  LLM_API_BASE: ${LITELLM_BASE_URL:-http://litellm:4000}
  FRONTEND_URL: https://unstract.cianfhoghlaim.ie
  ENABLE_POCKETID_SSO: "true"
  POCKETID_BASE_URL: ${POCKETID_BASE_URL:-https://pocketid.cianfhoghlaim.ie}

services:
  unstract-backend:
    image: unstract/unstract-backend:${UNSTRACT_VERSION:-latest}
    container_name: unstract-backend
    restart: unless-stopped
    environment:
      <<: *unstract-env
      DJANGO_SETTINGS_MODULE: unstract.settings
      ALLOWED_HOSTS: unstract.cianfhoghlaim.ie,localhost
    volumes: [unstract_data:/app/data]
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:8000/api/v1/health/"]
      interval: 30s; timeout: 10s; retries: 3; start_period: 90s
    deploy: { resources: { limits: { memory: 4G, cpus: '4' } } }
    networks: [cianfhoghlaim, lakehouse]
    depends_on:
      unstract-pg:    { condition: service_healthy }
      unstract-redis: { condition: service_healthy }

  unstract-frontend:
    image: unstract/unstract-frontend:${UNSTRACT_VERSION:-latest}
    container_name: unstract-frontend
    restart: unless-stopped
    environment:
      BACKEND_URL: http://unstract-backend:8000
      VITE_BASE_URL: /
    depends_on: { unstract-backend: { condition: service_healthy } }
    networks: [cianfhoghlaim]

  unstract-worker:
    image: unstract/unstract-backend:${UNSTRACT_VERSION:-latest}
    container_name: unstract-worker
    restart: unless-stopped
    command: ["celery", "-A", "unstract.celery", "worker",
              "--loglevel=info", "--concurrency=4"]
    environment: { <<: *unstract-env }
    volumes: [unstract_data:/app/data]
    deploy: { resources: { limits: { memory: 8G, cpus: '8' } } }
    networks: [cianfhoghlaim, lakehouse]
    depends_on:
      unstract-pg:    { condition: service_healthy }
      unstract-redis: { condition: service_healthy }

  unstract-beat:
    image: unstract/unstract-backend:${UNSTRACT_VERSION:-latest}
    container_name: unstract-beat
    restart: unless-stopped
    command: ["celery", "-A", "unstract.celery", "beat", "--loglevel=info"]
    environment: { <<: *unstract-env }
    networks: [cianfhoghlaim]
    depends_on:
      unstract-pg:    { condition: service_healthy }
      unstract-redis: { condition: service_healthy }

  unstract-llmwhisperer:
    image: unstract/llmwhisperer:${LLMWHISPERER_VERSION:-latest}
    container_name: unstract-llmwhisperer
    restart: unless-stopped
    environment: { WHISPERER_API_KEY: ${LLMWHISPERER_API_KEY} }
    deploy: { resources: { limits: { memory: 4G, cpus: '4' } } }
    networks: [cianfhoghlaim, lakehouse]

  unstract-redis:
    image: redis:7-alpine
    container_name: unstract-redis
    restart: unless-stopped
    command: ["redis-server", "--appendonly", "yes",
              "--maxmemory", "2gb", "--maxmemory-policy", "allkeys-lru"]
    volumes: [unstract_redis_data:/data]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s; retries: 5
    networks: [cianfhoghlaim]

  unstract-pg:
    image: postgres:16
    container_name: unstract-pg
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${UNSTRACT_DB_NAME:-unstract}
      POSTGRES_USER: ${UNSTRACT_DB_USER:-unstract}
      POSTGRES_PASSWORD: ${UNSTRACT_DB_PASSWORD}
      POSTGRES_SHARED_BUFFERS: 2GB
      POSTGRES_WORK_MEM: 256MB
    volumes: [unstract_pg_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL",
             "pg_isready -d ${UNSTRACT_DB_NAME:-unstract} -U ${UNSTRACT_DB_USER:-unstract}"]
      interval: 10s; retries: 5
    networks: [cianfhoghlaim]

volumes:
  unstract_data:      { driver: local }
  unstract_redis_data: { driver: local }
  unstract_pg_data:    { driver: local }

networks:
  cianfhoghlaim: { driver: bridge }
  lakehouse:     { name: lakehouse_lakehouse, external: true }
```

## Notes for the engineer applying this file

1. **Replace `compose.yaml` (49 lines → 175 lines).** Run `bun run validate-stacks`
   against the 6-file GOLD_STANDARD (`infrastructure/GOLD_STANDARD.md`).
2. **Reuse the existing `sidecar.yaml`** — the Locket pattern is correct; the
   only change is the volume of env vars being injected.
3. **Provision the Infisical entries** listed in the benchmark §6.3
   (`secrets.env`) before bringing the stack up. The `LLMWHISPERER_API_KEY` and
   `UNSTRACT_DB_PASSWORD` must be generated (`openssl rand -hex 32`) and
   pushed to `dev-baile` first.
4. **Pin the image** to `unstract/unstract-backend:v0.39.0` (not `latest`) to
   avoid upstream breaking changes during the benchmark run.
5. **Resource limits** are tuned for `cax41-hetzner` (16G mem budget per
   service). The Celery worker at 8G / 4 concurrency is the bottleneck;
   raise `--concurrency=6` only after monitoring shows <70% CPU.
6. **No `unstract-mcp` service in this file** — MCP is exposed as a sidecar
   on the backend at `/mcp/` per upstream. Wire as
   `http://unstract-backend:8000/mcp/` in the oideachais MCP registry.
