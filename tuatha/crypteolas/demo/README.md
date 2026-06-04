# Crypteolas Demo

Standalone demonstration of the GitHub Intelligence + DeFi Analytics platform.
Crypteolas lives at `tuatha/crypteolas/` after the
[consolidation refactor](../../../../openspec/changes/consolidate-external-libs-into-tuatha/).
See [`../STATUS.md`](../STATUS.md) for the full refactor history.

## Quick Start

```bash
cd tuatha/crypteolas
python demo/run_demo.py
```

## What This Demo Demonstrates

### 1. GitHub Intelligence
- Repository search by topic, language, stars
- Trending repos by language
- Commit history analysis
- Contributor patterns

### 2. DeFi Analytics
- Protocol TVL tracking (DeFiLlama)
- Pool yield comparisons
- Chain TVL breakdown
- Cross-protocol analytics
- Funding-rate analysis (Binance, Bybit, OKX)
- Subgraph data (Aave v3, Pendle)

### 3. Hybrid Search
- Vector search across GitHub + DeFi data
- Cross-domain correlation
- Semantic query understanding

### 4. Knowledge Graph
- Cognee static protocol knowledge graph (Memgraph)
- Graphiti temporal protocol graph (FalkorDB)
- Protocol development metrics
- GitHub stars vs TVL correlation
- Contributor expertise mapping

### 5. Research Agent
- Agno-based agent team (research, analysis, pipeline)
- CopilotKit integration
- Multi-step research workflows
- Automated report generation

## Requirements

This demo requires the FastAPI server running:

```bash
cd tuatha
uv run uvicorn crypteolas.api.main:app --port 8001 --reload
```

Then run the demo:

```bash
cd tuatha/crypteolas
python demo/run_demo.py
```

## Demo Structure

```
tuatha/crypteolas/demo/
├── __init__.py
├── run_demo.py       # Main demo script
└── README.md         # This file
```

## Running the Demo

The demo expects the API server at `http://localhost:8001`.

```bash
# Terminal 1: Start API server
cd tuatha
uv run uvicorn crypteolas.api.main:app --port 8001 --reload

# Terminal 2: Run demo
cd tuatha/crypteolas
python demo/run_demo.py
```

The demo will showcase:
- Health checks and API overview
- GitHub intelligence features
- DeFi analytics dashboards
- Hybrid search across domains
- Cross-domain analysis
- Agent capabilities
- Dagster pipeline overview

## Full Platform Setup

To run the complete platform:

```bash
# Install dependencies (from the tuath workspace root)
cd tuatha && uv sync

# Configure environment
cp .env.example .env
# Edit .env with your credentials
# (See ../docs/SETUP.md for the full secrets reference)

# Run API server
cd tuatha
uv run uvicorn crypteolas.api.main:app --port 8001 --reload

# Start the unified Dagster UI (loads all 3 code-locations)
cd tuatha
uv run dagster dev

# Or just the crypteolas code-location
cd tuatha
uv run dagster dev -m crypteolas.definitions

# Run tests
cd tuatha
uv run pytest crypteolas/tests/ -v
```

## API Endpoints

When the server is running:

**GitHub**
- `GET /github/repos/search` - Search repositories
- `GET /github/trending` - Trending repos
- `GET /github/repos/:owner/:name` - Repo details

**DeFi**
- `GET /defi/protocols` - List protocols
- `GET /defi/pools` - Yield opportunities
- `GET /defi/metrics/tvl` - TVL breakdown
- `GET /defi/funding-rates` - Funding rates (Binance, Bybit, OKX)

