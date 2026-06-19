---
truth: partial
merged_from:
  - docs/06-infrastructure/DOCKER_COMPOSE_ARCHITECTURE.md
  - docs/06-infrastructure/DOCKER_COMPOSE_QUICKSTART.md
  - docs/06-infrastructure/DOCKER_COMPOSE_REFERENCE.md
  - docs/06-infrastructure/Docker Compose Setup for Data Tools.md
---

# Docker Compose — Master Reference

> Consolidated from 4 source documents. Original content preserved below.

---

## From: DOCKER_COMPOSE_REFERENCE.md (canonical)

# Docker Compose Stacks Analysis - Hackathon Project

## Executive Summary

This document provides a comprehensive analysis of 18 Docker Compose stacks in `/infrastructure/compose/`. The stacks are organized by functional category: Infrastructure, Data Processing, LLM Operations, Package Management, and Observability.

---

## 1. INFRASTRUCTURE FOUNDATION

### 1.1 Supabase (PostgreSQL + Full Stack Backend)
**Type**: Core database infrastructure
**Location**: `/compose/supabase/`
**Compose File**: `docker-compose.yml` (~230+ services/components)

**Key Services**:
- PostgreSQL 15 database
- Kong API Gateway (REST/GraphQL proxy)
- GoTrue (Auth server)
- PostgREST (auto-generated REST API)
- Realtime (WebSocket)
- Studio (Web Dashboard)
- Logflare (Analytics)

**Environment Variables**:
| Variable | Purpose | Example |
|----------|---------|---------|
| POSTGRES_PASSWORD | DB password | op://komodo/supabase/... |
| JWT_SECRET | Authentication | ef6dae4ba7c... |
| ANON_KEY | Public JWT key | eyJhbGciOiJIUzI1NiIs... |
| SERVICE_ROLE_KEY | Service JWT key | eyJhbGciOiJIUzI1NiIs... |
| POSTGRES_HOST | DB host | db |
| POSTGRES_PORT | DB port | 5432 |
| KONG_HTTP_PORT | API port | 8000 |
| SITE_URL | Frontend URL | http://localhost:3000 |

**API Endpoints**:
- REST API: `http://localhost:8000/rest/v1`
- GraphQL: `http://localhost:8000/graphql/v1`
- Auth: `http://localhost:8000/auth/v1`
- Realtime: WebSocket at port 8000
- Dashboard: `http://localhost:3000`

**Dependencies**: None (standalone)
**Build Requirements**: None (pulls images)
**Secrets Management**: Uses Komodo vaults for sensitive data

---

### 1.2 Dragonfly (Redis Cache)
**Type**: In-memory data store
**Location**: `/compose/dragonfly/`
**Compose File**: `compose.yaml`

**Structure**:
```yaml
Service: dragonfly
Image: docker.dragonflydb.io/dragonflydb/dragonfly
Port: 6379
Volumes: dragonflydata:/data
```

**Environment Variables**: None required
**API Endpoints**: Redis-compatible protocol on port 6379
**Dependencies**: None
**Build Requirements**: None

---

### 1.3 Qdrant (Vector Database)
**Type**: Vector search database
**Location**: `/compose/qdrant/`
**Compose File**: `compose.yaml`

**Structure**:
```yaml
Service: qdrant
Image: qdrant/qdrant:latest
Ports: 6333 (REST), 6334 (gRPC)
Volumes: ./qdrant_data
Config: Inline config.yaml (log_level: INFO)
```

**Environment Variables**: None required
**API Endpoints**:
- REST API: `http://localhost:6333`
- gRPC: `localhost:6334`

**Dependencies**: None
**Build Requirements**: None

---

### 1.4 Memgraph (Graph Database)
**Type**: Neo4j alternative for graphs
**Location**: `/compose/memgraph/`
**Compose File**: `compose.yaml`

**Key Services**:
- memgraph-mage (Graph database with algorithms)
- lab (Web UI for visualization)

**Environment Variables**:
```
MEMGRAPH_USER=op://dev-baile/memgraph_credentials/user
MEMGRAPH_PASSWORD=op://dev-baile/memgraph_credentials/password
```

**API Endpoints**:
- Bolt protocol: `localhost:7687`
- HTTPS: `localhost:7444`
- Web UI: `http://localhost:3000`

**Dependencies**: None
**Build Requirements**: None

---

## 2. DATA PROCESSING & ETL

### 2.1 Cognee (Knowledge Graph + Multi-DB)
**Type**: Data processing engine
**Location**: `/compose/cognee/`
**Compose Files**: `compose.yaml`, `.env`

**Key Services** (orchestrates external services):
- PostgreSQL with pgvector
- Memgraph (graph)
- Dragonfly (cache/redis)
- LanceDB (vector - file-based or cloud)

**Environment Variables** (Critical):
```
# LLM Configuration
LLM_API_KEY="your_api_key"
LLM_MODEL="openai/gpt-4o-mini"
LLM_PROVIDER="openai"
EMBEDDING_PROVIDER="openai"
EMBEDDING_MODEL="openai/text-embedding-3-large"

# Databases
DB_PROVIDER=postgres
DB_HOST=postgres
DB_PORT=5432
DB_USERNAME=cognee
DB_PASSWORD=cognee
GRAPH_DATABASE_URL=bolt://memgraph:7687
VECTOR_DB_PROVIDER="lancedb"

# Cache
REDIS_HOST=dragonfly
REDIS_PORT=6379

# Security
ACCEPT_LOCAL_FILE_PATH=True
ALLOW_HTTP_REQUESTS=True
ALLOW_CYPHER_QUERY=True
```

**Dependencies**: 
- PostgreSQL, Memgraph, Dragonfly (external)
- Requires LLM API key

**Build Requirements**: None (runs in Docker)

---

### 2.2 Crawl4AI (Web Scraping + LLM)
**Type**: Web crawling/scraping framework
**Location**: `/compose/crawl4ai/`
**Compose File**: `compose.yaml`

**Structure**:
```yaml
Service: crawl4ai
Image: unclecode/crawl4ai:${TAG:-latest}
Port: 11235
Memory: 4GB limit, 1GB reserved
GPU Support: Optional (ENABLE_GPU=false)
```

**Environment Variables** (from `.llm.env`):
```
OPENAI_API_KEY=
DEEPSEEK_API_KEY=
ANTHROPIC_API_KEY=
GROQ_API_KEY=
TOGETHER_API_KEY=
MISTRAL_API_KEY=
GEMINI_API_TOKEN=
LLM_PROVIDER= (optional override)
INSTALL_TYPE=default
ENABLE_GPU=false
```

**API Endpoints**: Health check at `http://localhost:11235/health`

**Dependencies**: None (standalone)
**Build Requirements**: Optional local build with Dockerfile

---

## 3. PACKAGE & ARTIFACT MANAGEMENT

### 3.1 Forgejo (Git + PyPI/Container Registry)
**Type**: Self-hosted Git with package registry
**Location**: `/compose/forgejo/`
**Compose File**: `compose.yaml`

**Key Services**:
- PostgreSQL 16 (database)
- Forgejo (Git server + registries)

**Environment Variables**:
```
# Database
FORGEJO_DB_USER=forgejo
FORGEJO_DB_PASSWORD=forgejo_password
FORGEJO_DB_NAME=forgejo

# Server
FORGEJO_DOMAIN=localhost
FORGEJO_ROOT_URL=http://localhost:3000
FORGEJO_HTTP_PORT=3000
FORGEJO_SSH_PORT=2222

# Security
FORGEJO_SECRET_KEY= (openssl rand -hex 32)

# Features
FORGEJO_DISABLE_REGISTRATION=false
FORGEJO_ACTIONS_ENABLED=false
FORGEJO__packages__ENABLED=true
FORGEJO__packages__LIMIT_TOTAL_OWNER_COUNT=-1
```

**API Endpoints**:
- Web UI: `http://localhost:3000`
- PyPI Registry: `http://localhost:3000/api/packages/{owner}/pypi`
- Container Registry: `http://localhost:3000/api/v2`
- SSH: `localhost:2222`

**SDK/Access**:
```bash
# Python package installation
pip install --index-url http://localhost:3000/api/packages/{owner}/pypi/simple data-unified

# Publication (.pypirc)
[forgejo]
repository = http://localhost:3000/api/packages/{owner}/pypi
username = {username}
password = {token}
```

**Dependencies**: None
**Build Requirements**: None

---

### 3.2 Garage (S3-Compatible Object Storage)
**Type**: Distributed S3-compatible storage
**Location**: `/compose/garage/`
**Compose File**: `docker-compose.yaml`

**Structure**:
```yaml
Service: garage
Image: dxflrs/garage:v1.0.1
Ports: 
  - 3900: S3 API
  - 3901: RPC
  - 3902: K2V API
  - 3903: Web UI
Config: ./garage.toml
Volumes: garage-meta, garage-data
```

**Environment Variables**:
```
GARAGE_RPC_PORT=3901
GARAGE_S3_API_PORT=3900
GARAGE_K2V_API_PORT=3902
GARAGE_WEB_PORT=3903
GARAGE_ADMIN_PORT=3904
RUST_LOG=garage=info
RPC_SECRET= (openssl rand -hex 32)
ADMIN_API_TOKEN= (openssl rand -base64 32)
S3_REGION=garage
REPLICATION_MODE=1 (1, 2, or 3)
```

**API Endpoints**:
- S3 API: `http://localhost:3900`
- Admin API: `http://localhost:3903`
- K2V (key-value): `http://localhost:3902`

**Dependencies**: None
**Build Requirements**: None (pulls image)
**Configuration**: Requires `./garage.toml`

---

## 4. LLM OPERATIONS & ORCHESTRATION

### 4.1 LiteLLM (LLM Proxy & Management)
**Type**: LLM provider abstraction
**Location**: `/compose/litellm/`
**Compose File**: `compose.yaml`

**Key Services**:
- LiteLLM proxy server
- PostgreSQL 15 (for model/key management)

**Environment Variables**:
```
# Security
LITELLM_MASTER_KEY=op://komodo/litellm/.../LITELLM_MASTER_KEY
LITELLM_SALT_KEY=op://komodo/litellm/.../LITELLM_SALT_KEY

# UI
UI_USERNAME=op://komodo/litellm/.../UI_USERNAME
UI_PASSWORD=op://komodo/litellm/.../UI_PASSWORD

# Database
DATABASE_URL=postgresql://litellm:litellm_password@postgres:5432/litellm
POSTGRES_USER=litellm
POSTGRES_PASSWORD=litellm_password
POSTGRES_DB=litellm

# LLM API Keys (all optional, as needed)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=op://komodo/litellm/.../ANTHROPIC_API_KEY
HF_TOKEN=op://komodo/litellm/.../HF_TOKEN
OPENROUTER_API_KEY=op://komodo/litellm/.../OPENROUTER_API_KEY
AZURE_API_KEY=
GEMINI_API_KEY=op://komodo/litellm/.../GEMINI_API_KEY
GROQ_API_KEY=
TOGETHER_AI_API_KEY=
MISTRAL_API_KEY=
DEEPSEEK_API_KEY=op://komodo/litellm/.../DEEPSEEK_API_KEY

# Observability Integration
LANGFUSE_PUBLIC_KEY=op://komodo/litellm/.../LANGFUSE_PUBLIC_KEY
LANGFUSE_SECRET_KEY=op://komodo/litellm/.../LANGFUSE_SECRET_KEY
```

**API Endpoints**:
- Proxy server: `http://localhost:4000`
- Admin UI: `http://localhost:4000/ui/`

**Configuration**: Requires `./litellm_config.yaml`
**Dependencies**: PostgreSQL
**Build Requirements**: None

---

### 4.2 MLFlow (Model Tracking & Registry)
**Type**: ML experiment tracking
**Location**: `/compose/mlflow/`
**Compose File**: `compose.yaml`

**Key Services**:
- PostgreSQL 15 (backend store)
- MinIO (artifact storage)
- MLFlow server

**Environment Variables**:
```
# Database
POSTGRES_USER= (required)
POSTGRES_PASSWORD= (required)
POSTGRES_DB= (required)

# MinIO S3
MINIO_ROOT_USER= (required)
MINIO_ROOT_PASSWORD= (required)
MINIO_HOST=minio
MINIO_PORT=9000
MINIO_BUCKET=mlflow

# MLFlow
MLFLOW_BACKEND_STORE_URI=postgresql://user:pass@postgres:5432/db
MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://mlflow
MLFLOW_S3_ENDPOINT_URL=http://minio:9000
MLFLOW_HOST=0.0.0.0
MLFLOW_PORT=5000
AWS_DEFAULT_REGION=us-east-1
```

**API Endpoints**:
- UI: `http://localhost:5000`
- Tracking API: `http://localhost:5000`

**Dependencies**: PostgreSQL, MinIO
**Build Requirements**: None

---

### 4.3 Langfuse (LLM Observability)
**Type**: LLM trace logging & analytics
**Location**: `/compose/langfuse/`
**Compose File**: `compose.yaml`

**Key Services**:
- Langfuse server
- PostgreSQL 15

**Environment Variables**:
```
# Application
LANGFUSE_VERSION=2
LANGFUSE_PORT=3000

# PostgreSQL
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=postgres
POSTGRES_PORT=5432

# Security (REQUIRED - generate with: openssl rand -base64 32)
NEXTAUTH_SECRET=
SALT=
ENCRYPTION_KEY=

# Optional
LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES=false
TELEMETRY_ENABLED=true
LANGFUSE_DEFAULT_PROJECT_ID=
LANGFUSE_DEFAULT_PROJECT_ROLE=
```

