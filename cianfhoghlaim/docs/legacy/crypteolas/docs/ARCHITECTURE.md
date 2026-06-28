# Crypteolas - Current State & Architecture Summary

## Overview
Crypteolas is a production-grade cryptocurrency analytics SaaS platform built for the Cronos x402 Paytech Hackathon. It implements a hybrid payment model combining free tier + pay-per-call monetization using the HTTP 402 standard, with settlement on Cronos blockchain.

**Key Status**: Foundation in place with significant infrastructure, core data pipelines partially implemented, frontend scaffolding complete.

---

## 1. Directory Structure Overview

```
crypteolas/
├── config/                    # Configuration files (YAML-based)
├── pipelines/                 # DLT Data Pipelines
│   ├── sources/               # API source modules (CoinGecko, DeFiLlama, Binance, Subgraphs)
│   ├── scrapers/              # Firecrawl documentation scraping
│   ├── indexers/              # CocoIndex semantic chunking + LanceDB
│   ├── knowledge/             # Cognee graph schema & pipeline
│   ├── transformations/       # Ibis analytics functions
│   ├── shared/                # Config loaders, utilities
│   └── scheduler.py           # APScheduler orchestration
├── orchestration/             # Dagster asset definitions
│   ├── assets.py              # DLT-integrated asset definitions
│   └── definitions.py         # Jobs, schedules, sensors
├── workflows/                 # Restate durable workflows
│   └── services.py            # Virtual Objects for pipeline coordination
├── agents/                    # Agno agents
│   ├── crypto_agents.py       # Research, Analysis, Coordinator agents
│   └── mcp_tools.py           # MCP server exposing agent tools
├── demo/                      # TanStack Start frontend
│   ├── src/
│   │   ├── routes/            # File-based routing (TanStack Start)
│   │   ├── components/        # React UI components
│   │   ├── lib/               # Utility libraries (x402, auth, web3)
│   │   └── stores/            # Zustand state management
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
├── notebooks/                 # Marimo interactive dashboards
├── compose.yaml               # Compose setup (legacy)
├── docker-compose.yaml        # Full stack orchestration
├── workspace.yaml             # Dagster workspace config
├── pyproject.toml             # Python dependencies
└── README.md                  # Comprehensive documentation
```

---

## 2. Frontend (Demo) - TanStack Start

### Package.json Dependencies
```json
{
  "dependencies": {
    "@copilotkit/react-core": "^1.8.0",          // AI chat interface
    "@copilotkit/react-ui": "^1.8.0",
    "@x402/core": "^2.0.0",                       // x402 payment library
    "@x402/evm": "^2.0.0",                        // EVM integration
    "@x402/fetch": "^2.0.0",                      // Fetch wrapper
    "better-auth": "^1.0.0",                      // Auth framework
    "siwe": "^2.3.2",                             // Sign In With Ethereum
    "@tanstack/react-router": "^1.79.0",          // Routing
    "@tanstack/react-start": "^1.79.0",           // Full-stack framework
    "@tanstack/react-query": "^5.60.0",           // Data fetching
    "viem": "^2.21.0",                            // Ethereum client
    "wagmi": "^2.12.0",                           // React hooks for viem
    "zustand": "^5.0.0",                          // State management
    "recharts": "^2.13.0",                        // Data visualization
    "tailwindcss": "^3.4.14"                      // Styling
  }
}
```

### Project Structure

#### Routes (`src/routes/`)
- **`__root.tsx`** - Root layout with providers:
  - QueryClient provider
  - WagmiProvider (Web3)
  - X402Provider (payment infrastructure)
  - CopilotKit wrapper
  - Header, Sidebar, Navigation
  
- **`index.tsx`** - Dashboard:
  - Key metrics display (ETH price, sUSDe APY, TVL, peg)
  - Price charts (Recharts)
  - Protocol cards (Ethena, Aave, Pendle)
  - Event feed
  
