# Knowledge Graph Architecture for Crypto Analytics

## Overview

This document describes the dual-graph architecture for the crypto analytics platform, combining temporal agent memory (Graphiti + FalkorDB) with static protocol knowledge (Cognee + Memgraph).

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Crypto Analytics Platform                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        Application Layer                                 ││
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐                ││
│  │  │ Agents   │  │ Chat UI  │  │Analytics │  │ API      │                ││
│  │  │ (Agno)   │  │(Copilot) │  │(Marimo)  │  │(FastAPI) │                ││
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘                ││
│  └───────┼──────────────┼──────────────┼──────────────┼────────────────────┘│
│          │              │              │              │                      │
│          └──────────────┴──────────────┴──────────────┘                      │
│                                    │                                          │
│  ┌─────────────────────────────────┴─────────────────────────────────────┐  │
│  │                      Knowledge Layer (Unified Query API)               │  │
│  │                                                                        │  │
│  │   query_knowledge(                                                     │  │
│  │     query: str,                                                        │  │
│  │     mode: "temporal" | "semantic" | "hybrid"                          │  │
│  │   ) -> KnowledgeResult                                                 │  │
│  │                                                                        │  │
│  └─────────────────────────────────┬─────────────────────────────────────┘  │
│                                    │                                          │
│          ┌─────────────────────────┼─────────────────────────┐              │
│          │                         │                         │              │
│          ▼                         ▼                         ▼              │
│  ┌───────────────────┐   ┌───────────────────┐   ┌───────────────────┐    │
│  │  Temporal Memory  │   │  Static Knowledge │   │  Vector Search    │    │
│  │  (Graphiti)       │   │  (Cognee)         │   │  (LanceDB)        │    │
│  │                   │   │                   │   │                   │    │
│  │  • Agent sessions │   │  • Protocol docs  │   │  • Embeddings     │    │
│  │  • Market events  │   │  • Entity graphs  │   │  • Similarity     │    │
│  │  • Conversations  │   │  • Risk factors   │   │  • Hybrid search  │    │
│  │                   │   │                   │   │                   │    │
│  │  [FalkorDB:6379]  │   │  [Memgraph:7687]  │   │  [LanceDB:8080]   │    │
│  └───────────────────┘   └───────────────────┘   └───────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Graph Engine Selection

### FalkorDB + Graphiti (Temporal/Dynamic)

**Use Cases:**
- Agent memory and session context
- Real-time market events
- Conversation history with temporal ordering
- Price/TVL history with bi-temporal tracking

**Key Features:**
- Redis-compatible protocol (port 6379)
- Bi-temporal design (valid time + transaction time)
- Episode-based memory addition
- Fast retrieval for agent reasoning

**Configuration:**
```python
from graphiti_core import Graphiti
from graphiti_core.llm_client import LiteLLMClient

graphiti = Graphiti(
    uri="bolt://localhost:6379",
    database="crypto_memory",
    llm_client=LiteLLMClient(
        base_url="http://localhost:4000",  # LiteLLM gateway
        model="gpt-4o-mini"
    )
)
```

### Memgraph + Cognee (Static/Analytical)

**Use Cases:**
- Protocol documentation and whitepapers
- Entity relationships (Token ↔ Protocol ↔ Exchange)
- Risk factor tracking from audits
- Graph algorithms (PageRank, community detection)

**Key Features:**
- Bolt protocol (port 7687)
- MAGE library for graph algorithms
- HTAP support (transactional + analytical)
- Built-in vector search (v3.0+)

**Configuration:**
```python
import cognee

cognee.config.set_graph_database(
    type="memgraph",
    host="localhost",
    port=7687
)
cognee.config.set_vector_database(
    type="lancedb",
    path="./data/vectors"
)
```

### LanceDB (Vector Store)

**Use Cases:**
- Document embeddings for semantic search
- Hybrid search (keyword + semantic)
- Fast similarity queries
- Integration with Cognee

**Key Features:**
- Native DuckDB integration
- IVF-PQ indexing for scale
- Zero-copy Arrow format
- Local-first (no server required)

## Entity Schema

### Node Types

| Entity | Properties | Temporal | Backend |
|--------|------------|----------|---------|
| Token | symbol, name, contract_address, decimals, total_supply | Yes (price, volume) | Both |
| Protocol | name, category, tvl, chains | Yes (TVL) | Memgraph |
| Exchange | name, type, volume | Yes (volume) | Memgraph |
| LiquidityPool | address, tokens, fee_tier, apy | Yes (TVL, APY) | Memgraph |
| Document | title, doc_type, url, published_date | No | Memgraph |
| Risk | category, severity, title, mitigation | No | Memgraph |
| MarketEvent | event_type, title, impact | Yes | FalkorDB |
| AgentSession | session_id, user_id, started_at | Yes | FalkorDB |

