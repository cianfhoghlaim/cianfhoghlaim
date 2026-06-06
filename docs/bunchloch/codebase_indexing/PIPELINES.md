# Crypteolas Data Pipelines

Data ingestion, transformation, and orchestration for GitHub Intelligence + DeFi Analytics.

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Sources                              │
├─────────────┬─────────────┬─────────────┬─────────────┬─────────┤
│   GitHub    │  DeFiLlama  │  CoinGecko  │   Binance   │  Docs   │
│    API      │    API      │    API      │    API      │ Crawl   │
└─────┬───────┴─────┬───────┴─────┬───────┴─────┬───────┴────┬────┘
      │             │             │             │            │
      └─────────────┴─────────────┴─────────────┴────────────┘
                              │
                    ┌─────────▼─────────┐
                    │   DLT Sources     │
                    │ (data load tool)  │
                    └─────────┬─────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
┌────────▼────────┐  ┌────────▼────────┐  ┌───────▼────────┐
│   DuckDB        │  │   CocoIndex     │  │   Graphiti     │
│ (Structured)    │  │  (Embeddings)   │  │ (Knowledge)    │
└────────┬────────┘  └────────┬────────┘  └────────┬───────┘
         │                    │                    │
         │           ┌────────▼────────┐           │
         │           │    LanceDB      │           │
         │           │ (Vector Store)  │           │
         │           └────────┬────────┘           │
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │      Dagster      │
                    │  (Orchestration)  │
                    └───────────────────┘
```

## DLT Sources

### GitHub Source

**Location:** `dlt_sources/github/`

#### Repository Data

**File:** `github_source.py`

Ingests DeFi repository data from GitHub:
- Repository metadata
- Commit history
- Contributor activity
- Issue and PR data

```python
@dlt.source
def github_repositories(repos: list[str]):
    """Load DeFi repository data."""
    yield dlt.resource(
        fetch_repositories(repos),
        name="repositories",
        write_disposition="merge",
        primary_key="full_name",
    )
    yield dlt.resource(
        fetch_commits(repos),
        name="commits",
        write_disposition="append",
        primary_key="sha",
    )
    yield dlt.resource(
        fetch_contributors(repos),
        name="contributors",
        write_disposition="merge",
        primary_key=["repo", "login"],
    )
```

#### Tracked Repositories

Default DeFi repositories:
- `uniswap/v4-core`
- `aave/aave-v3-core`
- `compound-finance/compound-protocol`
- `MakerDAO/dss`
- `curvefi/curve-contract`

### DeFi Sources

**Location:** `dlt_sources/defi/`

#### DeFiLlama

**File:** `defillama.py`

Protocol TVL and yield data:

```python
@dlt.source
def defillama_protocols():
    """Load protocol TVL data from DeFiLlama."""
    yield dlt.resource(
        fetch_protocols(),
        name="protocols",
        write_disposition="merge",
        primary_key="slug",
    )
    yield dlt.resource(
        fetch_tvl_history(),
        name="tvl_history",
        write_disposition="append",
        primary_key=["protocol", "timestamp"],
    )
    yield dlt.resource(
        fetch_yields(),
        name="yields",
        write_disposition="replace",
    )
```

#### CoinGecko

**File:** `coingecko.py`

Price and market data:

```python
@dlt.source
def coingecko_prices(tokens: list[str]):
    """Load token price data from CoinGecko."""
    yield dlt.resource(
        fetch_prices(tokens),
        name="prices",
        write_disposition="append",
        primary_key=["token", "timestamp"],
    )
    yield dlt.resource(
        fetch_market_data(tokens),
        name="market_data",
        write_disposition="merge",
        primary_key="id",
    )
```

#### Binance

**File:** `binance.py`

Derivatives and funding data:

```python
@dlt.source
def binance_derivatives(symbols: list[str]):
    """Load derivatives data from Binance."""
    yield dlt.resource(
        fetch_funding_rates(symbols),
        name="funding_rates",
        write_disposition="append",
        primary_key=["symbol", "timestamp"],
    )
    yield dlt.resource(
        fetch_open_interest(symbols),
        name="open_interest",
        write_disposition="append",
        primary_key=["symbol", "timestamp"],
    )
```

### Documentation Source

**Location:** `dlt_sources/documentation/`

#### Protocol Docs

**File:** `protocol_docs.py`

Crawls protocol documentation:

```python
@dlt.source
def protocol_documentation(protocols: list[str]):
    """Crawl and load protocol documentation."""
    yield dlt.resource(
        crawl_docs(protocols),
        name="documentation",
        write_disposition="replace",
    )
    yield dlt.resource(
        fetch_whitepapers(protocols),
        name="whitepapers",
        write_disposition="merge",
        primary_key="protocol",
    )
```

### Running DLT Pipelines

```bash
# Run single source
uv run python -m crypteolas.dlt_sources.github.github_source

# Run DeFi sources
uv run python -m crypteolas.dlt_sources.defi.defillama

