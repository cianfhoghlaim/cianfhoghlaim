# Crypteolas API Reference

Complete API documentation for the GitHub Intelligence + DeFi Analytics platform.

## Base URL

- Development: `http://localhost:8001`
- Production: `https://api.crypteolas.cianfhoghlaim.dev`

## Authentication

### SIWE (Sign-In With Ethereum)

All authenticated endpoints require a JWT token obtained via SIWE.

#### 1. Get Nonce

```http
GET /auth/nonce
```

Response:
```json
{
  "nonce": "abc123xyz..."
}
```

#### 2. Sign In

```http
POST /auth/siwe
Content-Type: application/json

{
  "message": "crypteolas.cianfhoghlaim.dev wants you to sign in...",
  "signature": "0x..."
}
```

Response:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "address": "0x1234...",
  "expires_at": "2025-01-27T12:00:00Z"
}
```

---

## GitHub Intelligence Endpoints

### Search Repositories

```http
GET /api/github/repositories?query=defi&language=solidity&limit=20
```

Parameters:
- `query`: Search query
- `language`: Filter by language (optional)
- `min_stars`: Minimum stars (optional)
- `limit`: Max results (default 20)

Response:
```json
{
  "repositories": [
    {
      "id": "uniswap/v4-core",
      "name": "v4-core",
      "owner": "uniswap",
      "description": "Core smart contracts for Uniswap v4",
      "stars": 2500,
      "forks": 450,
      "language": "Solidity",
      "topics": ["defi", "amm", "ethereum"],
      "last_commit": "2025-01-20T10:30:00Z",
      "contributors_count": 45
    }
  ],
  "total": 156,
  "query_time_ms": 89
}
```

### Get Repository Details

```http
GET /api/github/repositories/{owner}/{repo}
```

Response:
```json
{
  "id": "uniswap/v4-core",
  "name": "v4-core",
  "owner": "uniswap",
  "description": "Core smart contracts for Uniswap v4",
  "stars": 2500,
  "forks": 450,
  "language": "Solidity",
  "languages": {
    "Solidity": 85.5,
    "TypeScript": 10.2,
    "Shell": 4.3
  },
  "commit_activity": {
    "last_week": 45,
    "last_month": 180,
    "total": 1250
  },
  "top_contributors": [
    {"login": "haydenadams", "contributions": 350}
  ],
  "dependencies": ["openzeppelin", "foundry"],
  "security_alerts": 0
}
```

### Get Commit History

```http
GET /api/github/repositories/{owner}/{repo}/commits?since=2025-01-01
```

Response:
```json
{
  "commits": [
    {
      "sha": "abc123",
      "message": "feat: add hook interface",
      "author": "haydenadams",
      "date": "2025-01-20T10:30:00Z",
      "files_changed": 5,
      "additions": 250,
      "deletions": 30
    }
  ],
  "total": 45
}
```

### Search Code

```http
POST /api/github/code/search
Content-Type: application/json

{
  "query": "reentrancy guard implementation",
  "repositories": ["openzeppelin/openzeppelin-contracts"],
  "file_types": [".sol"],
  "limit": 10
}
```

Response:
```json
{
  "results": [
    {
      "repository": "openzeppelin/openzeppelin-contracts",
      "file_path": "contracts/security/ReentrancyGuard.sol",
      "matches": [
        {
          "line": 45,
          "content": "modifier nonReentrant() {",
          "context": "abstract contract ReentrancyGuard {"
        }
      ],
      "relevance_score": 0.95
    }
  ]
}
```

---

## DeFi Analytics Endpoints

### List Protocols

```http
GET /api/analytics/protocols?chain=ethereum&category=dex&limit=20
```

Parameters:
- `chain`: Filter by chain (optional)
- `category`: dex, lending, bridge, yield, etc. (optional)
- `min_tvl`: Minimum TVL in USD (optional)
- `limit`: Max results (default 20)

Response:
```json
{
  "protocols": [
    {
      "id": "uniswap",
      "name": "Uniswap",
      "category": "dex",
      "chains": ["ethereum", "arbitrum", "base", "polygon"],
      "tvl_usd": 5250000000,
      "tvl_change_24h": 2.5,
      "tvl_change_7d": 8.3,
      "volume_24h": 1200000000,
      "fees_24h": 3600000,
      "logo": "https://..."
    }
  ],
  "total": 450
}
```

### Get Protocol Details

```http
GET /api/analytics/protocols/{id}
```

Response:
```json
{
  "id": "uniswap",
  "name": "Uniswap",
  "description": "Decentralized exchange protocol",
  "category": "dex",
  "chains": ["ethereum", "arbitrum", "base"],
  "tvl_by_chain": {
    "ethereum": 3500000000,
    "arbitrum": 1200000000,
    "base": 550000000
  },
  "metrics": {
    "tvl_usd": 5250000000,
    "volume_24h": 1200000000,
    "volume_7d": 8500000000,
    "fees_24h": 3600000,
    "revenue_24h": 2400000,
    "users_24h": 45000
  },
  "tvl_history": [
    {"date": "2025-01-20", "tvl": 5250000000},
    {"date": "2025-01-19", "tvl": 5120000000}
  ],
  "github": "uniswap/v4-core",
  "token": {
    "symbol": "UNI",
    "address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
    "price_usd": 12.50,
    "market_cap": 7500000000
  },
  "audits": [
    {"auditor": "OpenZeppelin", "date": "2024-06-15", "url": "..."}
  ]
}
```

### Get Yield Opportunities

```http
GET /api/analytics/yields?chain=ethereum&min_apy=5&limit=20
```

Response:
```json
{
  "pools": [
    {
      "id": "uniswap-v3-eth-usdc",
      "protocol": "uniswap",
      "chain": "ethereum",
      "pool": "ETH-USDC",
      "apy_base": 12.5,
      "apy_reward": 3.2,
      "apy_total": 15.7,
      "tvl_usd": 450000000,
      "volume_24h": 120000000,
      "il_risk": "high"
    }
  ]
}
```

### Compare Protocols

```http
POST /api/analytics/compare
Content-Type: application/json

