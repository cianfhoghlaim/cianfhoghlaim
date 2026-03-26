# Crypto Flow Integration Outline

## Master Synthesis Document

This document synthesizes findings from all example analyses into a unified integration plan for the crypto analytics and AI agent platform.

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER                                 │
│  TanStack Start + shadcn/ui + DuckDB-Wasm                               │
│  - Route-level data loading                                              │
│  - Client-side analytics                                                 │
│  - WebSocket streaming for agent responses                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       ORCHESTRATION LAYER                                │
│  Restate (TypeScript) + Convex (Real-time)                              │
│  - MCP server for AI agent tools                                         │
│  - Virtual objects for user sessions                                     │
│  - Durable workflows for multi-step crypto operations                   │
│  - Real-time subscriptions for UI updates                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          AGENT LAYER                                     │
│  Agno + Eliza Patterns + DBOS Durability                                │
│  - Character system for agent personas                                   │
│  - Provider pattern for context injection                                │
│  - Evaluator pattern for post-interaction learning                      │
│  - Multi-type memory (transactions, observations, assessments)          │
│  - BAML for structured outputs                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA PIPELINE LAYER                               │
│  crawl4ai + DLT + Dagster                                               │
│  - Web scraping with JavaScript rendering                                │
│  - Schema inference and incremental loading                             │
│  - Asset-based orchestration                                            │
│  - R2 storage destination                                               │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       ANALYTICS LAYER                                    │
│  RisingWave + Dragonfly                                                 │
│  - Streaming SQL with materialized views                                │
│  - HOP/TUMBLE windows for time-series aggregations                      │
│  - Redis-compatible cache for hot data                                  │
│  - Celery broker for async tasks                                        │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       KNOWLEDGE LAYER                                    │
│  Cognee + LanceDB                                                       │
│  - Knowledge graph for entities and relationships                       │
│  - Vector embeddings for semantic search                                │
│  - Hybrid queries (graph + vector)                                      │
│  - Long-term memory for agents                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        STORAGE LAYER                                     │
│  Cloudflare R2 + DuckDB + Postgres                                      │
│  - Parquet files on R2 (zero egress)                                    │
│  - DuckDB for analytical queries                                        │
│  - Postgres for transactional data (DBOS, Cognee)                       │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Technology Mapping

### Selected Technologies by Layer

| Layer | Primary | Alternative | Source Example |
|-------|---------|-------------|----------------|
| **Frontend** | TanStack Start + shadcn | - | `examples/frontend/crypto-charts/` |
| **Orchestration (TS)** | Restate | Temporal | `examples/restate/` |
| **Orchestration (Python)** | DBOS | Temporal | `examples/dbos/pydantic/` |
| **Real-time** | Convex | Restate WS | Project spec |
| **Agents** | Agno | Eliza patterns | `examples/agno/`, `examples/eliza/` |
| **Scraping** | crawl4ai | - | `examples/crawl4ai/` |
| **Data Loading** | DLT | - | Project spec |
| **Orchestration** | Dagster | - | Project spec |
| **Streaming SQL** | RisingWave | - | `examples/risingwave/` |
| **Cache/Queue** | Dragonfly | Redis | `examples/dragonfly/` |
| **Knowledge Graph** | Cognee | - | Project spec |
| **Vector DB** | LanceDB | - | Project spec |
| **Schema** | BAML | - | `examples/baml/` |

---

## 3. Data Flow Patterns

### Pattern 1: Document Ingestion

```
Source (Web/PDF)
    ↓
crawl4ai (extract markdown)
    ↓
BAML (structured extraction)
    ↓
DLT resource (schema inference)
    ↓
R2 (Parquet storage)
    ↓
Cognee (knowledge graph)
    ↓
LanceDB (embeddings)
```

**Use Cases:**
- Protocol documentation scraping
- Whitepaper analysis
- News sentiment extraction
- Governance proposal indexing

### Pattern 2: Real-Time Market Data

```
Blockchain RPC / Exchange API
    ↓
Kafka topic
    ↓
RisingWave (streaming SQL)
    ↓
Materialized Views (HOP/TUMBLE windows)
    ↓
Dragonfly (cache layer)
    ↓
Frontend (WebSocket/polling)
```

**Use Cases:**
- Price feeds and charts
- Volume analytics
- TVL tracking
- Liquidation monitoring

### Pattern 3: Agent Workflow