- **`chat.tsx`** - AI assistant interface (stub, needs implementation)
- **`portfolio.tsx`** - Portfolio tracking (stub)
- **`analytics.tsx`** - Analytics dashboard (stub)
- **`knowledge.tsx`** - Knowledge graph explorer (stub)

#### API Routes (`src/routes/api/`)
- **`auth.$.ts`** - BetterAuth + SIWE authentication
- **`copilot.ts`** - CopilotKit backend for AI chat
- **`tokens.ts`** - Token price data (free tier)
- **`protocols.ts`** - Protocol metrics (free tier)
- **`graph.ts`** - Knowledge graph queries
- **`analytics/yield.ts`** - Yield analysis (paid feature)
- **`analytics/risk.ts`** - Risk modeling (paid feature)
- **`mcp.ts`** - MCP server integration (stub)

#### Components (`src/components/`)
**Wallet & Auth**
- `wallet/WalletConnect.tsx` - Wallet connection UI
- `wallet/SiweAuth.tsx` - SIWE authentication flow

**Payments**
- `payment/PaymentModal.tsx` - x402 payment UI (trigger when 402 response)
- `payment/UsageDashboard.tsx` - Free tier usage tracking display

**Data Visualization**
- `charts/PriceChart.tsx` - Recharts wrapper
- `graph/KnowledgeGraph.tsx` - Force-graph visualization
- `ui/ProtocolCard.tsx` - Protocol summary cards
- `ui/MetricCard.tsx` - Metric display cards

**Chat**
- `chat/ChatSidebar.tsx` - Chat history/sessions

#### Libraries (`src/lib/`)

**x402 Payment Integration** (`x402/`)
- `index.ts` - Main exports
- `networks.ts` - Cronos + Base testnet configurations
- `pricing.ts` - Feature pricing model (free limits + per-call costs)
- `middleware.ts` - Server-side payment verification
- `provider.tsx` - React context for payment state & signing

**Authentication** (`auth/`)
- `client.ts` - Client-side BetterAuth integration
- `server.ts` - BetterAuth server config with SIWE plugin
  - Nonce generation & verification
  - SIWE message validation
  - ENS lookups (optional)

**Web3** 
- `web3.ts` - Wagmi config with multi-chain support:
  - Cronos (25), Cronos Testnet (338)
  - Ethereum, Polygon, Arbitrum, Base, Base Sepolia
  - Token addresses for USDe, sUSDe, USDC, WETH, WCRO

**MCP Integration** (`mcp/`)
- `crypto-com.ts` - Crypto.com MCP client
- `copilot-actions.ts` - CopilotKit action definitions

**API Client** (`api.ts`)
- Typed fetch wrapper for API endpoints
- x402 header handling

#### State Management (`src/stores/`)

**Usage Store** (`usage.ts`)
```typescript
{
  walletAddress: string | null,
  dailyUsage: { [featureId]: count },
  usageDate: string (YYYY-MM-DD UTC),
  payments: PaymentRecord[],
  totalSpent: bigint,
  
  // Methods
  setWallet(address)
  incrementUsage(featureId)
  recordPayment(payment)
  getUsageCount(featureId)
  getRemainingFree(featureId)
  needsPayment(featureId)
  resetIfNewDay()
  clearUsage()
}
```
- Persists to localStorage (keyed by wallet)
- Auto-resets at UTC midnight
- Tracks free tier usage + payment history

**Portfolio Store** (`portfolio.ts` - stub)
**Chat Store** (`chat.ts` - stub)
**Graph Store** (`graph.ts` - stub)

### Build & Development

**Build Tool**: Vinxi (TanStack Start meta-framework over Vite)
```bash
npm/bun install
npm/bun run dev    # Dev server on :3000
npm/bun run build  # Production build
npm/bun run start  # Start production server
```

**Environment Variables**
```
PAYMENT_RECIPIENT=0xWalletAddress
FACILITATOR_URL=https://x402.org/facilitator
LITELLM_BASE_URL=http://localhost:4000
```

---

## 3. Backend - Python Data Pipelines

### Python Dependencies (pyproject.toml)