**API Endpoints**:
- Dashboard: `http://localhost:3000`
- API: `http://localhost:3000/api`
- SDKs: Python, JS/TS available

**Dependencies**: PostgreSQL
**Build Requirements**: None

---

## 5. WORKFLOW & ORCHESTRATION

### 5.1 Dagster (Data Orchestration)
**Type**: Data pipeline orchestration
**Location**: `/compose/dagster/`
**Compose File**: `docker-compose.yaml`

**Key Services**:
- PostgreSQL 15 (state storage)
- Dagster User Code (gRPC server)
- Dagster Webserver (UI + GraphQL API)
- Dagster Daemon (scheduler/launcher)

**Environment Variables** (from `.env.example`):
```
# PostgreSQL
DAGSTER_POSTGRES_USER=dagster
DAGSTER_POSTGRES_PASSWORD=dagster_password
DAGSTER_POSTGRES_DB=dagster

# Forgejo PyPI Registry (for data-unified package)
FORGEJO_URL=http://forgejo:3000
FORGEJO_OWNER=data
FORGEJO_USER=
FORGEJO_TOKEN=
DATA_UNIFIED_VERSION=0.1.0

# GitHub API
GITHUB_TOKEN=ghp_your_token_here
GITHUB_INCREMENTAL_DAYS=30

# Ports
DAGSTER_WEBSERVER_PORT=3001
```

**API Endpoints**:
- Dashboard: `http://localhost:3001`
- GraphQL API: `http://localhost:3001/graphql`
- Docs: `http://localhost:3001/docs`

**Build Requirements**: 
- `Dockerfile` - Dagster image
- `Dockerfile.user_code` - User code gRPC server
- `Dockerfile.dagster` - Webserver/Daemon

**Dependencies**: 
- PostgreSQL
- Forgejo (for data-unified package)
- Docker socket (for DockerRunLauncher)

**Network Integration**: Connects to `forgejo_network` for package access

---

### 5.2 Pangolin (Network Config Management)
**Type**: Infrastructure as Code
**Location**: `/compose/pangolin/core/`
**Compose File**: `compose.yaml`

**Key Services**:
- Pangolin (main service)
- Gerbil (Wireguard VPN)
- Traefik (reverse proxy)

**Environment Variables**: None required
**API Endpoints**: `http://localhost:3001/api/v1/`
**Dependencies**: None
**Build Requirements**: None
**Network**: Custom network `pangolin` with bridge driver

---

### 5.3 Komodo (Infrastructure Orchestration)
**Type**: Server/container orchestration
**Location**: `/compose/komodo/periphery/`
**Compose File**: `compose.yaml`

**Key Services**:
- Komodo Periphery (agent)

**Environment Variables**:
```
PERIPHERY_ROOT_DIRECTORY=/etc/komodo
PERIPHERY_PASSKEYS=abc123
PERIPHERY_SSL_ENABLED=true
PERIPHERY_DISABLE_TERMINALS=false
PERIPHERY_INCLUDE_DISK_MOUNTS=/etc/hostname
```

**Volumes**:
- Docker socket access
- /proc for process monitoring
- /etc/komodo (agent root)

**Dependencies**: None (standalone agent)
**Build Requirements**: None

---

## 6. DEVELOPMENT & AGENTIC FRAMEWORKS

### 6.1 Agno (Agentic Framework)
**Type**: Agent development framework
**Location**: `/compose/agno/`
**Compose File**: `compose.yaml`

**Key Services**:
- pgvector (Postgres + vector search)
- API server (FastAPI)

**Environment Variables**:
```
# Database
DB_USER=ai
DB_PASSWORD=ai
DB_NAME=ai

# LLM
OPENAI_API_KEY= (required)

# Internal
DB_HOST=pgvector
DB_PORT=5432
WAIT_FOR_DB=True
PRINT_ENV_ON_LOAD=True
```

**API Endpoints**: `http://localhost:8000`

**Build Requirements**: 
- Local Dockerfile in root
- Image: `${IMAGE_NAME:-agent-os}:${IMAGE_TAG:-latest}`
- Volume mounts current directory for development

**Dependencies**: PostgreSQL
**Network**: Custom `agent-os` network

---

### 6.2 Termix (Terminal Multiplexer)
**Type**: Web-based terminal
**Location**: `/compose/termix/`
**Compose File**: `compose.yaml`

**Structure**:
```yaml
Service: termix
Image: ghcr.io/lukegus/termix:latest
Port: 8080
Volumes: termix-data:/app/data
```

**Environment Variables**: None required
**API Endpoints**: `http://localhost:8080`
**Dependencies**: None

---

## 7. SECRETS & CONFIGURATION MANAGEMENT

### 7.1 Infisical (Secrets Management)
**Type**: Secrets management platform
**Location**: `/compose/infisical/`
**Compose File**: Not found (uses `.env.template`)

**Environment Variables** (from template):
```
# Encryption
ENCRYPTION_KEY=6c1fe4e407b8911c104518103505b218
AUTH_SECRET=5lrMXKKWCVocS/uerPsl7V+TX/aaUaI7iDkgl3tSmLE=

# Database
POSTGRES_USER=infisical
POSTGRES_PASSWORD=infisical
POSTGRES_DB=infisical
DB_CONNECTION_URI=postgres://infisical:infisical@db:5432/infisical

# Redis
REDIS_URL=redis://redis:6379

# Server
SITE_URL=http://localhost:8080

# Optional integrations (GitHub, Gitlab, etc)
CLIENT_ID_GITHUB=
CLIENT_SECRET_GITHUB=
...
```

**Status**: No compose file (incomplete)

---

## SERVICE DEPENDENCY MATRIX

```
┌─────────────────────────────────────────────────────────────────┐
│ SERVICE DEPENDENCIES & DATA FLOW                                │
└─────────────────────────────────────────────────────────────────┘

CORE INFRASTRUCTURE:
├── Supabase (PostgreSQL + APIs)
│   └── depends on: PostgreSQL, Redis (optional)
├── Forgejo (Git + PyPI Registry)
│   └── depends on: PostgreSQL
├── Garage (S3 Storage)
│   └── depends on: none
├── Dragonfly (Cache)
│   └── depends on: none
├── Qdrant (Vector DB)
│   └── depends on: none
├── Memgraph (Graph DB)
│   └── depends on: none

DATA PROCESSING:
├── Cognee (Knowledge Graph)
│   └── depends on: PostgreSQL, Memgraph, Dragonfly, LanceDB, LLM API
├── Crawl4AI (Web Scraping)
│   └── depends on: LLM API keys

ORCHESTRATION:
├── Dagster (Pipeline Orchestration)
│   ├── depends on: PostgreSQL, Forgejo, GitHub API, Docker
│   └── provides data to: Supabase, S3, BigQuery, Snowflake
├── Pangolin (Network Management)
│   └── depends on: none
└── Komodo Periphery (Infrastructure Agent)
    └── depends on: Docker, /proc, /etc/komodo

LLM OPERATIONS:
├── LiteLLM (LLM Proxy)
│   ├── depends on: PostgreSQL, LLM API keys
│   └── integrates with: Langfuse
├── MLFlow (Model Tracking)
│   ├── depends on: PostgreSQL, MinIO
│   └── provides: Model registry, Experiment tracking
└── Langfuse (LLM Observability)
    └── depends on: PostgreSQL

DEVELOPMENT:
├── Agno (Agent Framework)
│   ├── depends on: PostgreSQL (pgvector)
│   └── needs: OPENAI_API_KEY
└── Termix (Terminal)
    └── depends on: none
```

---

## ENVIRONMENT VARIABLE MANAGEMENT MATRIX

| Service | Type | Required | Optional | Template File | Uses Vault |
|---------|------|----------|----------|---------------|-----------|
| **Supabase** | Secrets | POSTGRES_PASSWORD | OPENAI_API_KEY | N/A | Yes (Komodo) |
| **Forgejo** | Config | FORGEJO_DB_PASSWORD, SECRET_KEY | DOMAIN, HTTP_PORT | `.env.example` | No |
| **Garage** | Config | RPC_SECRET, ADMIN_API_TOKEN | BOOTSTRAP_PEERS | `.env` | No |
| **Dragonfly** | Config | None | RUST_LOG | N/A | No |
| **Qdrant** | Config | None | None | N/A | No |
| **Memgraph** | Secrets | PASSWORD | None | `.env.template` | Yes (OnePassword) |
| **Cognee** | Config | LLM_API_KEY | 15+ database/LLM configs | `.env` | No |
| **Crawl4AI** | Secrets | LLM_API_KEY (at least 1) | Multiple LLM providers | `.llm.env` | No |
| **Dagster** | Config | GITHUB_TOKEN, FORGEJO_TOKEN | DAGSTER_WEBSERVER_PORT | `.env.example` | No |
| **Pangolin** | Config | None | None | N/A | No |
| **Komodo** | Config | None | PERIPHERY_PASSKEYS | N/A | No |
| **Agno** | Config | OPENAI_API_KEY | DB_*, custom ports | N/A | No |
| **Termix** | Config | None | PORT | N/A | No |
| **LiteLLM** | Secrets | LITELLM_MASTER_KEY | Multiple LLM keys | `.env.template` | Yes (Komodo vault) |
| **MLFlow** | Config | POSTGRES_*, MINIO_* | AWS_DEFAULT_REGION | N/A | No |
| **Langfuse** | Secrets | NEXTAUTH_SECRET, SALT, ENCRYPTION_KEY | TELEMETRY_ENABLED | N/A | No |
| **Infisical** | Secrets | ENCRYPTION_KEY, AUTH_SECRET | OAuth tokens | `.env.template` | No |

---

## NETWORK ARCHITECTURE

### Custom Networks
```
forgejo_network       - Shared by: Forgejo, Dagster
dagster_network       - Dagster internal
agent-os             - Agno framework
pangolin             - Pangolin services
mlflow-network       - MLFlow ecosystem
default (Docker)     - Most other services
```

### Port Allocation Reference
```
Port Range 3000-3999  (Web UIs):
  3000: Forgejo, Supabase Studio, Memgraph Lab, Agno, Termix
  3001: Dagster Webserver, Pangolin API
  3903: Garage Web UI

Port Range 4000-4999 (APIs):
  4000: LiteLLM
  4001: Langfuse

Port Range 5000-5999 (Databases/Data):
  5432: PostgreSQL instances (Supabase, Forgejo, Langfuse, MLFlow, etc.)
  5000: MLFlow UI

Port Range 6000-6999 (Search/Graph):
  6333: Qdrant REST
  6334: Qdrant gRPC
  6379: Dragonfly/Redis
  6543: Supabase Supavisor (pooling)

Port Range 7000-7999 (Graph/Additional):
  7687: Memgraph Bolt
  7444: Memgraph HTTPS

Port Range 8000-8999 (APIs/Secondary):
  8000: Supabase Kong (API Gateway)
  8000: Crawl4AI health
  8080: Infisical, Termix
  8443: Supabase Kong HTTPS

Port Range 9000-9999 (Object Storage):
  9000: MinIO S3 API
  9001: MinIO Console

Port Range 11000+:
  11235: Crawl4AI
```

---

## BUILD & DEPLOYMENT REQUIREMENTS

### Services Requiring Build
1. **Dagster** (3 Dockerfiles):
   - `Dockerfile` - Main webserver/daemon
   - `Dockerfile.user_code` - gRPC server for pipeline code
   - `Dockerfile.dagster` - Reusable Dagster image

2. **Agno**:
   - `Dockerfile` - FastAPI server with pgvector

3. **Crawl4AI** (Optional):
   - `Dockerfile` - Local build with INSTALL_TYPE/GPU options

### Services Using Pre-built Images
All others pull from registries:
- `docker.io`: Most official images
- `ghcr.io`: GitHub Container Registry (LiteLLM, MLFlow, Komodo, Termix)
- `codeberg.org`: Forgejo
- `docker.dragonflydb.io`: Dragonfly

---

## OBSERVABILITY & INTEGRATION CHAIN

### Data Collection Pipeline
```
Crawl4AI → Cognee → PostgreSQL
   ↓
Dagster (orchestrates) → GitHub data → Cognee/PostgreSQL
   ↓
MLFlow (tracks models) → PostgreSQL + MinIO
   ↓
Langfuse (traces LLM calls) → PostgreSQL
   ↓
LiteLLM (proxies requests) → Integrated with Langfuse
   ↓
Supabase (stores results) → PostgreSQL + APIs
   ↓
Qdrant (vector search) ← Cognee embeddings
```

### Authentication & Secrets Chain
```
Komodo vault (.env.template files)
    ↓
LiteLLM, Memgraph, Supabase secrets
    ↓
Docker Compose env substitution
    ↓
Running services
```

---

## SERVICE MANAGEMENT MATRIX

