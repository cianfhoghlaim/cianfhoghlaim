# Deployment Guide

Production deployment guide for the Tuath Celtic Educational MMO.

## Overview

The Tuath platform consists of:
- **Python API** (FastAPI) - Main backend
- **Rust API** (Axum) - Premium endpoints
- **SpacetimeDB** - Real-time multiplayer
- **Databases** - DuckDB, LanceDB, FalkorDB
- **Frontend** - TanStack Start (Cloudflare Workers)

---

## Architecture

```
                    ┌─────────────────────┐
                    │   Cloudflare CDN    │
                    │   (Workers/Pages)   │
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
     ┌────────▼────────┐  ┌────▼────┐  ┌────────▼────────┐
     │   TanStack UI   │  │  Assets │  │  SpacetimeDB    │
     │   (Workers)     │  │  (R2)   │  │   (WebSocket)   │
     └────────┬────────┘  └─────────┘  └─────────────────┘
              │
     ┌────────▼────────┐
     │   API Gateway   │
     │   (Traefik)     │
     └────────┬────────┘
              │
    ┌─────────┼─────────┐
    │                   │
┌───▼───┐          ┌────▼────┐
│ Python │          │  Rust   │
│  API   │          │   API   │
│ :8000  │          │  :8080  │
└───┬────┘          └────┬────┘
    │                    │
    └────────┬───────────┘
             │
    ┌────────┼────────┬────────────┐
    │        │        │            │
┌───▼───┐ ┌──▼──┐ ┌───▼───┐ ┌──────▼──────┐
│DuckDB │ │Lance│ │Falkor │ │ Embedding   │
│       │ │ DB  │ │  DB   │ │   Service   │
└───────┘ └─────┘ └───────┘ └─────────────┘
```

---

## Prerequisites

### Required Services

| Service | Purpose | Minimum Spec |
|---------|---------|--------------|
| Server | API hosting | 4 CPU, 16GB RAM, 100GB SSD |
| Redis | Caching, sessions | 1GB RAM |
| PostgreSQL | Session storage (optional) | 1GB RAM |

### Required Accounts

- Cloudflare (CDN, Workers, R2)
- SpacetimeDB Cloud (or self-hosted)
- Domain with DNS access

### Environment Variables

Create `.env.production`:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_ENV=production
SECRET_KEY=your-secret-key-here

# Database Paths
DUCKDB_PATH=/data/tuath.duckdb
LANCEDB_PATH=/data/lancedb
FALKORDB_URI=redis://falkordb:6379

# Embedding Service
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_BATCH_SIZE=100
HF_TOKEN=your-huggingface-token

# SpacetimeDB
SPACETIMEDB_URI=wss://spacetime.clockworklabs.net
SPACETIMEDB_MODULE=tuath-celtic-mmo

# Authentication
SIWE_DOMAIN=tuath.cianfhoghlaim.dev
SESSION_EXPIRY_HOURS=24

# Payments (x402)
PAYMENT_RECEIVER_ADDRESS=0x...
PAYMENT_CHAIN_ID=8453  # Base

# External APIs
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...

# Monitoring
SENTRY_DSN=https://...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
```

---

## Docker Compose Deployment

### docker-compose.yml

```yaml
version: "3.9"

services:
  # Python API
  api:
    build:
      context: .
      dockerfile: Dockerfile.api
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
    environment:
      - DUCKDB_PATH=/data/tuath.duckdb
      - LANCEDB_PATH=/data/lancedb
    env_file:
      - .env.production
    depends_on:
      - falkordb
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

  # Rust API (Premium)
  api-rs:
    build:
      context: ./api-rs
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - RUST_LOG=info
    env_file:
      - .env.production
    depends_on:
      - api
    restart: unless-stopped

  # FalkorDB (Knowledge Graph)
  falkordb:
    image: falkordb/falkordb:latest
    ports:
      - "6379:6379"
    volumes:
      - falkordb_data:/data
    command: >
      --loadmodule /usr/lib/redis/modules/falkordb.so
      --save 60 1
      --appendonly yes
    restart: unless-stopped

  # Redis (Caching)
  redis:
    image: redis:7-alpine
    ports:
      - "6380:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

  # Dagster (Pipeline Orchestration)
  dagster:
    build:
      context: .
      dockerfile: Dockerfile.dagster
    ports:
      - "3000:3000"
    volumes:
      - ./data:/data
      - ./dagster_home:/opt/dagster/dagster_home
    environment:
      - DAGSTER_HOME=/opt/dagster/dagster_home
    env_file:
      - .env.production
    restart: unless-stopped

  # Traefik (Reverse Proxy)
  traefik:
    image: traefik:v3.0
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik:/etc/traefik
      - ./certs:/certs
    command:
      - --api.dashboard=true
      - --providers.docker=true
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --certificatesresolvers.letsencrypt.acme.email=admin@cianfhoghlaim.dev
      - --certificatesresolvers.letsencrypt.acme.storage=/certs/acme.json
      - --certificatesresolvers.letsencrypt.acme.httpchallenge.entrypoint=web
    restart: unless-stopped