**Data Loading**
- `dlt[duckdb,filesystem]>=1.0.0` - Schema-aware ETL framework
- `httpx>=0.27.0` - HTTP client for API calls

**Analytics**
- `ibis-framework[duckdb]>=9.0.0` - SQL-based analytics
- `polars>=1.0.0` - DataFrame operations
- `pandas>=2.0.0` - Legacy support

**Vector Storage & Search**
- `lancedb>=0.15.0` - Vector database
- `sentence-transformers>=3.0.0` - Embeddings

**Knowledge Graph**
- `cognee>=0.1.0` - Knowledge extraction & graph building
- `neo4j>=5.0.0` - Graph database client
- `falkordb>=1.0.0` - Temporal graph (Redis protocol)

**Document Processing**
- `cocoindex>=0.1.0` - Semantic chunking
- `firecrawl-py>=1.0.0` - Web scraping
- `langchain-text-splitters>=0.3.0` - Text splitting

**Orchestration**
- `dagster>=1.8.0` - Asset-based orchestration
- `dagster-dlt>=0.24.0` - DLT integration
- `apscheduler>=3.10.0` - Scheduled jobs

**Durable Workflows**
- `restate-sdk>=0.5.0` - Virtual Objects + Services

**Notebooks & Visualization**
- `marimo>=0.10.0` - Interactive notebooks
- `altair>=5.0.0` - Declarative visualization

**Agents**
- `agno>=0.1.0` - Agent framework
- `mcp>=1.0.0` - MCP protocol

**Utilities**
- `pyyaml>=6.0` - Config parsing
- `python-dotenv>=1.0.0` - Environment variables
- `typer>=0.12.0` - CLI
- `rich>=13.0.0` - Terminal formatting

### Data Pipeline Architecture

#### DLT Sources (`pipelines/sources/`)

**CoinGecko** (`coingecko.py`)
```python
def coingecko_source(
    api_key: str,
    days_back: int = 30,
    tokens: Optional[list[str]] = None
) -> Iterator[dlt.resource]
```
- Resources: price_<token>, global_market
- Update frequency: Hourly
- Primary tokens: ethena-usde, ethena-staked-usde, ethereum, usd-coin

**DeFiLlama** (`defillama.py`)
- TVL by protocol
- Yield/APY data
- Stablecoin metrics
- Protocols: Ethena, Aave, Pendle, Lido
- Update frequency: 6 hours

**Binance** (`binance.py`)
- Funding rates
- Open Interest
- Long/Short ratios
- Update frequency: 8 hours

**Subgraphs** (`subgraphs.py`)
- Aave V3 (reserves, positions)
- Pendle (markets, swaps, implied APY)
- Update frequency: 4 hours

**Firecrawl Scraper** (`scrapers/firecrawl_source.py`)
```python
async def scrape_protocol_docs(
    protocol: str,
    base_url: str,
    max_depth: int = 3,
    max_pages: int = 100
) -> list[Document]
```
- Protocols: Ethena, Aave, Pendle, Lido, EigenLayer
- Returns: page content + metadata

#### Data Processing

**Indexers** (`pipelines/indexers/`)
- `cocoindex_flow.py`: 
  - Semantic chunking via CocoIndex
  - Embeddings via sentence-transformers
  - LanceDB vector storage
  - Methods: `query_crypto_knowledge()`, `get_protocol_context()`

**Knowledge Graph** (`pipelines/knowledge/`)
- `graph_schema.py`:
  - Entity types: PROTOCOL, TOKEN, YIELD_STRATEGY, RISK_FACTOR, CONCEPT
  - Relationship types: NATIVE_TOKEN_OF, YIELD_BEARING, HEDGES_WITH, HAS_RISK
  
- `cognee_pipeline.py`:
  - ECL (Entity-Concept-Link) extraction
  - Dual-graph architecture:
    - Memgraph: Static relationships
    - FalkorDB: Temporal/event data
  - Async query interface