| Service | Env Vars | Image Build | Secrets | Config Files | Health Check |
|---------|----------|------------|---------|--------------|--------------|
| Supabase | 20+ | No | Vault refs | docker-compose.yml | Script-based |
| Forgejo | 15+ | No | PASSWORD, SECRET_KEY | compose.yaml | pg_isready |
| Garage | 8+ | No | RPC_SECRET | garage.toml + .env | None |
| Dragonfly | 2 | No | None | compose.yaml | None |
| Qdrant | 0 | No | None | Inline config | None |
| Memgraph | 2 | No | Vault refs | compose.yaml | None |
| Cognee | 40+ | No | LLM_API_KEY | .env | None |
| Crawl4AI | 10+ | Optional | LLM keys | .llm.env | HTTP (11235) |
| Dagster | 12+ | 3x Yes | GITHUB_TOKEN | workspace.yaml | pg_isready, HTTP |
| Pangolin | 0 | No | None | config/*.yml | HTTP (3001) |
| Komodo | 4+ | No | PASSKEYS | periphery.config.toml | None |
| Agno | 8+ | Yes | OPENAI_API_KEY | None | HTTP (8000) |
| Termix | 1 | No | None | compose.yaml | None |
| LiteLLM | 20+ | No | Vault refs | litellm_config.yaml | None |
| MLFlow | 12+ | No | None | compose.yaml | HTTP (5000) |
| Langfuse | 8+ | No | Random keys | compose.yaml | HTTP (3000) |
| Infisical | 30+ | No | Vault refs | .env.template | None |

---

## DEPLOYMENT CHECKLIST

### Pre-deployment
- [ ] Generate security keys (openssl rand -hex 32)
- [ ] Copy all .env.example/.env.template files to .env
- [ ] Fill in LLM API keys (OpenAI, Anthropic, etc.)
- [ ] Fill in GitHub token for Dagster
- [ ] Setup Komodo vault references for sensitive data
- [ ] Configure Forgejo registry credentials if using data-unified
- [ ] Verify port availability (3000-11235 range)

### Post-deployment
- [ ] Test Supabase: `curl http://localhost:8000/rest/v1`
- [ ] Test Forgejo: Visit `http://localhost:3000`
- [ ] Test Dagster: Visit `http://localhost:3001`
- [ ] Test LiteLLM: Visit `http://localhost:4000/ui/`
- [ ] Test Langfuse: Visit `http://localhost:3000`
- [ ] Verify PostgreSQL databases: `psql postgresql://user:pass@localhost:5432/db`
- [ ] Test Crawl4AI: `curl http://localhost:11235/health`

---

## CRITICAL INTEGRATION POINTS

1. **Forgejo ↔ Dagster**: data-unified package installation via PyPI
2. **Dagster ↔ Supabase**: Data warehouse for pipeline results
3. **Cognee ↔ Memgraph**: Graph data storage
4. **Cognee ↔ Dragonfly**: Cache for embeddings
5. **LiteLLM ↔ Langfuse**: LLM call tracing
6. **Crawl4AI ↔ Cognee**: Web content processing
7. **All LLM services**: Require external API keys (OpenAI, Anthropic, etc.)
8. **Dagster ↔ GitHub**: Repository data ingestion

---

## KNOWN LIMITATIONS & NOTES

1. **Infisical**: Only .env.template provided, no compose.yaml
2. **Pangolin/Komodo**: Minimal/example configurations
3. **Garage**: Single-node setup (REPLICATION_MODE=1)
4. **Port Conflicts**: Ensure ports 3000-11235 available
5. **Docker Socket**: Dagster & Komodo need `/var/run/docker.sock` access
6. **Secrets Management**: Heavy reliance on Komodo vault for production
7. **Network Isolation**: Most services on isolated networks but interconnected
8. **Database Sizing**: Default PostgreSQL with minimal resources

---

# Service Management Matrix

## SERVICE MATRIX

| # | Service | Type | ENV | BUILD | Secrets | Config | Dependencies | Status | Priority |
|---|---------|------|-----|-------|---------|--------|--------------|--------|----------|
| 1 | **Supabase** | Core DB | 20+ | No | Vault refs | compose.yml | None | Ready | Critical |
| 2 | **Forgejo** | Registry | 15+ | No | 2 | compose.yaml | None | Ready | Critical |
| 3 | **Dagster** | Orchestration | 12+ | 3x Yes | 2 | 3 files | PG, Forgejo, GH | Ready | Critical |
| 4 | **LiteLLM** | LLM Proxy | 20+ | No | Vault refs | litellm_config.yaml | PostgreSQL | Ready | High |
| 5 | **Cognee** | Data Engine | 40+ | No | LLM key | .env | PG, Memgraph, Cache | Ready | High |
| 6 | **Langfuse** | Observability | 8+ | No | 3 keys | compose.yaml | PostgreSQL | Ready | High |
| 7 | **Crawl4AI** | Web Scraper | 10+ | Opt | LLM keys | .llm.env | None | Ready | Medium |
| 8 | **MLFlow** | Model Tracking | 12+ | No | None | compose.yaml | PG, MinIO | Ready | Medium |
| 9 | **Agno** | Agent Framework | 8+ | Yes | 1 key | None | PostgreSQL | Ready | Medium |
| 10 | **Garage** | S3 Storage | 8+ | No | 2 | garage.toml | None | Ready | Medium |
| 11 | **Memgraph** | Graph DB | 2 | No | Vault refs | compose.yaml | None | Ready | Medium |
| 12 | **Qdrant** | Vector DB | 0 | No | None | Inline | None | Ready | Low |
| 13 | **Dragonfly** | Cache | 2 | No | None | compose.yaml | None | Ready | Low |
| 14 | **Pangolin** | Network Mgmt | 0 | No | None | config/*.yml | None | Example | Low |
| 15 | **Komodo** | Infra Agent | 4+ | No | 1 | config.toml | Docker socket | Example | Low |
| 16 | **Termix** | Terminal | 1 | No | None | compose.yaml | None | Ready | Utility |
| 17 | **Infisical** | Secrets Mgmt | 30+ | No | Vault refs | .env.template | None | Incomplete | Low |

---

## ENVIRONMENT SETUP BY CATEGORY

### Critical Path (Required for MVP)
```
1. Supabase          → Primary database & auth
2. Forgejo           → Package registry for data-unified
3. Dagster           → Pipeline orchestration
4. LiteLLM           → LLM abstraction layer
5. Langfuse          → Observability
```

### Data Processing (Recommended)
```
6. Cognee            → Knowledge graph processing
7. Crawl4AI          → Web content extraction
8. Memgraph          → Graph database
9. Dragonfly         → Cache layer
10. Qdrant           → Vector search
```

### Advanced (Optional)
```
11. MLFlow           → Model experiment tracking
12. Agno             → Agent development
13. Garage           → S3-compatible storage
14. Pangolin         → Infrastructure networking
15. Komodo           → Server orchestration
```

---

## SECRETS & KEYS REQUIRED

### API Keys (External Services)
- **OpenAI** OPENAI_API_KEY (for LLMs, Supabase SQL editor)
- **Anthropic** ANTHROPIC_API_KEY (optional, for multi-LLM)
- **Other LLMs**: Groq, DeepSeek, Mistral, etc. (optional)
- **GitHub** GITHUB_TOKEN (Dagster, for repo data)

### Generated Keys (one-time, store securely)
- **Forgejo** FORGEJO_SECRET_KEY (openssl rand -hex 32)
- **Garage** RPC_SECRET, ADMIN_API_TOKEN
- **Langfuse** NEXTAUTH_SECRET, SALT, ENCRYPTION_KEY
- **Infisical** ENCRYPTION_KEY, AUTH_SECRET
- **LiteLLM** LITELLM_MASTER_KEY, LITELLM_SALT_KEY
- **Supabase** JWT_SECRET, ANON_KEY, SERVICE_ROLE_KEY

### Vault-Managed (Komodo)
- Supabase credentials
- LiteLLM keys
- Memgraph credentials
- Various API keys

---

## PORT ASSIGNMENTS

### Web UIs (3000-3999)
```
3000: Forgejo, Supabase Studio, Memgraph Lab, Agno
3001: Dagster, Pangolin API
3903: Garage Web UI
```

### APIs (4000-4999)
```
4000: LiteLLM
```

### Databases (5432+)
```
5432: Multiple PostgreSQL instances
5000: MLFlow UI
```

### Search & Cache (6333-6379)
```
6333: Qdrant REST
6334: Qdrant gRPC
6379: Dragonfly/Redis
```

### Graph (7687+)
```
7687: Memgraph Bolt
```

### Storage & APIs (8000-8999)
```
8000: Supabase Kong API Gateway
8080: Infisical, Termix
```

### Object Storage (9000-9999)
```
9000: MinIO S3 API
9001: MinIO Console
```

### Special (11235+)
```
11235: Crawl4AI
```

---

## ENVIRONMENT FILE CHECKLIST

### Step 1: Copy Templates
```bash
cd /infrastructure/compose

# Copy all templates
cp cognee/.env.template cognee/.env
cp litellm/.env.template litellm/.env
cp memgraph/.env.template memgraph/.env
cp infisical/.env.template infisical/.env
cp forgejo/.env.example forgejo/.env
cp dagster/.env.example dagster/.env

# Crawl4AI special case
cp crawl4ai/.llm.env.example crawl4ai/.llm.env
```

### Step 2: Generate Secrets
```bash
# Generate Forgejo secret
openssl rand -hex 32  # → FORGEJO_SECRET_KEY

# Generate Garage secrets
openssl rand -hex 32  # → RPC_SECRET
openssl rand -base64 32  # → ADMIN_API_TOKEN

# Generate Langfuse secrets
openssl rand -base64 32  # → NEXTAUTH_SECRET
openssl rand -base64 32  # → SALT
openssl rand -base64 32  # → ENCRYPTION_KEY

# Generate LiteLLM secrets
openssl rand -hex 32  # → LITELLM_MASTER_KEY
openssl rand -hex 32  # → LITELLM_SALT_KEY
```

### Step 3: Fill in API Keys
```bash
# Get these from services:
# - OpenAI: https://platform.openai.com/account/api-keys
# - Anthropic: https://console.anthropic.com/
# - GitHub: https://github.com/settings/tokens
# - Groq, DeepSeek, Mistral, etc.

# Edit each .env file and add your keys
nano cognee/.env
nano litellm/.env
nano crawl4ai/.llm.env
nano dagster/.env
# ... etc
```

### Step 4: Verify Configurations
```bash
# Check all .env files exist
ls -la */\.env

# Verify required vars are set (non-empty)
grep -h "^[A-Z_]*=$" */\.env  # Shows empty vars
```

---

## DEPLOYMENT ORDER

### Phase 1: Infrastructure (No dependencies)
1. Dragonfly (cache)
2. Qdrant (vector DB)
3. Memgraph (graph DB)

### Phase 2: Core Services (Dependencies on Phase 1)
4. Forgejo (needs working before Dagster)
5. Supabase (main DB + APIs)
6. PostgreSQL instances (for other services)

### Phase 3: Orchestration & LLM
7. Dagster (needs Forgejo ready)
8. LiteLLM (LLM proxy)
9. Langfuse (observability)

### Phase 4: Data Processing
10. Cognee (needs Memgraph, Dragonfly, LLMs)
11. Crawl4AI (web scraping)
12. MLFlow (optional, for experiment tracking)

### Phase 5: Development & Utilities
13. Agno (agent framework)
14. Garage (S3 storage)
15. Pangolin (network management)
16. Komodo (infrastructure)
17. Termix (utilities)

---

## HEALTH CHECK COMMANDS

```bash
# Supabase API Gateway
curl http://localhost:8000/rest/v1

# Forgejo
curl http://localhost:3000

# Dagster
curl http://localhost:3001

# LiteLLM
curl http://localhost:4000/health

# Langfuse
curl http://localhost:3000/api/health

# Crawl4AI
curl http://localhost:11235/health

# Qdrant
curl http://localhost:6333/health

# Dragonfly
redis-cli -p 6379 ping

# MLFlow
curl http://localhost:5000

# Memgraph
curl http://localhost:7444

# Garage S3
curl http://localhost:3900

# PostgreSQL instances
psql postgresql://user:pass@localhost:5432/dbname -c "SELECT 1"
```

---

## COMMON ISSUES & SOLUTIONS

### Port Already in Use
```bash
# Find process using port
lsof -i :3000

# Kill process
kill -9 <PID>

# Or change port in .env
FORGEJO_HTTP_PORT=3001
```

### PostgreSQL Connection Failed
```bash
# Check if PostgreSQL is running
docker-compose logs postgres

# Verify credentials in .env
grep POSTGRES_ */\.env

# Check volume mounts
docker volume ls | grep postgres
```

### LLM API Key Invalid
```bash
# Test key directly
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models

# Check .env file
cat cognee/.env | grep LLM_API_KEY
```

### Vault References Not Resolving
```bash
# Ensure Komodo vault is running
docker ps | grep komodo

# Check vault CLI
op vault list

# Manually resolve and update .env
op read op://vault/service/key
```

---

## ENVIRONMENT VARIABLE TEMPLATES

### Minimal Setup (.env)
```bash
# Supabase
POSTGRES_PASSWORD=your_secure_password

# Forgejo
FORGEJO_DB_PASSWORD=your_secure_password
FORGEJO_SECRET_KEY=your_hex_key

# Dagster
GITHUB_TOKEN=ghp_your_token
DAGSTER_POSTGRES_PASSWORD=your_secure_password

# LLMs
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=sk-ant-your-key

# Langfuse
NEXTAUTH_SECRET=your_random_base64
SALT=your_random_base64
ENCRYPTION_KEY=your_random_base64
```

### Full Setup (.env.example pattern)
See individual `.env.example` and `.env.template` files for complete listings.

---

## INTEGRATION SUMMARY

### Data Flow
```
Web (Crawl4AI)
    ↓
Cognee (Processing)
    ↓
PostgreSQL (Supabase)
    ↓
Dagster (Orchestration) → GitHub Data
    ↓