### Relationship Types

```cypher
// Token relationships
(Token)-[:DEPLOYED_ON]->(Blockchain)
(Token)-[:TRADES_ON]->(Exchange)
(Token)-[:GOVERNANCE_FOR]->(Protocol)
(Token)-[:WRAPPED_AS]->(Token)
(Token)-[:IN_POOL]->(LiquidityPool)

// Protocol relationships
(Protocol)-[:INTEGRATES]->(Protocol)
(Protocol)-[:AUDITED_BY]->(Document)

// Document relationships
(Document)-[:DESCRIBES]->(Protocol)
(Document)-[:IDENTIFIES_RISK]->(Risk)

// Event relationships (temporal)
(MarketEvent)-[:AFFECTS]->(Protocol)
(MarketEvent)-[:PRECEDES]->(MarketEvent)

// Agent memory (temporal)
(AgentSession)-[:CONTAINS]->(Message)
(Message)-[:REFERENCES]->(Token|Protocol|Document)
```

## Data Flow

### Ingestion Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Data Ingestion Pipeline                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  REST APIs          dlt Pipeline           DuckDB                   │
│  ┌──────────┐      ┌──────────┐          ┌──────────┐              │
│  │CoinGecko │──────│          │──────────│ crypto_  │              │
│  │DeFiLlama │      │  dlt     │          │ raw.*    │              │
│  │Binance   │      │          │          │          │              │
│  └──────────┘      └──────────┘          └────┬─────┘              │
│                                               │                      │
│  GraphQL             Subgraph                 │                      │
│  ┌──────────┐      ┌──────────┐              │                      │
│  │Aave v3   │──────│  dlt     │──────────────┤                      │
│  │Pendle    │      │          │              │                      │
│  └──────────┘      └──────────┘              │                      │
│                                               │                      │
│                                               ▼                      │
│  Documents          Crawl4AI + BAML      Cognee ECL                │
│  ┌──────────┐      ┌──────────┐          ┌──────────┐              │
│  │Whitepapers│─────│ Extract  │──────────│ Cognify  │              │
│  │Audits    │      │ + Parse  │          │          │              │
│  │Research  │      │          │          │ [Memgraph│              │
│  └──────────┘      └──────────┘          │ +LanceDB]│              │
│                                          └──────────┘              │
│                                                                      │
│  Events              Graphiti               FalkorDB               │
│  ┌──────────┐      ┌──────────┐          ┌──────────┐              │
│  │Market    │──────│ add_     │──────────│ Temporal │              │
│  │News      │      │ episode  │          │ Memory   │              │
│  └──────────┘      └──────────┘          └──────────┘              │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Query Flow

```python
from typing import Literal
from dataclasses import dataclass

@dataclass
class KnowledgeResult:
    entities: list[dict]
    relationships: list[dict]
    documents: list[dict]
    temporal_context: list[dict]
    confidence: float

async def query_knowledge(
    query: str,
    mode: Literal["temporal", "semantic", "hybrid"] = "hybrid",
    entity_types: list[str] | None = None,
    time_range: tuple[datetime, datetime] | None = None
) -> KnowledgeResult:
    """Unified knowledge query across all graph backends"""

    results = KnowledgeResult(
        entities=[],
        relationships=[],
        documents=[],
        temporal_context=[],
        confidence=0.0
    )

    if mode in ["temporal", "hybrid"]:
        # Query Graphiti for temporal context
        temporal = await graphiti.search(
            query=query,
            num_results=20
        )
        results.temporal_context = temporal

    if mode in ["semantic", "hybrid"]:
        # Query Cognee for semantic search + graph completion
        cognee_results = await cognee.search(
            query_text=query,
            query_type="GRAPH_COMPLETION"
        )
        results.entities = cognee_results.entities
        results.relationships = cognee_results.relationships
        results.documents = cognee_results.documents

    # Calculate confidence based on result quality
    results.confidence = calculate_confidence(results)

    return results
```

## Agent Integration

### Agno Agent with Knowledge Access