# Run with custom destination
dlt run crypteolas.dlt_sources.defi.defillama --destination duckdb
```

## CocoIndex Embedding Flows

### Code Embedding

**File:** `cocoindex_flows/code_embedding.py`

Creates embeddings for code with Tree-sitter parsing:

```python
@cocoindex.flow
class CodeEmbeddingFlow:
    """Embed code with AST-aware chunking."""

    def source(self) -> Iterator[Document]:
        yield from load_code_files()

    def transform(self, doc: Document) -> list[Chunk]:
        # Parse with Tree-sitter
        tree = parse_code(doc.content, doc.language)
        # Chunk by function/class boundaries
        return chunk_by_ast(tree, max_tokens=512)

    def embed(self, chunks: list[Chunk]) -> list[Embedding]:
        return embed_with_bge_m3(chunks, batch_size=100)

    def sink(self, embeddings: list[Embedding]):
        store_to_lancedb(embeddings, table="code")
```

### Document Embedding

**File:** `cocoindex_flows/document_embedding.py`

Embeds protocol documentation:

```python
@cocoindex.flow
class DocumentEmbeddingFlow:
    """Embed documentation with semantic chunking."""

    def transform(self, doc: Document) -> list[Chunk]:
        # Semantic chunking with overlap
        chunks = semantic_chunk(
            doc,
            chunk_size=1000,
            overlap=200,
        )
        # Extract metadata
        for chunk in chunks:
            chunk.metadata["section"] = extract_section(chunk)
            chunk.metadata["protocol"] = doc.protocol
        return chunks
```

### Code Chunking Transform

**File:** `cocoindex_flows/transforms/code_chunking.py`

Smart code chunking using Tree-sitter:

```python
def chunk_by_ast(tree: Tree, max_tokens: int = 512) -> list[Chunk]:
    """Chunk code by AST node boundaries."""
    chunks = []
    for node in tree.root_node.children:
        if node.type in ['function_definition', 'class_definition', 'contract_declaration']:
            chunk = Chunk(
                content=node.text,
                metadata={
                    'node_type': node.type,
                    'name': extract_name(node),
                    'start_line': node.start_point[0],
                    'end_line': node.end_point[0],
                }
            )
            chunks.append(chunk)
    return chunks
```

### Running CocoIndex

```bash
# Build code embeddings
uv run cocoindex build code_embedding

# Build documentation embeddings
uv run cocoindex build document_embedding --force

# Query embeddings
uv run cocoindex query "flash loan callback" --flow code_embedding
```

## Dagster Orchestration

### Assets

**Location:** `dagster_assets/`

#### GitHub Assets

**File:** `github_assets.py`

```python
@asset(
    group_name="github",
    partitions_def=DailyPartitionsDefinition(start_date="2024-01-01"),
)
def github_repositories(context) -> pd.DataFrame:
    """Ingest DeFi repository metadata."""
    repos = get_tracked_repos()
    return load_repositories(repos)


@asset(deps=[github_repositories])
def github_commits(context, github_repositories) -> pd.DataFrame:
    """Load commit history for tracked repos."""
    repos = github_repositories["full_name"].tolist()
    return load_commits(repos, since=context.partition_key)


@asset(deps=[github_repositories])
def github_contributors(context, github_repositories) -> pd.DataFrame:
    """Load contributor activity."""
    repos = github_repositories["full_name"].tolist()
    return load_contributors(repos)
```

#### DeFi Assets

**File:** `defi_assets.py`

```python
@asset(
    group_name="defi",
    freshness_policy=FreshnessPolicy(maximum_lag_minutes=15),
)
def defi_protocols() -> pd.DataFrame:
    """Load protocol data from DeFiLlama."""
    return load_defillama_protocols()


@asset(deps=[defi_protocols])
def defi_pools(context, defi_protocols) -> pd.DataFrame:
    """Load yield opportunity data."""
    return load_defillama_yields()


@asset(
    group_name="defi",
    freshness_policy=FreshnessPolicy(maximum_lag_minutes=5),
)
def defi_prices() -> pd.DataFrame:
    """Load token prices from CoinGecko."""
    tokens = get_tracked_tokens()
    return load_coingecko_prices(tokens)


@asset(
    group_name="defi",
    freshness_policy=FreshnessPolicy(maximum_lag_minutes=1),
)
def funding_rates() -> pd.DataFrame:
    """Load funding rates from Binance."""
    symbols = ["BTC", "ETH", "SOL", "ARB", "OP"]
    return load_binance_funding(symbols)
```

#### Embedding Assets

**File:** `embedding_assets.py`

```python
@asset(
    deps=[github_repositories],
    group_name="embeddings",
)
def repository_embeddings(context, github_repositories) -> None:
    """Generate embeddings for repository code."""
    flow = CodeEmbeddingFlow()
    for repo in github_repositories.itertuples():
        code_files = fetch_code_files(repo.full_name)
        flow.run(code_files)


@asset(
    group_name="embeddings",
)
def protocol_embeddings(context) -> None:
    """Generate embeddings for protocol documentation."""
    flow = DocumentEmbeddingFlow()
    docs = fetch_protocol_docs()
    flow.run(docs)