volumes:
  falkordb_data:
  redis_data:
```

### Dockerfile.api

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY tuath/ ./tuath/

# Install dependencies
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with uvicorn
CMD ["uv", "run", "uvicorn", "tuath.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile.api-rs

```dockerfile
FROM rust:1.75 as builder

WORKDIR /app
COPY . .

RUN cargo build --release

FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    ca-certificates \
    libssl3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /app/target/release/tuath-api-rs /usr/local/bin/

EXPOSE 8080

CMD ["tuath-api-rs"]
```

---

## Database Setup

### DuckDB Initialization

```python
# scripts/init_duckdb.py

import duckdb

def init_database(path: str):
    """Initialize DuckDB with required schemas."""

    conn = duckdb.connect(path)

    # Curriculum tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS curriculum (
            id VARCHAR PRIMARY KEY,
            title VARCHAR,
            content TEXT,
            language VARCHAR,
            level VARCHAR,
            nation VARCHAR,
            learning_outcomes VARCHAR[],
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Mythology tables
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mythology_characters (
            id VARCHAR PRIMARY KEY,
            name VARCHAR,
            celtic_name VARCHAR,
            tradition VARCHAR,
            role VARCHAR,
            description TEXT,
            relationships JSON
        )
    """)

    # Session tracking
    conn.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            session_id VARCHAR PRIMARY KEY,
            address VARCHAR,
            player_id VARCHAR,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    """)

    # Free usage tracking
    conn.execute("""
        CREATE TABLE IF NOT EXISTS usage_tracking (
            id BIGINT PRIMARY KEY,
            player_id VARCHAR,
            resource_type VARCHAR,
            date DATE,
            count INTEGER DEFAULT 0,
            UNIQUE(player_id, resource_type, date)
        )
    """)

    conn.close()

if __name__ == "__main__":
    init_database("/data/tuath.duckdb")
```

### LanceDB Index Creation

```python
# scripts/init_lancedb.py

import lancedb

def init_lancedb(path: str):
    """Initialize LanceDB with required tables."""

    db = lancedb.connect(path)

    # Create curriculum table with embedding schema
    if "curriculum" not in db.table_names():
        db.create_table(
            "curriculum",
            data=[{
                "id": "placeholder",
                "content": "placeholder",
                "embedding": [0.0] * 1024,  # BGE-M3 dimension
                "metadata": {},
            }],
            mode="overwrite",
        )

        # Create HNSW index
        table = db.open_table("curriculum")
        table.create_index(
            "embedding",
            index_type="IVF_HNSW_SQ",
            num_partitions=256,
        )

    # Create mythology table
    if "mythology" not in db.table_names():
        db.create_table(
            "mythology",
            data=[{
                "id": "placeholder",
                "content": "placeholder",
                "embedding": [0.0] * 1024,
                "metadata": {},
            }],
            mode="overwrite",
        )

if __name__ == "__main__":
    init_lancedb("/data/lancedb")
```

### FalkorDB Graph Setup

```python
# scripts/init_falkordb.py

from falkordb import FalkorDB

def init_graph(uri: str):
    """Initialize FalkorDB knowledge graph."""

    client = FalkorDB.from_url(uri)
    graph = client.select_graph("tuath")

    # Create indexes
    graph.query("CREATE INDEX ON :Character(name)")
    graph.query("CREATE INDEX ON :Story(title)")
    graph.query("CREATE INDEX ON :Location(name)")
    graph.query("CREATE INDEX ON :Document(id)")

    # Create constraints
    graph.query("CREATE CONSTRAINT ON (c:Character) ASSERT c.id IS UNIQUE")
    graph.query("CREATE CONSTRAINT ON (s:Story) ASSERT s.id IS UNIQUE")

if __name__ == "__main__":
    init_graph("redis://localhost:6379")
```

---

## Cloudflare Deployment

### Workers (TanStack Start)

```bash
# Build frontend
cd ui
pnpm build

# Deploy to Cloudflare Workers
pnpm wrangler deploy
```

### wrangler.toml

```toml
name = "tuath-ui"
main = "dist/_worker.js"
compatibility_date = "2024-01-01"
compatibility_flags = ["nodejs_compat"]

[site]
bucket = "./dist"

[vars]
API_URL = "https://api.tuath.cianfhoghlaim.dev"

[[r2_buckets]]
binding = "ASSETS"
bucket_name = "tuath-assets"
```

### R2 Asset Upload

```bash
# Upload game assets
wrangler r2 object put tuath-assets/textures/ --file ./public/textures/ --recursive
wrangler r2 object put tuath-assets/audio/ --file ./public/audio/ --recursive
wrangler r2 object put tuath-assets/models/ --file ./public/models/ --recursive
```

---

## SpacetimeDB Deployment

### Publishing Module

```bash
cd server