Qdrant (Vector Search)
MLFlow (Model Tracking)
LiteLLM (LLM Proxy) → Langfuse (Tracing)
    ↓
APIs (Kong/PostgREST)
    ↓
Clients
```

### Storage Architecture
```
Forgejo:    Source code + Python packages
Supabase:   Primary database + auth
Garage:     S3-compatible object storage
Dragonfly:  Cache layer
Memgraph:   Knowledge graphs
Qdrant:     Vector embeddings
MLFlow:     Model artifacts (MinIO)
```

---

## SCALING CONSIDERATIONS

### Single-Node Limitations
- Garage set to REPLICATION_MODE=1 (no redundancy)
- Single PostgreSQL instance (no replication)
- Dragonfly single instance (no clustering)
- Memgraph single instance

### For Production
- Enable Garage replication (mode 2-3)
- Setup PostgreSQL streaming replication
- Use Dragonfly cluster mode
- Add Memgraph replication
- Load balance with Traefik/Kong
- Use managed databases if available


---

## From: DOCKER_COMPOSE_ARCHITECTURE.md (leftover)

# Docker Compose Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     HACKATHON DOCKER COMPOSE ECOSYSTEM                       │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────────┐
│ FRONTEND & EXTERNAL ACCESS LAYER                                             │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  Web Browsers / API Clients / CLI Tools                                       │
│         │                │                │                                  │
│         ├────────────────┼────────────────┤                                  │
│         │                │                │                                  │
│    3000,3001          8000,4000        11235,6333                           │
│         │                │                │                                  │
└─────────┼────────────────┼────────────────┼───────────────────────────────┘
          │                │                │
          v                v                v
┌────────────────┬──────────────────┬──────────────────┐
│                │                  │                  │
│   WEB UIs      │     API GATEWAYS │   DATA ACCESS    │
│   (Port 3000)  │     (Port 8000)  │   (Port 11235)   │
│                │                  │                  │
├────────────────┼──────────────────┼──────────────────┤
│ ○ Forgejo      │ ○ Kong/Supabase  │ ○ Crawl4AI       │
│ ○ Agno         │ ○ PostgREST      │   (Web Scraper)  │
│ ○ Memgraph Lab │ ○ GoTrue (Auth)  │                  │
│ ○ Dagster      │ ○ Realtime       │                  │
│ ○ MLFlow       │                  │                  │
│ ○ Termix       │                  │                  │
└────────────────┴──────────────────┴──────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│ APPLICATION LAYER                                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                  │
│  │  Orchestration   │    │  LLM Services   │    │  Data Processing          │
│  │                  │    │                  │    │                          │
│  ├──────────────┤    ├──────────────┤    ├──────────────┤                  │
│  │ ○ Dagster   │    │ ○ LiteLLM    │    │ ○ Cognee     │                  │
│  │   (ETL)     │    │   (Proxy)    │    │   (Graph)    │                  │
│  │ ○ Pangolin  │    │ ○ Langfuse   │    │ ○ Crawl4AI   │                  │
│  │   (Network) │    │   (Tracing)  │    │   (Scraper)  │                  │
│  │ ○ Komodo    │    │ ○ MLFlow     │    │ ○ Agno       │                  │
│  │   (Infra)   │    │   (Tracking) │    │   (Agents)   │                  │
│  │ ○ Termix    │    │              │    │              │                  │
│  │   (Shell)   │    │              │    │              │                  │
│  └──────────────┘    └──────────────┘    └──────────────┘                  │
│         │                   │                    │                          │
│         └───────────────────┼────────────────────┘                          │
│                             │                                               │
└─────────────────────────────┼───────────────────────────────────────────────┘
                              │
                              v
┌──────────────────────────────────────────────────────────────────────────────┐
│ DATA LAYER                                                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐    │
│  │  PRIMARY DATA   │  │ SPECIALIZED DBS │  │    CACHE & SEARCH       │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐    │
│  │ ○ Supabase      │  │ ○ Memgraph      │  │ ○ Qdrant                │    │
│  │   PostgreSQL    │  │   (Graph DB)    │  │   (Vector Search)       │    │
│  │   + Auth        │  │ ○ LanceDB       │  │ ○ Dragonfly             │    │
│  │   + APIs        │  │   (Vector)      │  │   (Redis Cache)         │    │
│  │                 │  │                 │  │                         │    │
│  │ ○ Multiple      │  │ ○ Kuzu          │  │ ○ MinIO                 │    │
│  │   PostgreSQL    │  │   (Graph)       │  │   (S3-compatible)       │    │
│  │   instances     │  │                 │  │                         │    │
│  │   (Forgejo,     │  │ ○ Neo4j         │  │ ○ Garage                │    │
│  │    Dagster,     │  │   (Graph)       │  │   (S3-compatible)       │    │
│  │    LiteLLM,     │  │                 │  │                         │    │
│  │    Langfuse,    │  │                 │  │                         │    │
│  │    MLFlow)      │  │                 │  │                         │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘    │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│ INFRASTRUCTURE LAYER                                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ○ Docker Networks       ○ Docker Volumes    ○ External APIs               │
│    - forgejo_network       - postgres data      - OpenAI                    │
│    - dagster_network       - cache data         - Anthropic                 │
│    - agent-os              - search indices     - GitHub                    │
│    - pangolin              - artifacts          - Other LLM providers       │
│    - mlflow-network                                                         │
│                                                                               │
│  ○ Registry (Forgejo)   ○ Secrets (Vault)                                   │
│    - PyPI packages        - Komodo vault                                    │
│    - Docker images        - API keys                                        │
│    - Data-unified pkg     - DB passwords                                    │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DATA PROCESSING PIPELINE                             │
└─────────────────────────────────────────────────────────────────────────────┘

INGESTION → PROCESSING → STORAGE → QUERYING → ANALYTICS
   │          │            │         │          │
   v          v            v         v          v

Crawl4AI    Cognee      Supabase   Qdrant    Langfuse
   │          │            │         │          │
   └──────────┴────────────┴─────────┴──────────┘
              │
              v
          Dagster
         (Orchestrator)
              │
       ┌──────┼──────┐
       │      │      │
       v      v      v
     GitHub  APIs  Reports
     Data  Output  Output
```

---

## Service Dependency Graph

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     SERVICE DEPENDENCIES CHART                               │
└─────────────────────────────────────────────────────────────────────────────┘

TIER 0 - STANDALONE (No Dependencies)
├── Dragonfly (Redis-compatible cache)
├── Qdrant (Vector database)
├── Termix (Web terminal)
├── Pangolin (Network configuration)
└── Komodo (Infrastructure agent)

TIER 1 - DATABASE-DEPENDENT
├── Forgejo → PostgreSQL
├── Supabase → PostgreSQL + external services
├── Memgraph (optional PostgreSQL extension)
├── LiteLLM → PostgreSQL
├── Langfuse → PostgreSQL
└── MLFlow → PostgreSQL + MinIO

TIER 2 - MULTI-SERVICE DEPENDENT
├── Cognee → PostgreSQL + Memgraph + Dragonfly + LanceDB + LLM API
├── Dagster → PostgreSQL + Forgejo + GitHub + Docker socket
├── Crawl4AI → LLM API keys
└── Agno → PostgreSQL (pgvector)

TIER 3 - DEPENDENT ON TIER 2
└── (None - everything converges at Supabase/Dagster)
```

---

## Network Topology

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DOCKER NETWORK TOPOLOGY                               │
└─────────────────────────────────────────────────────────────────────────────┘

ISOLATED NETWORKS:
  
  forgejo_network
  ├── forgejo
  └── forgejo_db

  dagster_network
  ├── dagster_postgresql
  ├── dagster_user_code
  ├── dagster_webserver
  └── dagster_daemon
  
  agent-os
  ├── pgvector (Agno)
  └── api (Agno FastAPI)
  
  pangolin
  ├── pangolin
  ├── gerbil
  └── traefik
  
  mlflow-network
  ├── postgres (MLFlow)
  ├── minio
  └── mlflow

BRIDGE NETWORKS (Services on default Docker bridge):
  ├── Supabase (multiple services)
  ├── LiteLLM + PostgreSQL
  ├── Langfuse + PostgreSQL
  ├── Memgraph + Lab
  ├── Dragonfly
  ├── Qdrant
  ├── Crawl4AI
  ├── Garage
  ├── Infisical
  └── Termix

SHARED CONNECTIONS:
  - Forgejo → Dagster (via external forgejo_network)
  - All services → External APIs (OpenAI, Anthropic, GitHub, etc.)
```

---

## Port Map by Service

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PORT ALLOCATION MAP                                  │
└─────────────────────────────────────────────────────────────────────────────┘

WEB INTERFACES (3000-3999)
├── 3000: Forgejo (Git)
├── 3000: Supabase Studio
├── 3000: Memgraph Lab  
├── 3000: Agno API
├── 3000: Langfuse Dashboard
├── 3000: Termix
├── 3001: Dagster
├── 3001: Pangolin API
└── 3903: Garage Web UI

API ENDPOINTS (4000-4999)
├── 4000: LiteLLM Proxy
└── (Various internal APIs)

DATABASES & STORES (5000-5999)
├── 5000: MLFlow
├── 5432: PostgreSQL (multiple instances)
└── (Database internal ports)

SEARCH & VECTOR DBS (6300-6399)
├── 6333: Qdrant REST
└── 6334: Qdrant gRPC

CACHE & KV (6370-6379)
├── 6379: Dragonfly / Redis

DATABASE POOLING (6500-6599)
└── 6543: Supabase Supavisor

GRAPH DATABASES (7600-7699)
├── 7687: Memgraph Bolt
└── 7444: Memgraph HTTPS

API GATEWAYS & SERVICES (8000-8999)
├── 8000: Supabase Kong (API Gateway)
├── 8443: Supabase Kong HTTPS
├── 8080: Infisical
└── 8080: Termix

OBJECT STORAGE (9000-9999)
├── 9000: MinIO / Garage S3 API
└── 9001: MinIO Console

SPECIAL PORTS (11000+)
└── 11235: Crawl4AI

SSH (2222)
└── 2222: Forgejo SSH
```

---

## Configuration Dependencies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      CONFIGURATION DEPENDENCIES                              │
└─────────────────────────────────────────────────────────────────────────────┘

ENVIRONMENT VARIABLES (from .env files)
├── LLM API Keys (External)
│   ├── OPENAI_API_KEY
│   ├── ANTHROPIC_API_KEY
│   ├── GROQ_API_KEY
│   ├── DEEPSEEK_API_KEY
│   └── ... (15+ other providers)
│
├── GitHub Tokens (External)
│   ├── GITHUB_TOKEN (for Dagster)
│   └── GITHUB_API_KEY
│
├── Generated Secrets (Stored Securely)
│   ├── Forgejo: FORGEJO_SECRET_KEY
│   ├── Garage: RPC_SECRET, ADMIN_API_TOKEN
│   ├── Langfuse: NEXTAUTH_SECRET, SALT, ENCRYPTION_KEY
│   ├── LiteLLM: LITELLM_MASTER_KEY, LITELLM_SALT_KEY
│   ├── Infisical: ENCRYPTION_KEY, AUTH_SECRET
│   └── Supabase: JWT_SECRET, ANON_KEY, SERVICE_ROLE_KEY
│
├── Database Credentials (Internal)
│   ├── PostgreSQL: Multiple POSTGRES_USER/PASSWORD pairs
│   ├── Memgraph: MEMGRAPH_USER, MEMGRAPH_PASSWORD
│   └── (Connection strings built from these)
│
├── Service URLs (Internal)
│   ├── FORGEJO_URL → http://forgejo:3000
│   ├── POSTGRES_HOST → postgres/db
│   ├── REDIS_HOST → dragonfly
│   ├── GRAPH_DATABASE_URL → bolt://memgraph:7687
│   └── ... (many others)
│
└── Feature Flags & Configurations
    ├── FORGEJO_DISABLE_REGISTRATION
    ├── FORGEJO_ACTIONS_ENABLED
    ├── LANGFUSE_ENABLE_EXPERIMENTAL_FEATURES
    ├── ENABLE_GPU (Crawl4AI)
    └── REPLICATION_MODE (Garage)

EXTERNAL CONFIGURATION FILES
├── docker-compose.yaml
│   └── (Service definitions, ports, volumes, networks)
│
├── Dockerfile (custom builds)
│   ├── Dagster (3x Dockerfiles)
│   └── Agno
│
├── litellm_config.yaml
│   └── (Model routes, fallbacks, settings)
│
├── garage.toml
│   └── (Storage configuration)
│
├── workspace.yaml (Dagster)
│   └── (Pipeline definitions)
│
├── dagster.yaml (Dagster)
│   └── (Executor, storage, scheduler)
│
└── config files (Pangolin, Traefik, etc.)
    └── (Various infrastructure configurations)
```

---

## Deployment Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DEPLOYMENT SEQUENCE                                     │
└─────────────────────────────────────────────────────────────────────────────┘

