# Crypteolas Demo

Standalone demonstration of the GitHub Intelligence + DeFi Analytics platform.

## Quick Start

```bash
cd sruth/crypteolas
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

### 3. Hybrid Search
- Vector search across GitHub + DeFi data
- Cross-domain correlation
- Semantic query understanding

### 4. Knowledge Graph
- Protocol development metrics
- GitHub stars vs TVL correlation
- Contributor expertise mapping

### 5. Research Agent
- CopilotKit integration
- Multi-step research workflows
- Automated report generation

## Requirements

This demo requires the FastAPI server running:

```bash
cd sruth/crypteolas
uv run uvicorn crypteolas.api.main:app --port 8001 --reload
```

Then run the demo:

```bash
python demo/run_demo.py
```

## Demo Structure

```
demo/
├── __init__.py
├── run_demo.py       # Main demo script
└── README.md         # This file
```

## Running the Demo

The demo expects the API server at `http://localhost:8001`.

```bash
# Terminal 1: Start API server
cd sruth/crypteolas
uv run uvicorn crypteolas.api.main:app --port 8001 --reload

# Terminal 2: Run demo
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
# Install dependencies
cd sruth/crypteolas
uv sync

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Run API server
uv run uvicorn crypteolas.api.main:app --port 8001 --reload

# Start Dagster (another terminal)
dagster dev -m crypteolas.dagster_assets

# Run tests
uv run pytest tests/ -v
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

**Search**
- `POST /search/` - Hybrid search

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
│ Knowledge   │      │ Hybrid      │      │ CopilotKit  │
│ Graph       │      │ Search      │      │ Agent       │
│             │      │             │      │             │
│ • Neo4j     │      │ • Vector    │      │ • Tools     │
│ • Relations │      │ • Graph     │      │ • Research  │
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
- `search_github` - Search repositories
- `get_repo_metrics` - Detailed repo stats
- `analyze_contributors` - Contributor patterns
- `get_protocol_tvl` - TVL data
- `compare_yields` - Yield comparison
- `correlate_dev_tvl` - Development vs TVL

**Example Query:**
```
User: Find lending protocols with the most active GitHub development

Agent:
1. Calls search_github(category="lending")
2. Calls get_repo_metrics for top results
3. Calls get_protocol_tvl to correlate
4. Renders comparison table
```

## Dagster Assets

| Asset | Description | Schedule |
|-------|-------------|----------|
| `github_repositories` | DeFi repos from GitHub API | hourly |
| `github_commits` | Commit history analysis | hourly |
| `defi_protocols` | Protocol TVL from DeFiLlama | 15 min |
| `defi_pools` | Pool yields from DeFiLlama | hourly |
| `embeddings` | BGE-M3 vectors for search | on change |
| `knowledge_graph` | Neo4j relationships | on change |

## Observability

Integrated observability stack:
- **Datadog APM**: API latency, error rates
- **Datadog LLMObs**: Agent token usage
- **MLflow**: Experiment tracking
- **Langfuse**: Cost tracking

## Related Projects

- **códeolas** - Code analysis (imports crypteolas for intelligence)
- **oideachas** - Education curriculum processing
- **tuath** - Celtic MMO game

## Support

For issues or questions:
- Main README: [sruth/crypteolas/README.md](../README.md)
- DeFiLlama: https://defillama.com
- GitHub API: https://docs.github.com/rest

## License

MIT