```
User Query (Frontend)
    ↓
Restate MCP Server (tool discovery)
    ↓
Agno Agent (DBOS-wrapped)
    ├── Provider context (portfolio, market)
    ├── Tool execution (blockchain RPC, APIs)
    ├── Knowledge retrieval (Cognee + LanceDB)
    └── BAML structured output
    ↓
Evaluator (post-response analysis)
    ↓
Memory storage (typed memories)
    ↓
Response streaming (WebSocket)
```

**Use Cases:**
- DeFi strategy analysis
- Smart contract review
- Portfolio optimization
- Risk assessment

### Pattern 4: Transaction Reconciliation

```
Transaction Intent
    ↓
Restate workflow (durable execution)
    ↓
Blockchain submission
    ↓
Dragonfly + Celery (polling queue)
    ↓
Confirmation check (exponential backoff)
    ↓
Ledger update (DBOS)
    ↓
Event notification (Convex)
```

**Use Cases:**
- Trade execution
- Token swaps
- Yield harvesting
- Gas optimization

---

## 4. Integration Points

### BAML Integration

**Schema Locations:**
- `baml_src/crypto_document.baml` - Document extraction schemas
- `baml_src/agent_outputs.baml` - Agent response structures
- `baml_src/market_analysis.baml` - Market data extraction

**Generated Outputs:**
- Python: Pydantic models for Agno agents
- TypeScript: Interfaces for frontend type safety
- Zod: Runtime validation schemas

### Restate MCP Integration

**Tool Categories:**
- `portfolio.*` - Portfolio queries and mutations
- `market.*` - Market data tools
- `agent.*` - Agent orchestration
- `blockchain.*` - On-chain operations

**Virtual Objects:**
- `UserSession` - Per-user conversation state
- `Portfolio` - User portfolio state
- `AgentContext` - Agent execution context

### Dragonfly Patterns

**Cache Keys:**
- `price:{symbol}` - Current prices (60s TTL)
- `portfolio:{user_id}` - Portfolio state (5m TTL)
- `market:fear_greed` - Market sentiment (15m TTL)
- `agent:context:{session_id}` - Agent context (1h TTL)

**Queue Patterns:**
- `reconciliation` - Transaction confirmation queue
- `analytics` - Background analytics tasks
- `notifications` - User notification queue

### RisingWave Views

**Core Views:**
- `block_stats` - Per-block aggregations
- `tx_volume_5min` - 5-minute transaction volumes
- `defi_metrics_hourly` - Hourly DeFi protocol metrics
- `sentiment_rolling` - Rolling sentiment scores

---

## 5. Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Infrastructure:**
- [ ] Set up Restate server
- [ ] Configure DBOS with Postgres
- [ ] Deploy Dragonfly instance
- [ ] Configure R2 bucket

**Core Integrations:**
- [ ] Create BAML schemas for crypto documents
- [ ] Implement crawl4ai → DLT pipeline
- [ ] Set up basic Agno agent with DBOS wrapper
- [ ] Configure Restate MCP server

**Deliverables:**
- Working document ingestion pipeline
- Basic agent with durability
- MCP tool discovery

### Phase 2: Analytics (Week 3-4)

**RisingWave:**
- [ ] Deploy RisingWave cluster
- [ ] Create Kafka sources
- [ ] Implement materialized views
- [ ] Connect cache layer

**Dragonfly Patterns:**
- [ ] Implement cache strategies
- [ ] Set up Celery workers
- [ ] Create reconciliation queue

**Deliverables:**
- Real-time market analytics
- Transaction reconciliation flow
- Cache-backed API endpoints

### Phase 3: Agents (Week 5-6)

**Agno Enhancement:**
- [ ] Implement Character system
- [ ] Create Provider classes
- [ ] Build Evaluator framework
- [ ] Implement multi-type memory

**Knowledge Integration:**
- [ ] Connect Cognee graph
- [ ] Configure LanceDB
- [ ] Build RAG pipeline

**Deliverables:**
- Full-featured crypto agents
- Knowledge-enhanced responses
- Post-interaction learning

### Phase 4: Frontend (Week 7-8)

**Components:**
- [ ] WalletConnect button
- [ ] ChainSelector
- [ ] TokenCommand search
- [ ] PriceChart
- [ ] PortfolioCard

**Integration:**
- [ ] TanStack Query + WebSocket
- [ ] Restate streaming integration
- [ ] DuckDB-Wasm analytics

**Deliverables:**
- Production-ready dashboard
- Real-time updates
- Agent chat interface

---