START
  │
  ├─ [PHASE 1] Infrastructure Foundation
  │  └─ docker-compose up
  │     ├─ dragonfly (6379) ──────────────────────┐
  │     ├─ qdrant (6333) ──────────────────────────┤
  │     ├─ memgraph (7687) ──────────────────────┤
  │     └─ (No dependencies, can start in parallel)
  │
  ├─ [PHASE 2] Core Services (wait for PG health)
  │  └─ docker-compose up
  │     ├─ forgejo (PostgreSQL + service)
  │     │  ├─ forgejo_db health check
  │     │  └─ forgejo ready
  │     ├─ supabase (many services)
  │     │  └─ postgresql health check
  │     ├─ litellm (PostgreSQL + proxy)
  │     │  └─ postgres health check
  │     ├─ langfuse (PostgreSQL + app)
  │     │  └─ postgres health check
  │     └─ mlflow (PostgreSQL + MinIO)
  │        ├─ postgres health check
  │        └─ minio health check
  │
  ├─ [PHASE 3] Orchestration & Observability
  │  └─ docker-compose up
  │     ├─ dagster (needs Forgejo ready first!)
  │     │  ├─ Forgejo must be running (package registry)
  │     │  ├─ PostgreSQL health check
  │     │  └─ All 3 containers (user_code, webserver, daemon)
  │     ├─ cognee (needs all DBs, LLM keys)
  │     ├─ crawl4ai (stateless, just needs LLM keys)
  │     └─ agno (needs PostgreSQL)
  │
  ├─ [PHASE 4] Additional Services (optional)
  │  └─ docker-compose up
  │     ├─ garage (S3 storage)
  │     ├─ pangolin (network config)
  │     └─ komodo (infra agent)
  │
  └─ [VERIFICATION]
     ├─ curl http://localhost:3001 → Dagster
     ├─ curl http://localhost:8000/rest/v1 → Supabase
     ├─ curl http://localhost:4000 → LiteLLM
     ├─ curl http://localhost:3000 → Forgejo/Langfuse
     └─ All health checks passed
        │
        └─ READY FOR USE

COMMON STARTUP ISSUES:
├── Port conflicts → Change in .env
├── Missing secrets → Generate with openssl
├── Network issues → Check docker network
├── PG not ready → Wait for health check
└── API key errors → Verify .env files
```

---

## Storage Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        STORAGE ARCHITECTURE                                   │
└─────────────────────────────────────────────────────────────────────────────┘

RELATIONAL (SQL)
├── Supabase PostgreSQL
│   ├── Auth tables (users, sessions)
│   ├── Storage (file metadata)
│   └── Custom user tables
│
├── Forgejo PostgreSQL
│   ├── Repositories
│   ├── Users & Orgs
│   ├── Issues & PRs
│   └── Packages
│
├── Dagster PostgreSQL
│   ├── Runs
│   ├── Events
│   ├── Assets
│   └── Schedules
│
├── Langfuse PostgreSQL
│   ├── Projects
│   ├── Traces
│   ├── Spans
│   └── Observations
│
├── LiteLLM PostgreSQL
│   ├── API keys
│   ├── Models
│   └── Usage logs
│
└── MLFlow PostgreSQL
    ├── Experiments
    ├── Runs
    └── Metrics/Params

GRAPH (NoSQL)
├── Memgraph
│   ├── Knowledge graphs
│   ├── Entity relationships
│   └── Computed properties
│
└── Cognee (Kuzu embedded)
    └── Entity relationships

VECTOR (Embeddings)
├── Qdrant
│   ├── Text embeddings
│   ├── Document chunks
│   └── Semantic search indexes
│
└── LanceDB (Cognee)
    └── Vector embeddings

KEY-VALUE (Cache)
├── Dragonfly (Redis-compatible)
│   ├── Session cache
│   ├── Embedding cache
│   └── Temporary data
│
└── Memgraph cache layer
    └── Query result cache

OBJECT STORAGE (Blob)
├── MinIO (MLFlow artifacts)
│   ├── Model files
│   ├── Artifacts
│   └── Datasets
│
├── Garage (S3-compatible)
│   ├── General object storage
│   ├── Backups
│   └── Archives
│
└── Supabase Storage
    ├── User uploads
    ├── Media files
    └── Documents

FILE SYSTEM (Local)
├── Docker Volumes
│   ├── pgdata (PostgreSQL volumes)
│   ├── mg_lib (Memgraph)
│   ├── garage-meta/data (Garage)
│   ├── dragonfly-data (Cache)
│   ├── qdrant_data (Vector DB)
│   ├── termix-data (Terminal)
│   └── Various other volumes
│
└── Mounted Config Directories
    ├── ./config (various services)
    ├── ./workspace.yaml (Dagster)
    ├── ./dagster.yaml (Dagster)
    ├── ./litellm_config.yaml (LiteLLM)
    └── ./garage.toml (Garage)
```

---

## Authentication & Authorization Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION ARCHITECTURE                               │
└─────────────────────────────────────────────────────────────────────────────┘

EXTERNAL AUTH SOURCES
├── GitHub (OAuth for Infisical)
├── Google (OAuth for Infisical)
├── GitLab (OAuth for Infisical)
└── Other cloud providers

INTERNAL AUTH SERVICES
│
├── Supabase GoTrue (Primary Auth Server)
│   ├── Email/Password auth
│   ├── OAuth providers
│   ├── MFA support
│   └── JWT token generation
│       ├── ANON_KEY (public)
│       └── SERVICE_ROLE_KEY (server)
│
├── Forgejo Built-in Auth
│   ├── Local users
│   ├── OAuth integration
│   └── API tokens for CI/CD
│
├── Langfuse NextAuth
│   ├── Session management
│   ├── JWT tokens
│   └── Project-level access
│
├── Infisical Custom Auth
│   ├── Local users
│   ├── SSO providers
│   └── API key auth
│
├── LiteLLM API Key Auth
│   ├── Master key verification
│   ├── Per-provider keys
│   └── Salt-based hashing
│
└── Dagster Built-in Auth
    ├── Basic HTTP auth
    ├── GraphQL API access
    └── Run-level permissions

DATA ACCESS PATTERNS
│
├── Public Access
│   ├── Supabase REST (anon key)
│   └── Public GraphQL endpoints
│
├── Authenticated Access
│   ├── User auth required
│   ├── JWT token in headers
│   └── Row-level security (RLS)
│
├── Service-to-Service
│   ├── Internal docker network
│   ├── No external auth
│   └── Database connection strings
│
└── API Token Access
    ├── Fixed API keys
    ├── Per-service tokens
    └── Vault-stored credentials
```

---

## Health & Monitoring Strategy

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MONITORING & HEALTH CHECKS                                │
└─────────────────────────────────────────────────────────────────────────────┘

SERVICE HEALTH CHECKS
├── Database Services
│   ├── PostgreSQL instances
│   │   └── pg_isready command
│   ├── Memgraph
│   │   └── Bolt protocol ping
│   ├── Qdrant
│   │   └── REST /health
│   ├── Dragonfly
│   │   └── Redis PING
│   └── MinIO
│       └── HTTP health endpoint
│
├── Application Services
│   ├── Supabase Kong
│   │   └── /status endpoint
│   ├── Dagster
│   │   ├── /graphql health
│   │   └── WebSocket availability
│   ├── LiteLLM
│   │   └── /health endpoint
│   ├── Langfuse
│   │   └── /api/health
│   ├── Crawl4AI
│   │   └── /health endpoint
│   └── Memgraph Lab
│       └── HTTP port availability
│
└── Infrastructure
    ├── Docker socket availability
    ├── Network connectivity
    ├── Volume mount accessibility
    └── DNS resolution

LOGGING AGGREGATION
├── Docker logs
│   ├── docker-compose logs
│   └── docker logs <container>
│
├── Service-specific logs
│   ├── PostgreSQL log files
│   ├── Dagster event store
│   ├── Langfuse trace database
│   └── Application stdout/stderr
│
└── Monitoring Tools (Optional)
    ├── Prometheus (metrics)
    ├── Grafana (visualization)
    ├── ELK Stack (logs)
    └── Sentry (error tracking)

OBSERVABILITY LAYER
├── Langfuse (LLM-specific)
│   ├── Traces all LLM calls
│   ├── Embeddings metadata
│   └── Cost tracking
│
├── LiteLLM logging
│   ├── Request/response logs
│   ├── Model usage
│   └── Error tracking
│
├── Dagster event logging
│   ├── Run execution events
│   ├── Asset materializations
│   └── Sensor triggers
│
└── Application metrics
    ├── Request latency
    ├── Error rates
    ├── Database connection pools
    └── Cache hit rates
```

---

## Document Map

**For Complete Reference, see:**
1. `/DOCKER_COMPOSE_ANALYSIS.md` - Detailed service breakdown
2. `/DOCKER_COMPOSE_MATRIX.md` - Quick reference matrix & deployment guide
3. `/DOCKER_COMPOSE_ARCHITECTURE.md` - This file (visual diagrams)



---

## From: DOCKER_COMPOSE_QUICKSTART.md (leftover)

# Docker Compose Analysis - Complete Documentation Index

## Overview

This directory contains comprehensive documentation for all 17 Docker Compose stacks in the `/infrastructure/compose/` directory, covering 18 containerized services organized across multiple functional domains.

**Total Documentation**: 1,985 lines across 3 documents

---

## Document Guide

### 1. DOCKER_COMPOSE_ANALYSIS.md (Detailed Reference)
**Size**: 891 lines | **Focus**: Complete service breakdown

The most comprehensive document covering:
- Each service with detailed specifications
- Environment variables required/optional
- API endpoints and SDK availability
- Build dependencies and custom images
- Inter-service dependencies

**Use this when you need:**
- Full details about a specific service
- Complete environment variable reference
- API endpoint documentation
- Build instructions
- Network integration details

**Key Sections:**
- Infrastructure Foundation (Supabase, Forgejo, Garage, Dragonfly, Qdrant, Memgraph)
- Data Processing & ETL (Cognee, Crawl4AI)
- Package & Artifact Management (Forgejo, Garage)
- LLM Operations & Orchestration (LiteLLM, MLFlow, Langfuse)
- Workflow & Orchestration (Dagster, Pangolin, Komodo)
- Development & Agentic Frameworks (Agno, Termix)
- Secrets & Configuration Management (Infisical)
- Service Dependency Matrix
- Environment Variable Management Matrix
- Network Architecture
- Build & Deployment Requirements
- Observability & Integration Chain
- Service Management Matrix
- Deployment Checklist
- Critical Integration Points
- Known Limitations & Notes

---

### 2. DOCKER_COMPOSE_MATRIX.md (Quick Reference & Deployment)
**Size**: 409 lines | **Focus**: Quick lookup and deployment guide

Fast-reference guide with:
- Service matrix (17 services in table format)
- Environment setup by category (MVP vs. Advanced)
- Secrets & keys required
- Port assignments by range
- Environment file checklist
- Deployment order (5 phases)
- Health check commands
- Common issues & solutions
- Integration summary
- Scaling considerations

**Use this when you need:**
- Quick lookup of service requirements
- Port numbers for testing
- Deployment order
- Health check commands
- Step-by-step setup instructions

**Key Sections:**
- Service Matrix (Env vars, Build, Secrets, Dependencies, Status)
- Environment Setup by Category
- Critical Path vs. Optional Services
- Secrets & Keys Required
- Port Assignments Reference
- Environment File Checklist (4-step setup)
- Deployment Order (5 phases)
- Health Check Commands
- Common Issues & Solutions
- Environment Variable Templates
- Integration Summary
- Scaling Considerations

---

### 3. DOCKER_COMPOSE_ARCHITECTURE.md (Visual Diagrams & Design)
**Size**: 685 lines | **Focus**: Architecture visualization

Comprehensive architecture documentation with ASCII diagrams:
- System architecture overview
- Data flow pipeline
- Service dependency graph
- Network topology
- Port map by service
- Configuration dependencies
- Deployment flow
- Storage architecture
- Authentication & authorization
- Health & monitoring strategy

**Use this when you need:**
- Visual understanding of system architecture
- Data flow between services
- Network topology overview
- Deployment sequence
- Storage architecture details
- Authentication flow
- Monitoring strategy

**Key Sections:**
- System Architecture Diagram (4-layer)
- Data Flow Architecture
- Service Dependency Graph (Tier 0-3)
- Network Topology
- Port Map by Service
- Configuration Dependencies
- Deployment Flow (5-phase)
- Storage Architecture
- Authentication & Authorization Flow
- Health & Monitoring Strategy

---

## Service Quick Reference

| Service | Type | Critical | Status | Env Vars | Build | Port |
|---------|------|----------|--------|----------|-------|------|
| Supabase | Core DB | Yes | Ready | 20+ | No | 8000 |
| Forgejo | Registry | Yes | Ready | 15+ | No | 3000 |
| Dagster | Orchestration | Yes | Ready | 12+ | 3x | 3001 |
| LiteLLM | LLM Proxy | High | Ready | 20+ | No | 4000 |
| Cognee | Data Engine | High | Ready | 40+ | No | - |
| Langfuse | Observability | High | Ready | 8+ | No | 3000 |
| Crawl4AI | Web Scraper | Medium | Ready | 10+ | Opt | 11235 |
| MLFlow | Model Tracking | Medium | Ready | 12+ | No | 5000 |
| Agno | Agent Framework | Medium | Ready | 8+ | Yes | 8000 |
| Garage | S3 Storage | Medium | Ready | 8+ | No | 3900 |
| Memgraph | Graph DB | Medium | Ready | 2 | No | 7687 |
| Qdrant | Vector DB | Low | Ready | 0 | No | 6333 |
| Dragonfly | Cache | Low | Ready | 2 | No | 6379 |
| Pangolin | Network Mgmt | Low | Example | 0 | No | 3001 |
| Komodo | Infra Agent | Low | Example | 4+ | No | - |
| Termix | Terminal | Utility | Ready | 1 | No | 8080 |
| Infisical | Secrets Mgmt | Low | Incomplete | 30+ | No | 8080 |

