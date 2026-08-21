# Crypteolas Agent Architecture

Multi-agent system for cryptocurrency protocol research and DeFi analytics.

## Architecture Overview

```
                    ┌─────────────────┐
                    │   User Query    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Root Agent    │
                    │  (Orchestrator) │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐
│    Protocol     │ │     Code        │ │     DeFi        │
│    Research     │ │    Analysis     │ │   Analytics     │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │          ┌────────▼────────┐          │
         │          │  Documentation  │          │
         │          │     Agent       │          │
         │          └────────┬────────┘          │
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │     Tools       │
                    │ (code_search,   │
                    │  defi_metrics,  │
                    │  doc_search)    │
                    └─────────────────┘
```

## Agent Framework

Built on **Google ADK (Agent Developer Kit)** with:
- LlmAgent for agent definitions
- Sub-agent routing for specialization
- Tool integration via function decorators
- AG-UI protocol for streaming responses

## Root Agent

**Location:** `sruth/crypteolas/agents/adk/root_agent.py`

The orchestrator that routes queries to specialist agents.

### Query Classification

```python
def classify_query(query: str) -> str:
    """Routes to: code, analytics, documentation, or research."""
```

| Keywords | Agent |
|----------|-------|
| code, implementation, function, contract, github | code_analysis |
| tvl, yield, apy, price, volume, funding | defi_analytics |
| docs, documentation, whitepaper, audit | documentation |
| research, compare, protocol, tokenomics | protocol_research |

### Model Configuration

```python
# From agents/config.py
orchestrator_model = "claude-sonnet-4-20250514"  # Fast routing
specialist_model = "claude-opus-4-20250514"       # Deep analysis
```

## Specialist Agents

### 1. Protocol Research Agent

**File:** `agents/adk/protocol_research.py`

Deep research on DeFi protocols:
- Protocol architecture analysis
- Tokenomics investigation
- Competitive comparison
- Risk assessment

**Research Capabilities:**
- Protocol mechanism analysis
- Token distribution research
- Governance structure review
- Security posture evaluation

**Example Interaction:**
```
User: Research Uniswap v4 hooks mechanism
Agent: Uniswap v4 introduces a hooks system that allows...
       The hook interface includes beforeSwap, afterSwap...
       Key security considerations include...
```

### 2. Code Analysis Agent

**File:** `agents/adk/code_analysis.py`

GitHub repository and code analysis:
- Semantic code search
- Implementation understanding
- Dependency analysis
- Security pattern detection

**Analysis Capabilities:**
- Smart contract code review
- Pattern recognition (reentrancy, overflow)
- Dependency graph construction
- Code quality metrics

**Example Interaction:**
```
User: How does Aave implement flash loans?
Agent: Aave's flash loan implementation in FlashLoanLogic.sol...
       The key functions are executeFlashLoanSimple and...
       Security measures include the _handleFlashLoanRepayment...
```

### 3. DeFi Analytics Agent

**File:** `agents/adk/defi_analytics.py`

On-chain and market analytics:
- TVL tracking and trends
- Yield comparison
- Funding rate analysis
- Volume and liquidity metrics

**Data Sources:**
- DeFiLlama (TVL, protocols)
- CoinGecko (prices, market data)
- Binance (derivatives, funding)

**Example Interaction:**
```
User: What are the best ETH yield opportunities right now?
Agent: Current top ETH yield opportunities:
       1. Lido stETH: 3.8% APY (lowest risk)
       2. Aave ETH Supply: 2.1% + 1.2% rewards...
       3. Uniswap ETH-USDC: 15.7% APY (high IL risk)
```

### 4. Documentation Agent

**File:** `agents/adk/documentation_agent.py`

Protocol documentation and audit research:
- Documentation search
- Whitepaper analysis
- Audit report queries
- Technical specification lookup

**Document Types:**
- Protocol whitepapers
- Technical documentation
- Audit reports
- API references

**Example Interaction:**
```
User: What did the OpenZeppelin audit find for Uniswap v4?
Agent: The OpenZeppelin audit of Uniswap v4 (June 2024) found...
       Critical findings: 0
       High severity: 2 (both resolved)
       Medium severity: 5...
```

## Tools

### code_search

**File:** `agents/tools/code_search.py`

Semantic search across code repositories.

```python
@tool
def code_search(
    query: str,
    repositories: list[str] = None,
    file_types: list[str] = None,
    limit: int = 10
) -> list[CodeResult]:
    """Search code semantically using BGE-M3 embeddings."""
```

Features:
- Tree-sitter parsing for AST-aware chunking
- BGE-M3 multilingual embeddings
- File type filtering
- Context window expansion

### document_search

**File:** `agents/tools/document_search.py`

Search protocol documentation and whitepapers.