**Analytics** (`pipelines/transformations/crypto_analytics.py`)
- Ibis-based SQL analytics
- DuckDB as default backend
- Functions: yield comparison, funding rate analysis, risk modeling

#### Orchestration

**Scheduler** (`pipelines/scheduler.py`)
- APScheduler-based job coordination
- Jobs:
  - Hourly: API source ingestion (CoinGecko, Binance)
  - 4h: Subgraph queries
  - 6h: DeFiLlama updates
  - Daily 2am: Full pipeline
  - Weekly (Sun 3am): Documentation scraping

**Dagster Assets** (`orchestration/assets.py`)
```python
# Asset groups (partitioned)
- coingecko_assets (hourly)
- defillama_assets (6h)
- binance_assets (8h)
- subgraph_assets (4h)
- firecrawl_assets (daily)
- cocoindex_assets (from documentation)
- cognee_assets (knowledge graph extraction)

# Analytics assets
- funding_rate_metrics
- yield_comparison_metrics
- risk_assessment_metrics
```

**Definitions** (`orchestration/definitions.py`)
- Job definitions with schedules
- Sensor definitions (for event-driven execution)

#### Configuration

**Config Files** (`config/`)

`sources.yaml` - API endpoints & credentials
```yaml
coingecko:
  base_url: https://api.coingecko.com/api/v3
  credentials: coingecko_api_key
  endpoints:
    - prices
    - global_market
    
defillama:
  base_url: https://api.llama.fi
  endpoints:
    - tvl
    - yields
```

`databases.yaml` - Connection strings
```yaml
duckdb:
  path: data/crypto_analytics.duckdb
  
lancedb:
  uri: data/crypto_vectors
  
memgraph:
  host: memgraph:7687
  
falkordb:
  host: falkordb:6379
```

---

## 4. Agents & MCP Integration

### Agno Agents (`agents/crypto_agents.py`)

**Agent Types**

1. **CryptoResearcher** (Knowledge-focused)
   - Tools:
     - `search_knowledge_base(query, protocol_filter, limit)`
     - `get_protocol_context(protocol)`
     - `query_knowledge_graph(query, search_type)`
   - Use case: Documentation queries, protocol analysis

2. **CryptoAnalyst** (Data-focused)
   - Tools:
     - `get_funding_rate_analysis(symbol, days)`
     - `compare_yields(protocols)`
     - `get_stablecoin_metrics()`
     - `query_graph(query)`
   - Use case: Data insights, strategy analysis

3. **PipelineManager** (Operations)
   - Tools:
     - `run_pipeline(pipeline_type, config)`
   - Use case: Trigger data refresh

### MCP Server (`agents/mcp_tools.py`)

Exposes agent tools via MCP protocol for Claude/other LLMs:
```python
tools = [
    "search_knowledge",       # Vector search documentation
    "get_funding_rates",      # Funding rate analysis
    "compare_yields",         # Protocol yield comparison
    "get_stablecoin_metrics", # Supply and peg metrics
    "query_graph",            # Knowledge graph queries
    "run_pipeline",           # Trigger data refresh
    "get_protocol_summary",   # Full protocol context
]
```

### Crypto.com MCP Integration

CopilotKit actions for real-time data:
```typescript
getCryptoPrice({ symbol: "BTC" })
compareCryptos({ symbol1: "ETH", symbol2: "SOL" })
getMarketOverview()
getTrendingCryptos()
```

---

## 5. Durable Workflows (Restate)

### Virtual Objects (`workflows/services.py`)

**CryptoPipelineService**
```python
@crypto_pipeline_service.handler()
async def start_pipeline(ctx: ObjectContext, tasks: list[dict]) -> str
async def execute_task(ctx: ObjectContext, task_id: str) -> dict
async def get_status(ctx: ObjectContext) -> dict
async def cancel_pipeline(ctx: ObjectContext) -> None
```

Features:
- Durable execution with automatic retries
- Exactly-once processing guarantees
- Awakeables for external event coordination
- Timers for scheduled operations