---

## Critical Path (MVP Deployment)

To get a working system, deploy in this order:

1. **Supabase** - Core database, auth, APIs (8000)
2. **Forgejo** - Git + PyPI registry (3000)
3. **Dagster** - Pipeline orchestration (3001)
4. **LiteLLM** - LLM proxy (4000)
5. **Langfuse** - Observability (3000)

Supporting services (deploy simultaneously):
- Dragonfly (6379) - Cache
- Qdrant (6333) - Vector search
- Memgraph (7687) - Graph DB

---

## Getting Started Checklist

### Preparation
- [ ] Review DOCKER_COMPOSE_MATRIX.md for overview
- [ ] Read DOCKER_COMPOSE_ANALYSIS.md for service details
- [ ] Understand DOCKER_COMPOSE_ARCHITECTURE.md topology

### Setup
- [ ] Copy all `.env.example` and `.env.template` files
- [ ] Generate security keys (openssl rand)
- [ ] Obtain LLM API keys (OpenAI, Anthropic, etc.)
- [ ] Get GitHub token for Dagster
- [ ] Configure Komodo vault references

### Deployment
- [ ] Phase 1: Infrastructure (Dragonfly, Qdrant, Memgraph)
- [ ] Phase 2: Core Services (Forgejo, Supabase, databases)
- [ ] Phase 3: Orchestration (Dagster, LiteLLM, Langfuse)
- [ ] Phase 4: Data Processing (Cognee, Crawl4AI)
- [ ] Phase 5: Advanced (Garage, Pangolin, Komodo)

### Verification
- [ ] Run health check commands (see MATRIX.md)
- [ ] Test key integrations
- [ ] Verify API endpoints accessible
- [ ] Monitor logs for errors

---

## Port Ranges

| Range | Purpose | Examples |
|-------|---------|----------|
| 3000-3001 | Web UIs | Forgejo, Dagster, Supabase, Langfuse |
| 4000-4999 | APIs | LiteLLM |
| 5000-5999 | Databases | MLFlow, PostgreSQL |
| 6300-6379 | Search/Cache | Qdrant, Dragonfly |
| 7687-7444 | Graphs | Memgraph |
| 8000-8999 | Gateways | Supabase Kong, Infisical, Termix |
| 9000-9001 | Object Storage | MinIO, Garage |
| 11235+ | Special | Crawl4AI |

---

## Key Integrations

### Data Processing Pipeline
```
Crawl4AI (scrape) → Cognee (process) → Supabase (store)
                         ↓
                    Qdrant (search)
                         ↓
                    Langfuse (observe)
```

### Orchestration Flow
```
Dagster (scheduler) → Forgejo (packages) → GitHub (data)
         ↓
      Supabase (warehouse)
```

### LLM Services Chain
```
LiteLLM (proxy) → Multiple providers (OpenAI, Anthropic, etc.)
     ↓
  Langfuse (tracing)
     ↓
  MLFlow (tracking)
```

---

## Environment Variables Summary

### Required (must have)
- OPENAI_API_KEY or other LLM API key
- GITHUB_TOKEN (for Dagster)
- Database passwords (generate with openssl)

### Generated (security-critical)
- FORGEJO_SECRET_KEY
- NEXTAUTH_SECRET, SALT, ENCRYPTION_KEY (Langfuse)
- LITELLM_MASTER_KEY, LITELLM_SALT_KEY
- RPC_SECRET, ADMIN_API_TOKEN (Garage)

### Vault-Managed (Komodo)
- Supabase credentials
- Memgraph credentials
- Multiple LLM API keys

---

## Service Dependencies Summary

**Tier 0 (No dependencies)**
- Dragonfly, Qdrant, Termix, Pangolin, Komodo

**Tier 1 (Database only)**
- Forgejo, Supabase, Memgraph, LiteLLM, Langfuse, MLFlow

**Tier 2 (Multiple services)**
- Cognee (PG + Memgraph + Dragonfly + LanceDB + LLM)
- Dagster (PG + Forgejo + GitHub + Docker)
- Crawl4AI (LLM keys)
- Agno (PostgreSQL)

---

## File Structure Reference

```
/infrastructure/compose/
├── agno/              - Agent framework
│   └── compose.yaml
├── cognee/            - Knowledge graph
│   ├── compose.yaml
│   ├── .env
│   └── .env.template
├── crawl4ai/          - Web scraper
│   ├── compose.yaml
│   └── .llm.env
├── dagster/           - Orchestration
│   ├── docker-compose.yaml
│   ├── Dockerfile*
│   ├── workspace.yaml
│   └── .env.example
├── dragonfly/         - Cache
│   └── compose.yaml
├── forgejo/           - Git + PyPI
│   ├── compose.yaml
│   └── .env.example
├── garage/            - S3 Storage
│   ├── docker-compose.yaml
│   ├── garage.toml
│   └── .env
├── infisical/         - Secrets
│   ├── .env.template (no compose.yaml)
├── komodo/            - Infra agent
│   └── periphery/compose.yaml
├── langfuse/          - Observability
│   ├── compose.yaml
│   └── .env
├── litellm/           - LLM Proxy
│   ├── compose.yaml
│   ├── litellm_config.yaml
│   └── .env.template
├── memgraph/          - Graph DB
│   ├── compose.yaml
│   └── .env.template
├── mlflow/            - Model tracking
│   └── compose.yaml
├── pangolin/          - Network mgmt
│   └── core/compose.yaml
├── qdrant/            - Vector search
│   └── compose.yaml
├── supabase/          - Core DB
│   ├── docker-compose.yml
│   └── .env
└── termix/            - Terminal
    └── compose.yaml
```

---

## Useful Commands

### List all services
```bash
cd /infrastructure/compose
ls -d */ | sort
```

### Check service status
```bash
docker-compose ps
docker-compose logs <service>
```

### Health checks
```bash
# See DOCKER_COMPOSE_MATRIX.md for full list
curl http://localhost:8000/rest/v1  # Supabase
curl http://localhost:3001          # Dagster
curl http://localhost:4000/health   # LiteLLM
```

### Generate secrets
```bash
openssl rand -hex 32    # For hex keys
openssl rand -base64 32 # For base64 keys
```

---

## For More Information

- **Detailed Service Specs**: See DOCKER_COMPOSE_ANALYSIS.md
- **Deployment Instructions**: See DOCKER_COMPOSE_MATRIX.md
- **Architecture Details**: See DOCKER_COMPOSE_ARCHITECTURE.md
- **Project Documentation**: See /CLAUDE.md (project instructions)
- **OpenSpec Guide**: See /openspec/AGENTS.md (for change proposals)

---

## Document Version

Created: November 28, 2025
Analyzed Services: 17
Total Compose Files: 15
Total Environment: 1,985 lines of documentation



---

## From: Docker Compose Setup for Data Tools.md (leftover)

# **Architecting the Composable Data Fabric: A Definitive Implementation Guide for Local-First Lakehouse Environments**

## **1\. Introduction: The Paradigm Shift to Composable Data Stacks**

The monolithic data warehouse, once the singular source of truth for enterprise analytics, is undergoing a rapid deconstruction. In its place, a "Composable Data Fabric" is emerging—an architecture defined not by a single vendor's walled garden, but by the orchestration of best-in-breed, modular components that decouple storage from compute and interface from infrastructure. This report serves as an exhaustive technical blueprint for implementing such a stack, specifically tailored to the unique requirements of a local-first, cloud-hybrid environment utilizing **Mathesar**, **Nimtable**, **Memgraph**, **DuckDB**, and **LanceDB**.  
The transition to this modular architecture is driven by the specific properties of modern data modalities. Relational data requires strict consistency; graph data requires index-free adjacency for performance; vector data requires specialized quantization for similarity search; and analytical data requires columnar compression for speed. No single database engine can perform all these tasks with optimal efficiency. Therefore, the modern data architect must construct a "Control Plane" that unifies these disparate engines into a coherent user experience.  
The objective of this analysis is to provide a rigorous, Deep Research-driven implementation strategy for deploying this stack using **Docker Compose**. While individual containers are simple to instantiate, the interoperability of this specific selection—spanning PostgreSQL, Apache Iceberg, Cypher Query Language (Graph), and Lance columnar formats—presents significant integration challenges. Specifically, bridging the gap between local Docker volumes and cloud-native storage (S3/R2) for tools like Lance Data Viewer and Nimtable requires advanced orchestration patterns, such as FUSE-based sidecars with bidirectional mount propagation.

### **1.1 The Selected Component Architecture**

The stack selected for this implementation represents a nuanced understanding of the strengths inherent in distinct data management paradigms.

| Component | Role in Fabric | Primary Data Modality | Storage Mechanism | Interface |
| :---- | :---- | :---- | :---- | :---- |
| **Mathesar** | Control Plane | Relational / OLTP | PostgreSQL (Local) | No-Code UI / SQL |
| **Nimtable** | Lakehouse Manager | Analytical / Metadata | Apache Iceberg (S3/R2) | React Web UI |
| **Memgraph** | Relationship Engine | Graph / Network | In-Memory / WAL | Memgraph Lab |
| **DuckDB** | Federated Compute | Ad-hoc OLAP | Hybrid (Parquet, CSV, DB) | DuckDB UI (WASM) |
| **LanceDB** | Semantic Memory | Vector Embeddings | Lance Format (S3/Local) | Lance Data Viewer |

**Mathesar and PostgreSQL** serve as the anchor. Unlike purely headless architectures, this stack acknowledges that metadata, user configurations, and highly transactional business logic still require the ACID guarantees of a relational database.1 Mathesar democratizes access to this layer, transforming the raw database into a collaborative interface without abstracting away the SQL power required by engineers.  
**Nimtable** introduces the "Lakehouse" paradigm. By managing Apache Iceberg tables, it allows the stack to scale storage infinitely to cloud object stores (like Cloudflare R2 or AWS S3) while maintaining transactional consistency on files. It acts as the visual "head" for the headless Iceberg REST catalog.3  
**Memgraph** addresses the "join penalty" of relational databases. For complex dependency tracking, fraud detection, or social graph analysis, recursive SQL queries are performant disasters. Memgraph provides high-performance graph traversal, and its integration via Bolt and Cypher offers a specialized lane for relationship-heavy workloads.  
**LanceDB** handles the high-dimensional vector embeddings crucial for modern AI workflows. Unlike generic blob storage, the Lance format enables random access and filtering on vectors, but it creates a challenge: viewing this opaque data requires a specialized viewer.5  
**DuckDB** is the "glue." It is the only engine capable of querying the Postgres tables, the Iceberg parquet files, and the Lance datasets with near-native performance. The DuckDB UI provides the ad-hoc analytical surface where these distinct modalities intersect.7

## **2\. The Control Plane: PostgreSQL and Mathesar Configuration**

The foundation of this composable stack is PostgreSQL. In this architecture, PostgreSQL is not merely a data store for Mathesar; it acts as the central state store for the entire fabric. It will likely house the backend database for Nimtable (which requires a JDBC connection for its own metadata) and serve as a query source for DuckDB. Therefore, the configuration must prioritize connectivity and security over isolation.

### **2.1 Mathesar Introspection and Privileges**

Mathesar functions by aggressively introspecting the PostgreSQL system catalogs to map schemas to user interfaces. This requires the Docker container for Postgres to be configured with a user that has sufficient privileges to read information\_schema and pg\_catalog. Standard Docker images for Postgres (postgres:15-alpine) initialize a superuser by default, but for a production-grade local environment, we must script the creation of dedicated users.  
The docker-entrypoint-initdb.d directory is the mechanism for this initialization. Scripts placed here run only on the first startup. For this stack, we require a script that not only sets up the Mathesar database but also prepares the database for **Nimtable**. Nimtable, as a Java-based application, requires a standard JDBC connection URL and a pre-existing database.3 If this database is missing, the container will fail to start.

### **2.2 Connectivity and Authentication (pg\_hba.conf)**

A critical insight from the research into PostgreSQL in Docker environments involves the pg\_hba.conf (Host-Based Authentication) file.1 Mathesar, Nimtable, and DuckDB will all be connecting to Postgres from *different* containers. In a default Docker bridge network, these connections appear as coming from different IP addresses within the container subnet (usually 172.x.x.x).  
By default, Postgres may be configured to trust local connections but require password authentication for TCP/IP connections. To ensure seamless interoperability, especially with the JDBC drivers used by Nimtable and the libpq used by DuckDB, the configuration must enforce scram-sha-256 or md5 password encryption. The research indicates that leaving this configuration to defaults can lead to "connection refused" or "no pg\_hba.conf entry" errors when services attempt cross-container communication.2  
Therefore, the implementation strategy must include a custom command or environment variable set in the Docker Compose file to ensure Postgres listens on all interfaces (listen\_addresses='\*') and accepts password-authenticated connections from the Docker subnet.

### **2.3 Mathesar Docker Specifics**

Mathesar itself is stateless, relying entirely on the database. The research highlights that Mathesar configuration is handled primarily through environment variables that define the connection to the "internal" database (where Mathesar stores its own state) and the "user" databases (which it manages).10 In this consolidated stack, these are physically the same Postgres instance, but logically separated databases (mathesar\_db and nimtable\_db). This separation is crucial for stability; corruption in the Lakehouse catalog (Nimtable) should not crash the Control Plane interface (Mathesar).

## **3\. The Lakehouse Layer: Nimtable and Object Storage Integration**