## 6. File Structure

```
/data/flows/crypto/
├── analysis/                          # Analysis documents
│   ├── workflow-comparison.md         # Temporal vs Restate vs DBOS
│   ├── eliza-patterns.md              # Patterns to adopt in Agno
│   ├── frontend-patterns.md           # shadcn component patterns
│   └── integration-outline.md         # This document
├── src/                               # Implementation
│   ├── workflows/                     # Restate TypeScript workflows
│   │   ├── portfolio.ts               # Portfolio operations
│   │   ├── transaction.ts             # Transaction workflows
│   │   └── mcp-server.ts              # MCP tool server
│   ├── agents/                        # Agno agents
│   │   ├── character.py               # Character system
│   │   ├── providers.py               # Provider pattern
│   │   ├── evaluators.py              # Evaluator pattern
│   │   ├── memory.py                  # Multi-type memory
│   │   ├── services.py                # Service registry
│   │   └── crypto_agent.py            # Main agent
│   └── pipelines/                     # Data pipelines
│       ├── documents.py               # Document ingestion
│       ├── market_data.py             # Market data pipeline
│       └── dagster_assets.py          # Dagster orchestration
├── baml_src/                          # BAML schemas
│   ├── crypto_document.baml           # Document extraction
│   ├── agent_outputs.baml             # Agent responses
│   └── generators.baml                # Code generation config
├── compose/                           # Infrastructure
│   └── docker-compose.yml             # Local development stack
├── examples/                          # Reference examples (existing)
├── research/                          # Research documents (existing)
└── openspec/                          # Change proposals (existing)
```

---

## 7. Configuration Requirements

### Environment Variables

```bash
# Restate
RESTATE_ADMIN_URL=http://localhost:9070
RESTATE_INGRESS_URL=http://localhost:8080

# DBOS
DBOS_DATABASE_URL=postgresql://postgres@localhost:5432/dbos

# Dragonfly
DRAGONFLY_URL=redis://localhost:6380

# RisingWave
RISINGWAVE_URL=postgresql://localhost:4566/dev

# Storage
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_BUCKET_NAME=crypto-data

# AI
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...

# Blockchain
ETH_RPC_URL=...
SOLANA_RPC_URL=...
```

### Docker Compose Services

```yaml
services:
  restate:
    image: docker.restate.dev/restatedev/restate:latest
    ports:
      - "8080:8080"   # Ingress
      - "9070:9070"   # Admin

  dragonfly:
    image: docker.dragonflydb.io/dragonflydb/dragonfly
    ports:
      - "6380:6379"

  risingwave:
    image: risingwavelabs/risingwave:latest
    ports:
      - "4566:4566"   # Frontend
      - "5691:5691"   # Meta
      - "6660:6660"   # Compute

  postgres:
    image: postgres:15
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: dbos

  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
```

---

## 8. Success Criteria

### Phase 1 Completion
- [ ] Document ingestion pipeline processes PDFs and web pages
- [ ] Agent responds with structured outputs via BAML
- [ ] MCP tools discoverable in Restate admin

### Phase 2 Completion
- [ ] Real-time price updates < 5 second latency
- [ ] Transaction reconciliation handles 100+ tx/day
- [ ] Materialized views update incrementally

### Phase 3 Completion
- [ ] Agent maintains context across sessions
- [ ] Knowledge retrieval improves response quality
- [ ] Evaluators log decisions for review

### Phase 4 Completion
- [ ] Dashboard loads in < 2 seconds
- [ ] Wallet connects across EVM + Solana
- [ ] Agent responses stream in real-time

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Restate learning curve | Start with simple workflows, iterate |
| RisingWave complexity | Use existing Solana example as template |
| Multi-chain complexity | Start with EVM only, add Solana later |
| Agent reliability | DBOS wrapper ensures durability |
| Knowledge quality | Implement evaluators early for feedback |

---

## 10. Next Steps

1. **Immediate**: Create BAML schemas for crypto document extraction
2. **This Week**: Scaffold src/ directory with base implementations
3. **Next Week**: Deploy local development stack
4. **Ongoing**: Iterate based on testing results

---

## References

- [workflow-comparison.md](./workflow-comparison.md) - Detailed workflow analysis
- [eliza-patterns.md](./eliza-patterns.md) - Agent pattern specifications
- [frontend-patterns.md](./frontend-patterns.md) - Component implementations
- `/examples/` - Source example code
- `/openspec/overview.md` - Project specifications