**Search**
- `POST /search/` - Hybrid search (LanceDB + Memgraph)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              CRYPTOEOLAS - DeFi Research Platform             │
└─────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ GitHub API  │      │ DeFiLlama   │      │ BGE-M3      │
│             │      │ API         │      │ Embeddings  │
│ • Repos     │      │ • Protocols │      │             │
│ • Commits   │      │ • TVL       │      │ • 1024 dim  │
│ • Issues    │      │ • Yields    │      │ • LanceDB   │
└─────────────┘      └─────────────┘      └─────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│ Knowledge   │      │ Hybrid      │      │ Agno Agent  │
│ Graph       │      │ Search      │      │ Team        │
│             │      │             │      │             │
│ • Cognee    │      │ • Vector    │      │ • Research  │
│ • Graphiti  │      │ • Graph     │      │ • Analysis  │
│ • Memgraph  │      │ • Memgraph  │      │ • Pipeline  │
│ • FalkorDB  │      │ • FalkorDB  │      │             │
└─────────────┘      └─────────────┘      └─────────────┘
```

## Data Sources

### GitHub
- **Search API**: Repository discovery
- **REST API**: Detailed repo data
- **GraphQL**: Commit history, contributors

### DeFiLlama
- **Protocols**: TVL, chains, categories
- **Pools**: Yield opportunities, risk scores
- **Metrics**: Historical data, rankings

### CoinGecko
- Token prices, market cap, 24h change

### Binance / Bybit / OKX
- Funding rates, open interest, long/short ratio

### Aave v3 / Pendle Subgraphs
- Reserves, user positions, markets, swaps

## Key Features

### Hybrid Search

Combines vector similarity with graph traversal:

```python
response = await client.post("/search/", json={
    "query": "lending protocols with active development",
    "mode": "hybrid",
    "limit": 5,
    "content_types": ["protocol", "repository"]
})
```

### Cross-Domain Analysis

Correlate GitHub activity with DeFi metrics:

| Protocol | TVL | Stars | Commits/30d | Contributors |
|----------|-----|-------|-------------|--------------|
| Aave | $10.5B | 3500 | 150 | 95 |
| Uniswap | $5.2B | 4200 | 200 | 120 |
| Compound | $2.8B | 1800 | 45 | 55 |

### Agent Capabilities

**Available Tools:**
- `search_protocol_docs` - Search protocol docs
- `get_protocol_tvl` - TVL data
- `compare_yields` - Yield comparison
- `get_funding_rates` - Live funding rates
- `query_knowledge_graph` - Cypher over the temporal graph
- `run_pipeline` - Trigger Dagster materialization

**Example Query:**
```
User: Find lending protocols with the most active GitHub development

Agent:
1. Calls search_protocol_docs(category="lending")
2. Calls get_repo_metrics for top results
3. Calls get_protocol_tvl to correlate
4. Renders comparison table
```

## Dagster Assets

The crypteolas code-location registers these assets in
`tuatha/crypteolas/dagster_assets/`:

| Asset | Description | Schedule |
|-------|-------------|----------|
| `github_api_assets` | GitHub issues, PRs, commits, workflows | hourly |
| `crawl_assets` | Documentation crawling (Firecrawl) | on demand |
| `files_assets` | Local file processing | on demand |
| `defi_assets` | CoinGecko, DeFiLlama, Binance, subgraphs | 15 min / hourly |
| `code_vector_index` | Code embeddings → LanceDB | on change |
| `docs_vector_index` | Doc embeddings → LanceDB | on change |
| `docs_graph_index` | Doc graph → Memgraph | on change |
| `cognee_knowledge_graph` | Static knowledge graph (Cognee) | on change |
| `graphiti_temporal_graph` | Temporal knowledge graph (Graphiti) | on change |

## Observability

Integrated observability stack:
- **Datadog APM**: API latency, error rates
- **Datadog LLMObs**: Agent token usage
- **MLflow**: Experiment tracking
- **Langfuse**: Cost tracking + LLM tracing
- **Prometheus**: Infrastructure metrics

## Related Projects

- **códeolas** (`tuatha/codeolas/`) - Code analysis (imports crypteolas for intelligence)
- **oideachas** (`oideachais/`) - Education curriculum processing
- **tuath** (`tuatha/`) - Celtic Educational MMO game

## Support

For issues or questions:
- Main README: [`../README.md`](../README.md)
- Tuath workspace README: [`../../README.md`](../../README.md)
- Tuath workspace DEVELOPMENT: [`../../DEVELOPMENT.md`](../../DEVELOPMENT.md)
- Crypteolas STATUS (refactor history): [`../STATUS.md`](../STATUS.md)
- Crypteolas QUICKSTART: [`../QUICKSTART.md`](../QUICKSTART.md)
- Crypteolas SETUP: [`../SETUP.md`](../SETUP.md)
- Crypteolas DEVELOPMENT: [`../DEVELOPMENT.md`](../DEVELOPMENT.md)
- Crypteolas ARCHITECTURE: [`../ARCHITECTURE.md`](../ARCHITECTURE.md)
- DeFiLlama: https://defillama.com
- GitHub API: https://docs.github.com/rest

## License

BUSL-1.1 (matching the parent tuath workspace; transitions to AGPL-3.0
after 4 years).