```

### Schedules

**File:** `schedules.py`

```python
# Hourly GitHub refresh
github_schedule = ScheduleDefinition(
    job=define_asset_job("github_job", selection=["github_*"]),
    cron_schedule="0 * * * *",  # Every hour
)

# 15-minute DeFi metrics
defi_schedule = ScheduleDefinition(
    job=define_asset_job("defi_job", selection=["defi_protocols", "defi_pools"]),
    cron_schedule="*/15 * * * *",  # Every 15 minutes
)

# 1-minute price updates
price_schedule = ScheduleDefinition(
    job=define_asset_job("price_job", selection=["defi_prices", "funding_rates"]),
    cron_schedule="* * * * *",  # Every minute
)

# Daily embedding rebuild
embedding_schedule = ScheduleDefinition(
    job=define_asset_job("embedding_job", selection=["repository_embeddings", "protocol_embeddings"]),
    cron_schedule="0 3 * * *",  # 3 AM daily
)
```

### Repository Definition

**File:** `definitions.py`

```python
from dagster import Definitions

defs = Definitions(
    assets=[
        github_repositories,
        github_commits,
        github_contributors,
        defi_protocols,
        defi_pools,
        defi_prices,
        funding_rates,
        repository_embeddings,
        protocol_embeddings,
    ],
    schedules=[
        github_schedule,
        defi_schedule,
        price_schedule,
        embedding_schedule,
    ],
    resources={
        "duckdb": DuckDBResource(database="./data/crypteolas.duckdb"),
        "lancedb": LanceDBResource(uri="./data/lancedb"),
        "graphiti": GraphitiResource(neo4j_uri=os.getenv("NEO4J_URI")),
        "redis": RedisResource(url=os.getenv("REDIS_URL")),
    },
)
```

### Running Dagster

```bash
# Start Dagster UI
dagster dev -m crypteolas.dagster_assets

# Materialize GitHub assets
dagster asset materialize -m crypteolas.dagster_assets --select 'github_*'

# Materialize DeFi assets
dagster asset materialize -m crypteolas.dagster_assets --select 'defi_*'

# Run scheduled job manually
dagster job execute -m crypteolas.dagster_assets -j github_job
```

### Asset Graph

```
github_repositories ──┬──► github_commits
                      ├──► github_contributors
                      └──► repository_embeddings ──┐
                                                   │
defi_protocols ───────┬──► defi_pools              ├──► search_index
                      └──► protocol_knowledge      │
                                                   │
protocol_docs ────────────► protocol_embeddings ───┘
```

## Caching Strategy

### Redis Caching

API responses cached in Redis:

```python
from crypteolas.cache import cache

@cache(ttl=3600)
async def get_repository(owner: str, repo: str):
    """Cached GitHub repository fetch."""
    return await github.get_repo(f"{owner}/{repo}")
```

Cache TTLs:
| Data Type | TTL |
|-----------|-----|
| Repository metadata | 1 hour |
| Commit history | 15 minutes |
| Protocol TVL | 5 minutes |
| Token prices | 1 minute |
| Funding rates | 30 seconds |

### LanceDB Caching

Embeddings cached in LanceDB with metadata:

```python
# Check cache before embedding
existing = lancedb.search(
    table="code",
    filter=f"file_hash = '{file_hash}'",
)
if existing:
    return existing
```

## Knowledge Graph

### Graphiti (Temporal)

Tracks protocol evolution:

```python
from crypteolas.knowledge_graph.graphiti import temporal_graph

# Add temporal fact
temporal_graph.add_episode(
    name="Uniswap v4 launch",
    content="Uniswap v4 introduces hooks...",
    reference_time=datetime(2024, 6, 15),
)

# Query temporal relationships
results = temporal_graph.search(
    "Uniswap governance changes",
    time_range=("2024-01-01", "2025-01-01"),
)
```

### Cognee (Static)

Static protocol relationships:

```python
from crypteolas.knowledge_graph.cognee import static_knowledge

# Build knowledge graph
static_knowledge.cognify([protocol_docs])

# Query relationships
results = static_knowledge.search("Aave liquidation mechanism")
```

## Monitoring

### Dagster UI

Access at http://localhost:3000 during development.

### Metrics

Pipeline metrics exposed at `/metrics`:
- `crypteolas_github_repos_processed`
- `crypteolas_defillama_protocols_loaded`
- `crypteolas_embedding_batch_duration_seconds`
- `crypteolas_cache_hit_ratio`

### Alerts

Configure alerts for:
- GitHub rate limit approaching
- DeFiLlama API failures
- Embedding pipeline delays
- Stale data (freshness policy violations)

## Best Practices

### Rate Limiting

Respect API limits:
```python
# GitHub: 5000/hour authenticated
# DeFiLlama: No official limit (be respectful)
# CoinGecko: 50/minute free, 500/minute pro
# Binance: 1200/minute
```

### Error Handling

Retry with exponential backoff:
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
)
def fetch_with_retry(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()
```

### Data Validation

Validate incoming data:
```python
from pydantic import BaseModel

class Protocol(BaseModel):
    slug: str
    name: str
    tvl: float
    chains: list[str]

# Validates on load
protocols = [Protocol(**p) for p in raw_data]
```