{
  "protocols": ["uniswap", "sushiswap", "curve"],
  "metrics": ["tvl", "volume_24h", "fees_24h", "users_24h"]
}
```

Response:
```json
{
  "comparison": {
    "uniswap": {
      "tvl": 5250000000,
      "volume_24h": 1200000000,
      "fees_24h": 3600000,
      "users_24h": 45000
    },
    "sushiswap": {
      "tvl": 850000000,
      "volume_24h": 150000000,
      "fees_24h": 450000,
      "users_24h": 8500
    },
    "curve": {
      "tvl": 2100000000,
      "volume_24h": 350000000,
      "fees_24h": 175000,
      "users_24h": 12000
    }
  }
}
```

### Get Funding Rates

```http
GET /api/analytics/funding?symbols=BTC,ETH,SOL
```

Response:
```json
{
  "rates": [
    {
      "symbol": "BTC",
      "exchange": "binance",
      "rate": 0.0123,
      "predicted_rate": 0.0115,
      "open_interest": 12500000000,
      "next_funding": "2025-01-20T16:00:00Z"
    }
  ]
}
```

---

## Search Endpoints

### Hybrid Search (Code + Documentation)

```http
POST /api/search/hybrid
Content-Type: application/json

{
  "query": "flash loan implementation with callback",
  "search_type": "hybrid",
  "sources": ["code", "documentation"],
  "vector_weight": 0.6,
  "graph_weight": 0.4,
  "limit": 10
}
```

Response:
```json
{
  "results": [
    {
      "id": "aave-v3-flashloan",
      "type": "code",
      "source": "aave/aave-v3-core",
      "file_path": "contracts/flashloan/FlashLoanSimpleReceiverBase.sol",
      "content": "function executeOperation(...",
      "score": 0.92,
      "graph_context": {
        "related_protocols": ["aave", "uniswap"],
        "security_considerations": ["reentrancy"]
      }
    }
  ]
}
```

### Documentation Search

```http
POST /api/search/docs
Content-Type: application/json

{
  "query": "how to integrate Uniswap v4 hooks",
  "protocols": ["uniswap"],
  "limit": 5
}
```

---

## Agent Endpoints (AG-UI)

### Chat with Research Agent

```http
POST /api/agent/chat
Content-Type: application/json

{
  "messages": [
    {"role": "user", "content": "Compare TVL trends for Aave vs Compound over the last month"}
  ],
  "stream": true
}
```

Response (SSE stream):
```
data: {"type": "text", "content": "I'll analyze the TVL trends..."}
data: {"type": "tool_call", "name": "defi_metrics", "args": {"protocols": ["aave", "compound"]}}
data: {"type": "tool_result", "content": {"aave_tvl": [...], "compound_tvl": [...]}}
data: {"type": "text", "content": "Based on the data...\n\n| Protocol | Start TVL | End TVL | Change |..."}
data: {"type": "done"}
```

### Get Agent Capabilities

```http
GET /api/agent/info
```

Response:
```json
{
  "agent": "crypteolas_agent",
  "sub_agents": [
    "protocol_research_agent",
    "code_analysis_agent",
    "defi_analytics_agent",
    "documentation_agent"
  ],
  "tools": [
    "code_search",
    "document_search",
    "defi_metrics",
    "github_repository",
    "protocol_comparison"
  ],
  "capabilities": [
    "Protocol research and comparison",
    "Code semantic search",
    "TVL and yield analysis",
    "Security audit queries",
    "Documentation lookup"
  ]
}
```

---

## Error Responses

All errors follow this format:
```json
{
  "error": "error_code",
  "message": "Human readable message",
  "details": {}
}
```

Common error codes:
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `unauthorized` | 401 | Missing or invalid token |
| `forbidden` | 403 | Insufficient permissions |
| `not_found` | 404 | Resource not found |
| `rate_limited` | 429 | Too many requests |
| `github_rate_limit` | 429 | GitHub API limit exceeded |
| `validation_error` | 422 | Invalid request body |

---

## Rate Limits

| Endpoint | Authenticated | Anonymous |
|----------|---------------|-----------|
| `/api/github/*` | 100/min | 20/min |
| `/api/analytics/*` | 200/min | 50/min |
| `/api/search/*` | 60/min | 10/min |
| `/api/agent/*` | 30/min | 5/min |

---

## Caching

Responses include cache headers:

```http
Cache-Control: public, max-age=300
ETag: "abc123"
```

### Cache TTLs

| Data Type | TTL |
|-----------|-----|
| Repository metadata | 1 hour |
| Commit history | 15 minutes |
| Protocol TVL | 5 minutes |
| Yield data | 1 minute |
| Price data | 30 seconds |

---

## OpenAPI Schema

Full OpenAPI 3.1 schema available at:
- Swagger UI: `/docs`
- ReDoc: `/redoc`
- JSON: `/openapi.json`