```python
from agno import Agent
from agno.tools import tool

class CryptoAnalystAgent(Agent):
    """Crypto analyst agent with knowledge graph access"""

    def __init__(self):
        super().__init__(
            name="CryptoAnalyst",
            instructions="""
            You are a DeFi analyst with access to:
            - Real-time market data
            - Protocol documentation
            - Risk analysis from audits
            - Historical market events

            Use the knowledge tools to provide accurate analysis.
            """
        )

    @tool
    async def search_protocol_knowledge(
        self,
        query: str,
        protocol: str | None = None
    ) -> str:
        """Search protocol documentation and knowledge graph"""
        results = await query_knowledge(
            query=query,
            mode="semantic"
        )
        return format_knowledge_results(results)

    @tool
    async def get_market_context(
        self,
        query: str,
        days_back: int = 7
    ) -> str:
        """Get temporal market context and events"""
        time_range = (
            datetime.now() - timedelta(days=days_back),
            datetime.now()
        )
        results = await query_knowledge(
            query=query,
            mode="temporal",
            time_range=time_range
        )
        return format_temporal_results(results)

    @tool
    async def analyze_risk(
        self,
        protocol: str
    ) -> str:
        """Analyze risk factors for a protocol"""
        # Query audit documents and risk entities
        cypher_query = """
        MATCH (p:Protocol {name: $protocol})
        OPTIONAL MATCH (p)<-[:DESCRIBES]-(d:Document {doc_type: 'audit'})
        OPTIONAL MATCH (d)-[:IDENTIFIES_RISK]->(r:Risk)
        RETURN p, collect(DISTINCT d) as audits, collect(r) as risks
        """
        results = await memgraph_query(cypher_query, {"protocol": protocol})
        return format_risk_analysis(results)
```

## Infrastructure Requirements

### Docker Compose Services

```yaml
# From infrastructure/compose/data-tools/compose.yaml
services:
  memgraph:
    image: memgraph/memgraph-mage:latest
    ports:
      - "7687:7687"
      - "3001:3000"  # Lab UI
    volumes:
      - memgraph_data:/var/lib/memgraph

  falkordb:
    image: falkordb/falkordb:latest
    ports:
      - "6379:6379"
      - "3002:3000"  # Browser UI
    volumes:
      - falkordb_data:/data

  graphiti-mcp:
    image: getzep/graphiti-mcp:latest
    ports:
      - "8000:8000"
    environment:
      - NEO4J_URI=bolt://falkordb:6379
      - LLM_API_BASE=http://litellm:4000
    depends_on:
      - falkordb

  cognee:
    image: topoteretes/cognee:latest
    ports:
      - "8001:8000"
    environment:
      - GRAPH_DATABASE_TYPE=memgraph
      - GRAPH_DATABASE_HOST=memgraph
      - GRAPH_DATABASE_PORT=7687
      - VECTOR_DATABASE_TYPE=lancedb
      - VECTOR_DATABASE_PATH=/data/vectors
    volumes:
      - lancedb_data:/data/vectors
    depends_on:
      - memgraph

  lancedb:
    image: lancedb/lancedb:latest
    ports:
      - "8080:8080"
    volumes:
      - lancedb_data:/data
```

### Resource Requirements

| Service | CPU | Memory | Storage |
|---------|-----|--------|---------|
| Memgraph | 2 cores | 4GB | 10GB SSD |
| FalkorDB | 1 core | 2GB | 5GB SSD |
| LanceDB | 1 core | 2GB | 20GB SSD |
| Graphiti MCP | 0.5 core | 512MB | - |
| Cognee | 1 core | 1GB | - |

## Query Performance Considerations

### Indexing Strategy

**Memgraph:**
```cypher
-- Token lookups
CREATE INDEX ON :Token(symbol);
CREATE INDEX ON :Token(contract_address);

-- Protocol lookups
CREATE INDEX ON :Protocol(name);

-- Document retrieval
CREATE INDEX ON :Document(url);
CREATE INDEX ON :Document(doc_type);

-- Temporal queries
CREATE INDEX ON :MarketEvent(timestamp);
```

**LanceDB:**
```python
# IVF-PQ index for embeddings
table.create_index(
    metric="L2",
    num_partitions=256,
    num_sub_vectors=96
)
```

### Caching Strategy

Use Dragonfly (Redis-compatible) for:
- Frequently accessed entity lookups
- Query result caching (TTL: 5 minutes for prices, 1 hour for documents)
- Session-based agent memory hot path

```python
from dragonfly import Dragonfly

cache = Dragonfly(host="localhost", port=6380)

async def cached_query(key: str, query_fn, ttl: int = 300):
    cached = await cache.get(key)
    if cached:
        return json.loads(cached)

    result = await query_fn()
    await cache.setex(key, ttl, json.dumps(result))
    return result
```

## References

- Graphiti documentation: https://github.com/getzep/graphiti
- Cognee documentation: https://github.com/topoteretes/cognee
- Memgraph MAGE: https://memgraph.com/docs/mage
- FalkorDB: https://www.falkordb.com/
- LanceDB: https://lancedb.github.io/lancedb/
