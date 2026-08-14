# firecrawl_mcp — 12-tool wrapper for the agent fleet

## Routing
The canonical external search surface of the agent stack. Use this module when adding a new agent-tool that needs web data, when picking which Firecrawl MCP tool to call for a given task, or when extending the wrapper with a new Pydantic response model.

## Quick start
```python
from agents.meaisinfhoghlaim.firecrawl_mcp import FirecrawlMCPClient

client = FirecrawlMCPClient()  # reads FIRECRAWL_API_KEY from env

# 1. The 3 keyless tools work without an API key
results = client.search("Dagster 1.13 release notes", categories=["developer"], limit=3)
page = client.scrape("https://docs.firecrawl.dev/features/scrape")
parsed = client.parse("/path/to/local.pdf", formats=["markdown"])

# 2. The 24 authenticated tools require FIRECRAWL_API_KEY
mapped = client.map("https://docs.dagster.io", search="partitions")
crawled = client.crawl("https://docs.dagster.io", limit=100)
research = client.research_search_papers("BiCEP v2 OCR ensemble", k=10)
dev = client.developer_search("BAML 0.224 streaming API", k=10)

# 3. The 3-tier tool availability surface
from agents.meaisinfhoghlaim.firecrawl_mcp import tools_available
avail = tools_available()  # {"keyless": frozenset, "authenticated": frozenset, "all": frozenset}
```

## Key sources
- The wrapper: `client.py` (~700 LOC, 12 public methods + 3 internal helpers)
- The 12 Pydantic response models: `FirecrawlSearchResponse`, `FirecrawlScrapeResponse`, `FirecrawlMapResponse`, `FirecrawlCrawlResponse`, `FirecrawlAgentResponse`, `FirecrawlInteractResponse`, `FirecrawlBatchResponse`, `FirecrawlMonitorCreate`, `FirecrawlMonitorCheck`, `FirecrawlResearchSearchResponse`, `FirecrawlDeveloperSearchResponse`, `FirecrawlParseResponse`, `FirecrawlAskResponse`
- The runtime contract: `_call_mcp()` is lazy-imported from `firecrawl_mcp._runtime_call` (the agents runtime wires the JSON-RPC transport)
- The 5th `## CCC + Cognee dual-search diagram` in `AGENTS.md` (now the 3-way triple-search)

## Adjacent specs
- [`dual-search-architecture`](../../../openspec/specs/dual-search-architecture/spec.md) — the 3-way dual-search contract
- [`centralized-registry`](../../../openspec/specs/centralized-registry/spec.md) — the centralized registries (model + schema + pipeline + stack)
- [`secrets-management`](../../../.agents/skills/secrets-management/SKILL.md) — the Infisical `firecrawl-api-key` contract
- [`agent-observability`](../../../.agents/skills/agent-observability/SKILL.md) — the Langfuse `@observe` contract

## DO NOT
- DO NOT call `firecrawl_*` tools directly — always go through `FirecrawlMCPClient` (it wraps the call in `@observe` + Pydantic validation)
- DO NOT use the FirecrawlMCPClient for DLT ingestion — the Firecrawl Python SDK at `dlt_sources/common/firecrawl_source.py` remains the canonical path for ingestion (the hybrid SDK/MCP split)
- DO NOT modify the Pydantic response models without updating the `openapi`-style docstring (the contract is the documentation)
- DO NOT skip the `@observe` decorator — every Firecrawl MCP call MUST be Langfuse-traced (per the agent-observability skill)

## Skill pointers
- `agents/meaisinfhoghlaim/AGENTS.md` — the OCR/HTR/alignment sub-package overview
- `agents/AGENTS.md` — the 12-agent fleet
- `.agents/skills/centralized-registry/SKILL.md` — the centralized registries
- `.agents/skills/agent-observability/SKILL.md` — the Langfuse observability contract
- `.agents/skills/secrets-management/SKILL.md` — the Infisical `firecrawl-api-key` contract