**PipelineTask Schema**
```python
task_id: str
task_type: str  # ingest, process, analyze, publish
source: str
config: dict
priority: int
status: str  # pending, running, completed, failed
```

---

## 6. x402 Payment Implementation

### Pricing Model (`demo/src/lib/x402/pricing.ts`)

```typescript
FEATURE_PRICING = {
  // Chat (5 free/day)
  chat_message: { price: "$0.01", freeLimit: 5 },
  
  // Knowledge (3 free/day)
  knowledge_search: { price: "$0.02", freeLimit: 3 },
  knowledge_entity: { price: "$0.03", freeLimit: 2 },
  
  // Analytics (no free access)
  analytics_protocol: { price: "$0.05", freeLimit: 0 },
  analytics_yield: { price: "$0.05", freeLimit: 0 },
  analytics_risk: { price: "$0.05", freeLimit: 0 },
  
  // Premium models
  model_finetuned: { price: "$0.10", freeLimit: 0 }
}
```

**Payment Flow**
1. User makes API request
2. Server checks daily usage quota
3. If quota exhausted → Return 402 Payment Required
   - Headers: price, network, USDC address, recipient
4. Client displays PaymentModal
5. User signs EIP-3009 authorization with same wallet as SIWE auth
6. Client retries request with PAYMENT-SIGNATURE header
7. Server verifies via x402 facilitator
8. Facilitator settles on Cronos blockchain
9. Server returns data + settlement confirmation

### Network Configuration

| Network | Chain ID | USDC Address | Status |
|---------|----------|--------------|--------|
| Cronos Testnet | 338 | `0x87EFB3ec...` | Primary |
| Cronos Mainnet | 25 | `0xc21223249C...` | Production |
| Base Sepolia | 84532 | `0x036CbD538...` | Fallback |
| Base Mainnet | 8453 | `0x833589fCD...` | Production |

### Middleware (`demo/src/lib/x402/middleware.ts`)

```typescript
export async function verifyPayment(
  signature: string,
  featureId: string,
  userAddress: string,
  network: string
): Promise<boolean>
```

- Validates EIP-3009 signatures
- Checks settlement on blockchain
- Records payment in usage store

---

## 7. Authentication (SIWE)

### BetterAuth Server Config (`demo/src/lib/auth/server.ts`)

**Features**
- SIWE (Sign In With Ethereum) via ERC-4361
- Anonymous authentication (no email required)
- Multi-chain support (Ethereum, Polygon, Arbitrum, Base, Cronos)
- ENS name/avatar lookups
- Nonce generation & verification
- In-memory nonce store (use Redis in production)

**Setup**
```typescript
const auth = betterAuth({
  database: { type: "memory" }, // Change to postgres/sqlite
  emailAndPassword: { enabled: false },
  plugins: [
    siwe({
      domain: process.env.APP_DOMAIN || "crypto.localhost",
      anonymous: true,
      getNonce: async () => generateRandomString(32),
      verifyMessage: async ({ message, signature, address }) => 
        verifyMessage({ address, message, signature }),
      ensLookup: async ({ walletAddress }) => ...
    })
  ]
})
```

### Client Integration (`demo/src/lib/auth/client.ts`)
- BetterAuth client initialization
- Hook utilities for auth state

---

## 8. Docker Orchestration

### Services (`docker-compose.yaml`)

| Service | Port | Role |
|---------|------|------|
| Dagster Webserver | 3000 | Asset orchestration UI |
| Dagster Daemon | - | Job scheduler |
| PostgreSQL | 5432 | Metadata store |
| Restate | 8080 | Workflow runtime |
| Restate Services | 9080 | Workflow service handlers |
| Marimo | 2718 | Interactive notebooks |
| MCP Server | 3001 | Agent tool server |

**Networks**
- Internal `crypto-net` for intra-service communication
- External `data-tools_default` for database access (shared with data infrastructure stack)

**Volumes**
- `crypto-data` - Shared data volume (DuckDB, LanceDB, embeddings)
- `dagster-home` - Dagster metadata
- `postgres-data` - PostgreSQL persistence
- `restate-data` - Restate workflow state