Nimtable serves as the visual interface for the Apache Iceberg ecosystem. Integrating this into a local Docker stack introduces complexity because Iceberg is inherently designed for distributed object storage (S3), whereas local Docker environments typically rely on block storage (volumes).

### **3.1 The Headless Catalog Challenge**

Apache Iceberg is a table format, not a database. It requires a "Catalog" to track which metadata files are current. Nimtable acts as this Catalog interface. The research indicates that Nimtable can function as a standalone REST Catalog or connect to external ones.3 For this stack, configured for self-hosting, Nimtable will manage the catalog state in the local PostgreSQL instance (discussed in Section 2\) while pointing the actual data files to a remote object store (Cloudflare R2 or AWS S3).  
This split-brain architecture—metadata in local Postgres, data in remote S3—optimizes for both speed (listing tables is fast because it's a local DB query) and scale (storage is infinite in S3).

### **3.2 Configuring Nimtable for Docker**

The primary challenge identified in the research regarding Nimtable's Docker setup is the configuration injection mechanism. While a config.yaml file is standard for bare-metal deployments, the Docker image favors environment variables for secrets to avoid baking credentials into the file system.4  
Key environment variables identified for valid configuration include:

* DATABASE\_URL: This must point to the *internal Docker DNS* name of the Postgres container (e.g., jdbc:postgresql://postgres\_control:5432/nimtable\_db), not localhost.  
* AWS\_REGION, AWS\_ACCESS\_KEY\_ID, AWS\_SECRET\_ACCESS\_KEY: These are standard SDK variables.  
* **Crucial Insight:** The AWS\_ENDPOINT variable is often necessary when using non-AWS providers like Cloudflare R2 or MinIO. The research suggests that without explicit endpoint definition, the Java AWS SDK inside Nimtable will default to aws-global and fail to find the R2 buckets.

Furthermore, snippets 3 highlight a security requirement: the default admin password must be changed upon first login. This state is persisted in the database, meaning the environment variable for the password is only effective during the very first initialization.

## **4\. The Vector Layer: LanceDB and the "Sidecar" Pattern**

The most technically demanding aspect of this stack is the integration of **Lance Data Viewer**. The research snippets 6 reveal a critical architectural constraint: Lance Data Viewer is designed primarily to browse *local* Lance datasets. The official documentation and community discussions 11 confirm that the viewer does not currently possess a native interface to authenticate and browse S3 buckets directly via API keys in the same way Nimtable does.  
This presents a conflict: the "Lakehouse" philosophy dictates data should live in S3/R2, but the tool requires a local filesystem path (/data).

### **4.1 The Rclone Solution: FUSE over Docker**

To resolve this, we must employ a "Sidecar" pattern using **rclone**. Rclone is a command-line program to manage files on cloud storage, but its capability extends to mounting remote storage as a local filesystem using FUSE (Filesystem in Userspace).12  
In this pattern, we introduce an auxiliary container (lance\_s3\_mounter) alongside the lance\_viewer container.

1. **The Mounter:** The rclone container authenticates with R2. It executes a mount command, making the remote bucket accessible at a path inside the container (e.g., /data/s3).  
2. **The Shared Volume:** A Docker volume is shared between the Mounter and the Viewer.  
3. **The Propagation Problem:** By default, a mount created *inside* a Docker container is invisible to the host and other containers, even if they share the volume. This is due to Linux mount namespaces.

### **4.2 Bidirectional Mount Propagation**

To make the R2 mount visible to the Lance Viewer, the Docker volume configuration must utilize **Mount Propagation**. Specifically, the rshared (recursive shared) propagation mode is required.12 This setting instructs the Docker daemon and the Linux kernel to replicate mount events from the container back to the host, and consequently, to any other container binding that directory with the rslave or rshared mode.  
The research into s3fs vs rclone performance 14 strongly suggests that **rclone** with VFS caching (--vfs-cache-mode full) is superior for this use case. LanceDB relies on random access reads of the columnar data. Without aggressive caching, every seek operation would trigger a high-latency HTTP request, rendering the viewer unusable. The full cache mode allows rclone to download chunks to disk and serve them locally, mimicking the performance profile LanceDB expects.

### **4.3 Container Privileges**

FUSE operations require interactions with the kernel that are restricted in standard containers. The lance\_s3\_mounter must be run with the \--privileged flag or, more granularly, with \--cap-add SYS\_ADMIN and \--device /dev/fuse.17 This grants the container permission to create the virtual filesystem required to bridge the S3-Local gap.

## **5\. The Analytical Layer: DuckDB UI**

DuckDB functions as the universal query engine. The ibero-data/duck-ui image 18 provides a web-based SQL IDE. However, there is a fundamental distinction in deployment modes identified in the research: **WASM (Client-Side)** vs. **External (Server-Side)**.

### **5.1 The WASM Limitation**

The default mode of DuckDB UI runs DuckDB via WebAssembly inside the user's browser. While secure and fast for local CSV imports, this creates a "Localhost Paradox." The browser cannot access the Docker network directly. It cannot connect to postgres\_control:5432 because that DNS name exists only inside the Docker bridge network, not on the user's machine.19

### **5.2 The External Server Solution**

To allow DuckDB to query the other components of the stack (Postgres, Memgraph), the UI should ideally connect to a backend DuckDB instance running *inside* the Docker network. However, standard DuckDB is an in-process library, not a server.  
The snippets 18 reference "duckdb-server" projects and the ability of the UI to connect to an external host. For this report, we will configure the DuckDB UI environment variables to hint at an external connection, but given the user's request for "ad-hoc analytical queries spanning the stack," the most robust immediate solution for *S3/R2* analysis (which is the primary request involving Nimtable and Lance) is actually the WASM mode configured with S3 secrets.  
To bridge the stack fully, one would typically run a Python script using duckdb and fastapi to expose a SQL endpoint, but the standard duckdb \--ui command in a container also serves this purpose. We will focus on configuring the UI to handle the S3/R2 connection natively via the httpfs extension, which works excellently in WASM mode for querying the data lake managed by Nimtable.

### **5.3 S3 Configuration in DuckDB**

Whether running in WASM or Server mode, DuckDB requires specific SQL commands to authenticate with R2. The httpfs extension must be loaded. The research 21 highlights that for Cloudflare R2, one should use the S3 secret type but explicitly override the ENDPOINT. The URL\_STYLE parameter must often be set to path rather than vhost for compatibility with non-AWS endpoints.

## **6\. Comprehensive Docker Compose Implementation Strategy**

Based on the synthesis of the above requirements—Postgres introspection, JDBC connections for Nimtable, FUSE sidecars for LanceDB, and S3-enabled DuckDB—the following docker-compose.yml represents the optimal configuration.

### **6.1 Prerequisite Directory Structure**

Before deploying, the host file system must be prepared to support the bind mounts and sidecar patterns.

Bash

mkdir \-p data\_fabric/postgres\_data  
mkdir \-p data\_fabric/memgraph\_data  
mkdir \-p data\_fabric/memgraph\_lib  
mkdir \-p data\_fabric/lance\_mount\_point  
mkdir \-p data\_fabric/init-scripts  
touch data\_fabric/.env

### **6.2 The Master Docker Compose Configuration**

The file below integrates all findings. It uses a unifying data\_fabric bridge network to allow internal DNS resolution.

YAML

version: '3.8'

networks:  
  data\_fabric:  
    driver: bridge  
    name: data\_fabric

volumes:  
  postgres\_data:  
  memgraph\_data:  
  memgraph\_lib:

services:  
  \# \==========================================  
  \# 1\. CONTROL PLANE: PostgreSQL \+ Mathesar  
  \# \==========================================  
  postgres\_control:  
    image: postgres:15-alpine  
    container\_name: postgres\_control  
    restart: unless-stopped  
    environment:  
      POSTGRES\_USER: ${PG\_USER:-admin}  
      POSTGRES\_PASSWORD: ${PG\_PASSWORD:-securepassword}  
      POSTGRES\_DB: mathesar\_db  
      PGDATA: /var/lib/postgresql/data/pgdata  
    volumes:  
      \- postgres\_data:/var/lib/postgresql/data  
      \-./init-scripts:/docker-entrypoint-initdb.d  
    networks:  
      \- data\_fabric  
    healthcheck:  
      test:  
      interval: 5s  
      timeout: 5s  
      retries: 5  
    \# Expose for local debugging, but internal comms happen via network  
    ports:  
      \- "5432:5432"  
    \# Command ensures listening on all interfaces for Docker networking  
    command: postgres \-c 'listen\_addresses=\*'

  mathesar:  
    image: mathesar/mathesar:latest  
    container\_name: mathesar\_ui  
    restart: unless-stopped  
    depends\_on:  
      postgres\_control:  
        condition: service\_healthy  
    environment:  
      DJANGO\_SECRET\_KEY: ${MATHESAR\_SECRET\_KEY:-unsafe\_dev\_key}  
      \# Connection to the DB where Mathesar stores its internal state  
      MATHESAR\_DATABASES\_host: postgres\_control  
      MATHESAR\_DATABASES\_port: 5432  
      MATHESAR\_DATABASES\_name: mathesar\_db  
      MATHESAR\_DATABASES\_user: ${PG\_USER:-admin}  
      MATHESAR\_DATABASES\_password: ${PG\_PASSWORD:-securepassword}  
      \# Connection to the DB Mathesar allows users to edit (Same instance here)  
      MATHESAR\_MODELS\_DATABASE\_HOST: postgres\_control  
      MATHESAR\_MODELS\_DATABASE\_PORT: 5432  
      MATHESAR\_MODELS\_DATABASE\_NAME: mathesar\_db  
      MATHESAR\_MODELS\_DATABASE\_USER: ${PG\_USER:-admin}  
      MATHESAR\_MODELS\_DATABASE\_PASSWORD: ${PG\_PASSWORD:-securepassword}  
    ports:  
      \- "8000:8000"  
    networks:  
      \- data\_fabric

  \# \==========================================  
  \# 2\. LAKEHOUSE MANAGER: Nimtable  
  \# \==========================================  
  nimtable:  
    image: nimtable/nimtable:latest  
    container\_name: nimtable  
    restart: unless-stopped  
    depends\_on:  
      postgres\_control:  
        condition: service\_healthy  
    environment:  
      \# Initial Admin Credentials (Must be changed in UI after first login)  
      ADMIN\_USERNAME: ${NIMTABLE\_ADMIN\_USER:-admin}  
      ADMIN\_PASSWORD: ${NIMTABLE\_ADMIN\_PASS:-admin}  
      \# Backend connection for Nimtable's own metadata  
      DATABASE\_URL: jdbc:postgresql://postgres\_control:5432/nimtable\_db  
      DATABASE\_USERNAME: ${PG\_USER:-admin}  
      DATABASE\_PASSWORD: ${PG\_PASSWORD:-securepassword}  
      \# S3/R2 Credentials for Iceberg Data  
      AWS\_REGION: ${AWS\_REGION:-auto}  
      AWS\_ACCESS\_KEY\_ID: ${AWS\_ACCESS\_KEY\_ID}  
      AWS\_SECRET\_ACCESS\_KEY: ${AWS\_SECRET\_ACCESS\_KEY}  
      AWS\_ENDPOINT: ${AWS\_ENDPOINT}  
      AW\[23\]\_PATH\_STYLE\_ACCESS: "true"  
    ports:  
      \- "3000:3000"  
    networks:  
      \- data\_fabric

  \# \==========================================  
  \# 3\. GRAPH ENGINE: Memgraph  
  \# \==========================================  
  memgraph:  
    image: memgraph/memgraph-platform:latest  
    container\_name: memgraph\_platform  
    restart: unless-stopped  
    ports:  
      \- "7687:7687"   \# Bolt Protocol (for drivers)  
      \- "7444:7444"   \# Logging  
      \- "3001:3000"   \# Lab UI (Mapped to 3001 to avoid conflict with Nimtable)  
    environment:  
      MEMGRAPH\_USER: ${MEMGRAPH\_USER:-admin}  
      MEMGRAPH\_PASSWORD: ${MEMGRAPH\_PASSWORD:-memgraph}  
    volumes:  
      \- memgraph\_data:/var/lib/memgraph  
      \- memgraph\_lib:/var/lib/memgraph/lib  
    networks:  
      \- data\_fabric

  \# \==========================================  
  \# 4\. ANALYTICS: DuckDB UI  
  \# \==========================================  
  duckdb\_ui:  
    image: ghcr.io/ibero-data/duck-ui:latest  
    container\_name: duckdb\_ui  
    restart: unless-stopped  
    ports:  
      \- "5522:5522"  
    environment:  
      \# Enable unsigned extensions to allow httpfs (S3) loading  
      DUCK\_UI\_ALLOW\_UNSIGNED\_EXTENSIONS: "true"  
      \# Hint parameters for external connections (optional usage)  
      DUCK\_UI\_EXTERNAL\_CONNECTION\_NAME: "Local Fabric"  
    networks:  
      \- data\_fabric

  \# \==========================================  
  \# 5\. VECTOR VIEWER & SIDECAR  
  \# \==========================================  
    
  \# The Sidecar: Mounts S3/R2 as a local filesystem using FUSE  
  lance\_s3\_mounter:  
    image: rclone/rclone:latest  
    container\_name: lance\_s3\_mounter  
    \# Capabilities required for FUSE mounting  
    privileged: true   
    cap\_add:  
      \- SYS\_ADMIN  
    devices:  
      \- /dev/fuse  
    environment:  
      \# Inject Rclone config for Cloudflare R2/S3  
      RCLONE\_CONFIG\_R2\_TYPE: s3  
      RCLONE\_CONFIG\_R2\_PROVIDER: Cloudflare  
      RCLONE\_CONFIG\_R2\_ACCESS\_KEY\_ID: ${AWS\_ACCESS\_KEY\_ID}  
      RCLONE\_CONFIG\_R2\_SECRET\_ACCESS\_KEY: ${AWS\_SECRET\_ACCESS\_KEY}  
      RCLONE\_CONFIG\_R2\_ENDPOINT: ${AWS\_ENDPOINT}  
      RCLONE\_CONFIG\_R2\_ACL: private  
    command: \>  
      mount r2:${S3\_BUCKET\_NAME} /data/s3  
      \--allow-other  
      \--vfs-cache-mode full  
      \--vfs-cache-max-size 5G  
      \--dir-cache-time 1m  
      \--poll-interval 1m  
    volumes:  
      \# The critical bind propagation: rshared makes the mount visible to other containers  
      \- type: bind  
        source:./lance\_mount\_point  
        target: /data/s3  
        bind:  
          propagation: rshared  
    networks:  
      \- data\_fabric

  lance\_viewer:  
    image: ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3  
    container\_name: lance\_viewer  
    restart: unless-stopped  
    depends\_on:  
      \- lance\_s3\_mounter  
    ports:  
      \- "8080:8080"  
    volumes:  
      \# Mounts the same host directory, seeing the files Rclone provides  
      \- type: bind  
        source:./lance\_mount\_point  
        target: /data  
        read\_only: true  
    networks:  
      \- data\_fabric

### **6.3 Database Initialization Script (init-scripts/01-init.sql)**

This script ensures the PostgreSQL instance is ready for both Mathesar (which uses the default DB or creates its own schema) and Nimtable (which needs a specific DB to exist upon connection).

SQL

\-- Create database for Nimtable Catalog  
CREATE DATABASE nimtable\_db;

\-- Create dedicated user for Nimtable  
CREATE USER nimtable\_user WITH ENCRYPTED PASSWORD 'securepassword';  
GRANT ALL PRIVILEGES ON DATABASE nimtable\_db TO nimtable\_user;

\-- Mathesar typically uses the root user or its own configured user to manage other DBs  
\-- Ensure the default admin has access  
GRANT ALL PRIVILEGES ON DATABASE nimtable\_db TO admin;

## **7\. Deep Dive: Integration and Interoperability Insights**

### **7.1 The Mechanism of the Rclone Sidecar**

The configuration of the lance\_s3\_mounter is the pivotal element enabling the Lance Data Viewer to function in a cloud-hybrid environment. The standard Docker volume driver is unaware of the contents of S3. By using rclone mount, we essentially turn the /data/s3 directory inside the container into a gateway to the cloud.  
The command flags are selected based on specific performance behaviors:

* \--vfs-cache-mode full: This is non-negotiable for database files. LanceDB (and DuckDB) performs random access reads on the .lance or .parquet files. Standard S3 streaming does not support seeking efficiently. This flag forces Rclone to download requested chunks to a local disk cache (/var/cache/rclone), effectively turning the container into a high-performance caching proxy.  
* \--allow-other: By default, FUSE mounts are owned by the user who created them (root in the container). Without this flag, the file system would be invisible to the host or any other container, even with shared volumes.  
* bind: propagation: rshared: This is a Linux kernel namespace feature. It allows the "mount event" (the act of Rclone connecting S3 to /data/s3) to propagate up to the host OS and down into any other container that binds the same directory. Without this, the Lance Viewer would see an empty directory.

### **7.2 Networking and DNS Resolution**

Within the data\_fabric network, services utilize Docker's embedded DNS server. This allows for resilient configuration that is independent of the host machine's IP address.

* **Nimtable to Postgres:** Uses postgres\_control. If Nimtable were configured to use localhost, it would fail, as localhost inside the Nimtable container refers to itself.  
* **Port Conflicts:** A common operational hazard in such stacks is the conflict on port 3000\. Both Memgraph Lab and Nimtable default to this port. The configuration resolves this by mapping Memgraph Lab's internal 3000 to external 3001 (3001:3000), leaving 3000 clear for Nimtable.

## **8\. Operational Workflows and Day 2 Configuration**

### **8.1 Configuring DuckDB UI for the Data Fabric**

Once the stack is operational, the DuckDB UI (accessible at http://localhost:5522) acts as the analytical console. Because it is running in WASM, it cannot inherently "see" the postgres\_control container via Docker DNS. It interacts with the outside world via HTTP.  
To query the Iceberg data managed by Nimtable or the Lance data viewed by Lance Viewer, the user must configure the S3 secret within the DuckDB session. The research confirms that the httpfs extension is the enabler here.  
**Required SQL for DuckDB Session:**

SQL

INSTALL httpfs;  
LOAD httpfs;

CREATE SECRET r2\_access (  
    TYPE S3,  
    KEY\_ID 'your\_access\_key',  
    SECRET 'your\_secret\_key',  
    REGION 'auto',  
    ENDPOINT 'your-account-id.r2.cloudflarestorage.com',  
    URL\_STYLE 'path'  
);

With this secret active, DuckDB can perform zero-copy queries on the Parquet files stored in the R2 bucket, which are simultaneously being managed by Nimtable.

### **8.2 Mathesar as the Control Hub**

Accessing http://localhost:8000 opens Mathesar. Upon first load, it will ask to connect to a database. The user should input the credentials for postgres\_control. Mathesar will then introspect the nimtable\_db (if permitted) and any other databases created. This provides a user-friendly interface to modify the *metadata* of the Lakehouse (e.g., changing table descriptions in the Nimtable backing store) without needing to write raw SQL updates.

### **8.3 Connecting to Memgraph**

Memgraph Lab is accessible at http://localhost:3001. The "Quick Connect" feature will default to localhost:7687. Since the Lab is running in a container but the browser is on the host, localhost works because we exposed port 7687 in the Compose file. However, if using a programmatic driver from *another* container (e.g., a Python script in a separate container), the address must be memgraph\_platform:7687.

## **9\. Security and Future Considerations**

### **9.1 Credential Management**

The use of a .env file is standard practice, but for production environments, Docker Secrets would be the superior mechanism. The current setup passes sensitive keys (AWS\_SECRET\_ACCESS\_KEY) as plain text environment variables to the containers. Any process capable of inspecting docker inspect can view these keys. For a local research environment, this is acceptable, but it constitutes a risk in shared environments.

### **9.2 The "Headless" Vector Viewer Limitation**

The research identified a significant gap in the Lance ecosystem: the lack of a native, authenticated S3 viewer. The solution provided (Sidecar) is robust but heavyweight. It requires a privileged container and significant memory for the VFS cache. Future iterations of this stack should monitor the lance-data-viewer roadmap for native S3 support, which would eliminate the need for the lance\_s3\_mounter service and simplify the architecture significantly.

### **9.3 Performance Tuning**

The vfs-cache-max-size in the Rclone sidecar is set to 5G. For datasets exceeding this size, Rclone will begin evicting chunks. If the Lance Viewer frequently accesses random segments of large datasets, this thrashing will degrade performance. Users should scale this parameter to match their available disk space and dataset working set size.

## **10\. Conclusion**

This report has detailed the architecture and implementation of a Composable Data Fabric using Mathesar, Nimtable, Memgraph, DuckDB, and LanceDB. By leveraging Docker Compose, we have created a unified environment that respects the distinct storage requirements of each tool while enabling interoperability through shared networks and advanced volume propagation.  
The resulting stack is a powerful, local-first data engineering platform. It allows for:

1. **Visual Management** of huge data lakes via Nimtable.  
2. **No-Code Interaction** with relational data via Mathesar.  
3. **Deep Relationship Analysis** via Memgraph.  
4. **Vector Debugging** via Lance Viewer (bridged to S3).  
5. **Unified Analytics** via DuckDB.

This architecture moves beyond simple container orchestration to solve the fundamental data gravity and access problems inherent in modern, multi-modal data stacks.

#### **Works cited**

1. Setting up TLS connection for containerized PostgreSQL database \- DEV Community, accessed December 1, 2025, [https://dev.to/whchi/setting-up-tls-connection-for-containerized-postgresql-database-1kmh](https://dev.to/whchi/setting-up-tls-connection-for-containerized-postgresql-database-1kmh)  
2. Can't get postgres to work \- Compose \- Docker Community Forums, accessed December 1, 2025, [https://forums.docker.com/t/cant-get-postgres-to-work/29580](https://forums.docker.com/t/cant-get-postgres-to-work/29580)  
3. nimtable/nimtable: The observability platform for Iceberg ... \- GitHub, accessed December 1, 2025, [https://github.com/nimtable/nimtable](https://github.com/nimtable/nimtable)  
4. Nimtable: The Control Plane for Apache Iceberg™ | by RisingWave Labs | Towards Dev, accessed December 1, 2025, [https://medium.com/towardsdev/nimtable-the-control-plane-for-apache-iceberg-aa230a32f7e1](https://medium.com/towardsdev/nimtable-the-control-plane-for-apache-iceberg-aa230a32f7e1)  
5. LanceDB | Vector Database for RAG, Agents & Hybrid Search, accessed December 1, 2025, [https://lancedb.com/](https://lancedb.com/)  
6. Introducing Lance Data Viewer: A Simple Way to Explore Lance Tables \- LanceDB, accessed December 1, 2025, [https://lancedb.com/blog/lance-data-viewer/](https://lancedb.com/blog/lance-data-viewer/)  
7. The DuckDB Local UI, accessed December 1, 2025, [https://duckdb.org/2025/03/12/duckdb-ui](https://duckdb.org/2025/03/12/duckdb-ui)  
8. DuckDB Wasm, accessed December 1, 2025, [https://duckdb.org/docs/stable/clients/wasm/overview](https://duckdb.org/docs/stable/clients/wasm/overview)  
9. How to connect to a Postgres DB (running in a container not installed locally)? · apache superset · Discussion \#30880 \- GitHub, accessed December 1, 2025, [https://github.com/apache/superset/discussions/30880](https://github.com/apache/superset/discussions/30880)  
10. Connection string for postgresql in docker-compose.yml file \- Stack Overflow, accessed December 1, 2025, [https://stackoverflow.com/questions/51442323/connection-string-for-postgresql-in-docker-compose-yml-file](https://stackoverflow.com/questions/51442323/connection-string-for-postgresql-in-docker-compose-yml-file)  
11. lance-format/lance-data-viewer: Browse Lance tables from your local machine in a simple web UI. No database to set up. Mount a folder and go. \- GitHub, accessed December 1, 2025, [https://github.com/lancedb/lance-data-viewer](https://github.com/lancedb/lance-data-viewer)  
12. Propogating rclone mounts to Docker containers without transport endpoint going stale, accessed December 1, 2025, [https://forum.rclone.org/t/propogating-rclone-mounts-to-docker-containers-without-transport-endpoint-going-stale/48112](https://forum.rclone.org/t/propogating-rclone-mounts-to-docker-containers-without-transport-endpoint-going-stale/48112)  
13. Docker Volume Plugin \- Rclone, accessed December 1, 2025, [https://rclone.org/docker/](https://rclone.org/docker/)  
14. Why rclone mount will be faster that the original s3 interface \- Help and Support, accessed December 1, 2025, [https://forum.rclone.org/t/why-rclone-mount-will-be-faster-that-the-original-s3-interface/46935](https://forum.rclone.org/t/why-rclone-mount-will-be-faster-that-the-original-s3-interface/46935)  
15. Achieving s3fs performance with rclone mount \- Help and Support, accessed December 1, 2025, [https://forum.rclone.org/t/achieving-s3fs-performance-with-rclone-mount/9644](https://forum.rclone.org/t/achieving-s3fs-performance-with-rclone-mount/9644)  
16. Achieving s3fs performance with rclone mount \- Page 2 \- Help and Support, accessed December 1, 2025, [https://forum.rclone.org/t/achieving-s3fs-performance-with-rclone-mount/9644?page=2](https://forum.rclone.org/t/achieving-s3fs-performance-with-rclone-mount/9644?page=2)  
17. Is s3fs not able to mount inside docker container? \- Stack Overflow, accessed December 1, 2025, [https://stackoverflow.com/questions/24966347/is-s3fs-not-able-to-mount-inside-docker-container](https://stackoverflow.com/questions/24966347/is-s3fs-not-able-to-mount-inside-docker-container)  
18. Getting Started \- Duck-UI, accessed December 1, 2025, [https://duckui.com/getting-started.html](https://duckui.com/getting-started.html)  
19. DuckDB Docker Container, accessed December 1, 2025, [https://duckdb.org/docs/stable/operations\_manual/duckdb\_docker](https://duckdb.org/docs/stable/operations_manual/duckdb_docker)  
20. A curated list of awesome DuckDB resources \- GitHub, accessed December 1, 2025, [https://github.com/davidgasquez/awesome-duckdb](https://github.com/davidgasquez/awesome-duckdb)  
21. S3 API Support \- DuckDB, accessed December 1, 2025, [https://duckdb.org/docs/stable/core\_extensions/httpfs/s3api](https://duckdb.org/docs/stable/core_extensions/httpfs/s3api)  
22. Connect DuckDB to S3 with Role-Based Credentials \- Stack Overflow, accessed December 1, 2025, [https://stackoverflow.com/questions/79348716/connect-duckdb-to-s3-with-role-based-credentials](https://stackoverflow.com/questions/79348716/connect-duckdb-to-s3-with-role-based-credentials)