```python
@tool
def document_search(
    query: str,
    protocols: list[str] = None,
    doc_types: list[str] = None
) -> list[DocResult]:
    """Search protocol documentation."""
```

Document types:
- `whitepaper` - Protocol whitepapers
- `docs` - Technical documentation
- `audit` - Security audit reports
- `api` - API documentation

### defi_metrics

**File:** `agents/tools/defi_metrics.py`

Query DeFi protocol metrics.

```python
@tool
def defi_metrics(
    protocols: list[str],
    metrics: list[str] = ["tvl", "volume_24h"],
    time_range: str = "7d"
) -> dict[str, ProtocolMetrics]:
    """Get DeFi protocol metrics from DeFiLlama."""
```

Available metrics:
- `tvl` - Total Value Locked
- `volume_24h` / `volume_7d`
- `fees_24h` / `revenue_24h`
- `users_24h`
- `apy` / `apy_base` / `apy_reward`

## AG-UI Protocol Integration

The agents expose an AG-UI protocol endpoint for streaming responses.

### Endpoint

```
POST /api/agent/chat
```

### Event Types

| Event | Description |
|-------|-------------|
| `text` | Streaming text response |
| `tool_call` | Agent invoking a tool |
| `tool_result` | Tool execution result |
| `agent_handoff` | Sub-agent delegation |
| `chart` | Data visualization |
| `table` | Tabular data |
| `done` | Stream complete |

### Rich Output Types

The agent can emit structured UI components:

```json
{
  "type": "chart",
  "chart_type": "line",
  "data": {
    "labels": ["Jan 1", "Jan 2", "..."],
    "datasets": [
      {"label": "Uniswap TVL", "data": [5.2, 5.3, ...]}
    ]
  }
}
```

```json
{
  "type": "table",
  "headers": ["Protocol", "TVL", "Volume 24h"],
  "rows": [
    ["Uniswap", "$5.2B", "$1.2B"],
    ["Aave", "$12.5B", "$450M"]
  ]
}
```

## Callbacks

### Citation Callbacks

**File:** `agents/callbacks/citation_callbacks.py`

Tracks sources for all agent responses:

```python
class CitationCallback:
    """Captures code and documentation citations."""

    def on_tool_call(self, tool_name: str, result: Any):
        if tool_name == "code_search":
            self.citations.append({
                'type': 'code',
                'repository': result.repository,
                'file': result.file_path,
                'line': result.line_number
            })
```

## Knowledge Graph Integration

### Graphiti (Temporal)

Tracks protocol evolution over time:

```python
from crypteolas.knowledge_graph.graphiti import temporal_graph

# Query temporal relationships
results = temporal_graph.search(
    "Uniswap governance changes",
    time_range=("2024-01-01", "2025-01-01"),
)
```

### Cognee (Static)

Static protocol knowledge:

```python
from crypteolas.knowledge_graph.cognee import static_knowledge

# Query static relationships
results = static_knowledge.query(
    "Which protocols are built on Aave?"
)
```

## Testing Agents

### Unit Tests

```bash
uv run pytest tests/test_agents.py -v
```

### Interactive Testing

```python
from crypteolas.agents.adk.root_agent import app

response = app.run("Compare Uniswap and Sushiswap TVL trends")
print(response)
```

### Demo Mode

```bash
uv run python -m crypteolas.demo.run_demo
```

## Configuration

**File:** `agents/config.py`

```python
class AgentConfig:
    # Model settings
    orchestrator_model: str = "claude-sonnet-4-20250514"
    specialist_model: str = "claude-opus-4-20250514"

    # Tool settings
    code_search_limit: int = 10
    doc_search_limit: int = 5
    metrics_default_range: str = "7d"

    # Data source settings
    github_cache_ttl: int = 3600
    defillama_cache_ttl: int = 300
    coingecko_cache_ttl: int = 60
```

## Adding New Agents

1. Create agent file in `agents/adk/`
2. Define LlmAgent with instruction prompt
3. Register tools from `agents/tools/`
4. Add to root_agent.sub_agents
5. Update classify_query() routing

Example:
```python
from google.adk.agents import LlmAgent
from ..config import config

security_agent = LlmAgent(
    name="security_analysis",
    model=config.specialist_model,
    description="Analyzes smart contract security",
    instruction="You are a security expert...",
    tools=[code_search, audit_search],
)
```

## Security Considerations

### Rate Limiting

Agents respect API rate limits:
- GitHub: 5000 requests/hour
- DeFiLlama: No limit (but be respectful)
- CoinGecko: 50 requests/minute (free tier)

### Data Freshness

All responses include data freshness indicators:
```
[Data as of 2025-01-20 12:00 UTC]
```

### Confidence Levels

Agents express uncertainty appropriately:
- High confidence: Direct data from APIs
- Medium confidence: Derived/calculated metrics
- Low confidence: Inferred from incomplete data