---

## 9. Current Implementation Status

### Completed
- ✅ Project structure & scaffolding
- ✅ TanStack Start frontend setup
- ✅ Wagmi + SIWE authentication
- ✅ BetterAuth server configuration
- ✅ x402 pricing model & payment infrastructure
- ✅ Usage tracking store (Zustand)
- ✅ DLT source definitions (CoinGecko, DeFiLlama, Binance, Subgraphs)
- ✅ Dagster asset definitions with DLT integration
- ✅ Knowledge graph schema (Cognee)
- ✅ Restate workflow service definitions
- ✅ Agno agent framework setup
- ✅ MCP server scaffold
- ✅ Docker Compose orchestration
- ✅ Dashboard layout & navigation
- ✅ Component scaffolding (charts, protocol cards, etc.)

### Partially Implemented
- ⚠️ API routes (stubbed, need backend integration)
- ⚠️ Payment modal UI (structure, needs handler logic)
- ⚠️ CopilotKit integration (declared, needs backend handler)
- ⚠️ Knowledge graph explorer (component exists, needs queries)
- ⚠️ Analytics endpoints (yield, risk - declared, not implemented)
- ⚠️ MCP tool implementations (client exists, server handlers stub)

### Not Yet Implemented
- ❌ Data pipeline execution (scheduler not hooked up)
- ❌ Dagster job definitions (only assets defined)
- ❌ Cognee ECL extraction (schema defined, extraction not implemented)
- ❌ Knowledge graph population (schema exists, no data loading)
- ❌ Agent tool implementations (tools declared, not wired to backends)
- ❌ Chat route implementation
- ❌ Portfolio tracking
- ❌ Analytics dashboard details
- ❌ Payment verification middleware (logic exists, not integrated)
- ❌ Restate workflow handlers (typed definitions exist, handlers stub)
- ❌ Marimo notebook (stub)
- ❌ Full integration testing

---

## 10. Key Configuration Files

### Environment Variables (`.env.example`)

**LLM Providers**
- OPENAI_API_KEY, ANTHROPIC_API_KEY, GROQ_API_KEY

**Databases**
- POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB
- FALKORDB_PASSWORD, MEMGRAPH_USER, MEMGRAPH_PASSWORD

**Cloud Storage (R2)**
- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_ENDPOINT_URL

**Data Sources**
- COINGECKO_API_KEY, DEFILLAMA_API_KEY, ETHERSCAN_API_KEY
- FIRECRAWL_API_KEY, CRAWL4AI_API_TOKEN

**Application Settings**
- DUCKDB_PATH, LANCEDB_URI, LOG_LEVEL, NODE_ENV
- RESTATE_HOST, RESTATE_ADMIN_PORT, RESTATE_INGRESS_PORT

### Dagster Workspace (`workspace.yaml`)
```yaml
load_from:
  - python_module: orchestration.definitions
```

---

## 11. Technology Stack Summary

| Layer | Technology | Status |
|-------|-----------|--------|
| Frontend Framework | TanStack Start + Vite | ✅ |
| Routing | TanStack Router | ✅ |
| State Management | Zustand | ✅ |
| Web3 | Wagmi + Viem | ✅ |
| Authentication | BetterAuth + SIWE | ✅ |
| Payments | @x402 (core, evm, fetch) | ✅ |
| AI Chat | CopilotKit | ✅ |
| UI Components | shadcn/ui + Radix | ✅ |
| Charts | Recharts | ✅ |
| Graph Viz | Force-Graph | ✅ |
| Data Loading | DLT | ✅ |
| Analytics | Ibis + DuckDB | ✅ |
| Vector Store | LanceDB | ✅ |
| Knowledge Graph | Cognee + Neo4j/FalkorDB | 🔄 |
| Orchestration | Dagster | ✅ |
| Workflows | Restate | ✅ |
| Notebooks | Marimo | 🔄 |
| Agents | Agno | ✅ |
| MCP | MCP Protocol | 🔄 |
| Web Scraping | Firecrawl | ✅ |
| Text Processing | CocoIndex | ✅ |
| Containerization | Docker Compose | ✅ |