# Build
spacetime build

# Publish to cloud
spacetime publish tuath-celtic-mmo

# Or self-hosted
spacetime publish tuath-celtic-mmo --host wss://spacetime.your-server.com
```

### Self-Hosted SpacetimeDB

```yaml
# spacetimedb.docker-compose.yml

services:
  spacetimedb:
    image: clockworklabs/spacetimedb:latest
    ports:
      - "3000:3000"
    volumes:
      - spacetimedb_data:/var/lib/spacetimedb
    environment:
      - SPACETIMEDB_LOG_LEVEL=info
    restart: unless-stopped

volumes:
  spacetimedb_data:
```

---

## SSL/TLS Configuration

### Traefik with Let's Encrypt

```yaml
# traefik/traefik.yml

entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https

  websecure:
    address: ":443"

certificatesResolvers:
  letsencrypt:
    acme:
      email: admin@cianfhoghlaim.dev
      storage: /certs/acme.json
      httpChallenge:
        entryPoint: web

providers:
  docker:
    exposedByDefault: false
```

### Service Labels

```yaml
services:
  api:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.api.rule=Host(`api.tuath.cianfhoghlaim.dev`)"
      - "traefik.http.routers.api.entrypoints=websecure"
      - "traefik.http.routers.api.tls.certresolver=letsencrypt"
      - "traefik.http.services.api.loadbalancer.server.port=8000"
```

---

## Monitoring

### Health Checks

```python
# api/routes/health.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    version: str
    databases: dict
    services: dict

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check."""

    return HealthResponse(
        status="healthy",
        version="1.0.0",
        databases={
            "duckdb": await check_duckdb(),
            "lancedb": await check_lancedb(),
            "falkordb": await check_falkordb(),
        },
        services={
            "embedding": await check_embedding_service(),
            "spacetimedb": await check_spacetimedb(),
        },
    )
```

### Prometheus Metrics

```python
# api/middleware/metrics.py

from prometheus_client import Counter, Histogram, generate_latest
from fastapi import Response

REQUEST_COUNT = Counter(
    "tuath_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "tuath_http_request_duration_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
)

@router.get("/metrics")
async def metrics():
    return Response(
        content=generate_latest(),
        media_type="text/plain",
    )
```

### Logging

```python
# api/logging_config.py

import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure JSON logging for production."""

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )
    handler.setFormatter(formatter)

    logging.root.handlers = [handler]
    logging.root.setLevel(logging.INFO)

    # Quiet noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
```

---

## Backup Strategy

### Automated Backups

```bash
#!/bin/bash
# scripts/backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/backups

# DuckDB
cp /data/tuath.duckdb $BACKUP_DIR/duckdb_$DATE.db

# LanceDB
tar -czf $BACKUP_DIR/lancedb_$DATE.tar.gz /data/lancedb

# FalkorDB
docker exec falkordb redis-cli BGSAVE
sleep 5
cp /var/lib/docker/volumes/falkordb_data/_data/dump.rdb $BACKUP_DIR/falkordb_$DATE.rdb

# Upload to S3/R2
aws s3 sync $BACKUP_DIR s3://tuath-backups/

# Cleanup old local backups (keep 7 days)
find $BACKUP_DIR -mtime +7 -delete
```

### Cron Schedule

```cron
# /etc/cron.d/tuath-backup

# Daily backup at 3 AM
0 3 * * * root /opt/tuath/scripts/backup.sh >> /var/log/tuath-backup.log 2>&1
```

---

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.scale.yml

services:
  api:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: "2"
          memory: 4G
```

### Load Balancer Configuration

```yaml
services:
  traefik:
    labels:
      - "traefik.http.services.api.loadbalancer.sticky.cookie=true"
      - "traefik.http.services.api.loadbalancer.sticky.cookie.name=tuath_session"
```

---

## Production Checklist

### Security
- [ ] SSL/TLS enabled for all endpoints
- [ ] CORS configured for allowed origins
- [ ] Rate limiting enabled
- [ ] Secret keys rotated from defaults
- [ ] Database access restricted to internal network

### Performance
- [ ] HNSW indexes created for vector tables
- [ ] Redis caching enabled
- [ ] Gzip compression enabled
- [ ] Static assets served from CDN

### Reliability
- [ ] Health checks configured
- [ ] Automated backups running
- [ ] Log aggregation set up
- [ ] Alerting configured

### Monitoring
- [ ] Prometheus metrics exposed
- [ ] Grafana dashboards created
- [ ] Error tracking (Sentry) enabled
- [ ] Uptime monitoring active

---

## Related Documentation

- [Architecture](./ARCHITECTURE.md) - System design overview
- [API Reference](./api/README.md) - Endpoint documentation
- [Performance Tuning](./guides/PERFORMANCE_TUNING.md) - Optimization guide
- [Adding Data Sources](./guides/ADDING_DATA_SOURCES.md) - Pipeline setup