---

## 12. What Needs to Be Added/Modified

### Critical Path

1. **Wire API Endpoints to Backend**
   - `/api/copilot` → Agent integration
   - `/api/analytics/yield` → DuckDB queries
   - `/api/analytics/risk` → Risk calculations
   - `/api/graph` → Knowledge graph queries

2. **Implement Payment Verification**
   - Integrate x402 facilitator client
   - Add signature verification middleware
   - Implement usage tracking in API layer

3. **Populate Knowledge Graph**
   - Complete Cognee ECL extraction pipeline
   - Load Firecrawl documents to Cognee
   - Implement graph schema population
   - Wire knowledge_search & query_graph tools

4. **Complete Agent Integration**
   - Implement agent tool handlers
   - Wire MCP server endpoints
   - Add CopilotKit backend handler
   - Test agent chains

5. **Implement Chat Features**
   - Chat message persistence
   - Session management
   - Real-time streaming support

6. **Data Pipeline Execution**
   - Complete scheduler implementation
   - Hook up Dagster daemon
   - Implement retry logic
   - Add monitoring/alerting

### Quality & Testing

- Unit tests for payment logic
- Integration tests for pipeline
- E2E tests for chat flow
- Load testing for payment processor
- Security audit of auth flow

### Deployment

- Kubernetes manifests (from Docker Compose)
- Environment configuration per stage
- CI/CD pipeline setup
- Monitoring & observability setup
- Secrets management (1Password, etc.)

---

## 13. Development Quick Start

### Frontend
```bash
cd demo
bun install
cp .env.example .env
bun run dev  # http://localhost:3000
```

### Backend
```bash
uv sync  # or pip install -e .
python -m pipelines.scheduler  # Start scheduler
dagster dev -w workspace.yaml  # http://localhost:3000
marimo run notebooks/ethena_dashboard.py  # http://localhost:2718
python -m agents.mcp_tools  # MCP server on 3001
```

### Full Stack
```bash
docker-compose up -d
# Dagster: http://localhost:3000
# Marimo: http://localhost:2718
# MCP: http://localhost:3001
```

---

## 14. Key Design Patterns

### Payment Flow (x402)
- Hybrid free tier + pay-per-call model
- Same wallet for auth (SIWE) and payment (EIP-3009)
- Daily quota resets at UTC midnight
- Client-side usage tracking persisted to localStorage
- Server-side verification via x402 facilitator

### Data Pipeline
- DLT sources → schema-aware ingestion
- DuckDB as analytical backbone
- LanceDB for vector search
- Cognee for knowledge extraction
- Dual-graph (Memgraph static + FalkorDB temporal)

### Orchestration
- Dagster for asset dependencies & scheduling
- APScheduler for cron-like jobs
- Restate for durability & exactly-once guarantees
- Event-driven via sensors

### Authentication
- SIWE for Web3-native auth (no passwords)
- BetterAuth for multi-chain support
- Anonymous mode (no email required)
- Optional ENS resolution

---

## 15. Next Steps Recommendation

1. **Start with data pipelines**
   - Verify DLT sources execute
   - Check DuckDB population
   - Validate asset definitions in Dagster UI

2. **Implement knowledge graph**
   - Test Cognee extraction on sample docs
   - Populate Memgraph with schema
   - Verify query interface

3. **Wire API endpoints**
   - Implement `/api/tokens` (free)
   - Implement `/api/protocols` (free)
   - Test with frontend

4. **Add payment layer**
   - Integrate x402 facilitator client
   - Implement 402 response in middleware
   - Test payment flow end-to-end

5. **Complete agent integration**
   - Test agents with backends
   - Wire CopilotKit handler
   - Implement chat route

6. **Polish & deploy**
   - E2E testing
   - Performance optimization
   - Security audit
   - Staging environment
   - Production deployment

