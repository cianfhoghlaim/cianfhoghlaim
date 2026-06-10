# MCP Servers — Full Configuration Reference

All Model Context Protocol (MCP) servers configured in `opencode.json` for the Kings' College Galway project. These servers expose tools to agents for code search, knowledge graph queries, web scraping, browser automation, database queries, and secret management.

## Server Inventory

| Server | Type | Port | Purpose | MCP Package |
|:--|:--|:--|:--|:--|
| `cocoindex-code` | local | — | Semantic code search | `ccc mcp` |
| `cognee` | local | 8100 | Document ingestion + GraphRAG | `cognee-mcp` |
| `graphiti` | local | 8000 | Temporal knowledge graph | `graphiti_core.mcp` |
| `langfuse` | local | — | LLM trace observability | `@langfuse/mcp` |
| `motherduck` | local | — | SQL analytics | `mcp-server-motherduck` |
| `firecrawl` | local | — | Web scraping | `firecrawl-mcp` |
| `browserbase` | local | — | Browser automation | `@browserbasehq/mcp` |
| `chrome` | local | — | Chrome DevTools | `chrome-devtools-mcp` |
| `infisical` | local | 8081 | Secret management | `@infisical/mcp` |

## Configuration — `opencode.json`

### Cognee — Document Cognition + GraphRAG

```json
"cognee": {
  "type": "local",
  "command": ["uvx", "cognee-mcp"],
  "env": {
    "COGNEE_API_URL": "http://localhost:8100",
    "COGNEE_API_KEY": "infisical://dev-baile/cognee/api_key",
    "LLM_API_KEY": "infisical://dev-baile/deepseek/api_key"
  },
  "enabled": true
}
```

**Prerequisites**: Cognee Docker container running on port 8100.

**Agent tools exposed**:
- `cognee_add(document, dataset)` — Add documents to Cognee
- `cognee_cognify(dataset)` — Build knowledge graph
- `cognee_search(query, search_type)` — Search graph (GRAPH_COMPLETION, CHUNKS, INSIGHTS, SUMMARIES)

### CCC — Semantic Code Search

```json
"cocoindex-code": {
  "type": "local",
  "command": ["ccc", "mcp"],
  "enabled": true
}
```

**Prerequisites**: `.cocoindex_code/target_sqlite.db` index database.

**Agent tools exposed**:
- `cocoindex-code_search(query, limit, languages, paths)` — Semantic code search
- Index refresh is automatic on each search

### Graphiti — Temporal Knowledge Graph

```json
"graphiti": {
  "type": "local",
  "command": ["uv", "run", "python", "-m", "graphiti_core.mcp"],
  "env": {
    "NEO4J_URI": "bolt://localhost:7687",
    "NEO4J_USER": "neo4j",
    "NEO4J_PASSWORD": "devpassword"
  },
  "enabled": true
}
```

**Prerequisites**: Graphiti server running on port 8000 with Neo4j backend.

**Agent tools exposed**:
- `graphiti_search(query)` — Temporal knowledge graph search
- `graphiti_get_node(id)` — Retrieve specific graph node
- `graphiti_get_edges(node_id)` — Get relationships for a node

### Langfuse — LLM Trace Observability

```json
"langfuse": {
  "type": "local",
  "command": ["bunx", "-y", "@langfuse/mcp"],
  "env": {
    "LANGFUSE_PUBLIC_KEY": "infisical://dev-baile/langfuse/public_key",
    "LANGFUSE_SECRET_KEY": "infisical://dev-baile/langfuse/secret_key",
    "LANGFUSE_HOST": "https://langfuse.cianfhoghlaim.ie"
  },
  "enabled": true
}
```

**Prerequisites**: Langfuse stack running (port 3000).

**Agent tools exposed**:
- `langfuse_get_trace(trace_id)` — Retrieve LLM call trace
- `langfuse_get_traces(project_id)` — List recent traces
- `langfuse_get_prompt(prompt_name)` — Retrieve prompt template

### MotherDuck — SQL Analytics

```json
"motherduck": {
  "type": "local",
  "command": ["uvx", "mcp-server-motherduck", "--db-path", ":memory:", "--read-write", "--allow-switch-databases"],
  "env": {
    "MOTHERDUCK_TOKEN": "infisical://dev-baile/motherduck/token"
  },
  "enabled": true
}
```

**Agent tools exposed**:
- `motherduck_execute_query(sql)` — Execute SQL query
- `motherduck_list_tables()` — List available tables
- `motherduck_list_databases()` — List databases

### Firecrawl — Web Scraping

```json
"firecrawl": {
  "type": "local",
  "command": ["bunx", "-y", "firecrawl-mcp"],
  "env": {
    "FIRECRAWL_API_KEY": "infisical://dev-baile/firecrawl/api_key"
  },
  "enabled": true
}
```

**Agent tools exposed**:
- `firecrawl_scrape(url, formats)` — Scrape a single page
- `firecrawl_search(query)` — Search the web
- `firecrawl_crawl(url)` — Crawl a website
- `firecrawl_map(url)` — Map site URLs

### Browserbase — Browser Automation

```json
"browserbase": {
  "type": "local",
  "command": ["bunx", "-y", "@browserbasehq/mcp", "--modelName", "deepseek/deepseek-chat", "--experimental"],
  "env": {
    "BROWSERBASE_API_KEY": "infisical://dev-baile/browserbase/api_key",
    "BROWSERBASE_PROJECT_ID": "infisical://dev-baile/browserbase/project_id",
    "DEEPSEEK_API_KEY": "infisical://dev-baile/deepseek/api_key"
  },
  "enabled": true
}
```

**Agent tools exposed**:
- `browserbase_navigate(url)` — Navigate to URL
- `browserbase_act(action)` — Perform action on page
- `browserbase_extract(instruction)` — Extract structured data
- `browserbase_observe(instruction)` — Observe actionable elements

### Chrome — Local DevTools

```json
"chrome": {
  "type": "local",
  "command": ["bunx", "-y", "chrome-devtools-mcp"],
  "enabled": true
}
```

**Agent tools exposed**:
- `chrome_navigate_page(url)` — Navigate in Chrome
- `chrome_take_screenshot()` — Capture page screenshot
- `chrome_take_snapshot()` — Get accessibility tree
- `chrome_evaluate_script(js)` — Run JavaScript

### Infisical — Secret Management

```json
"infisical": {
  "type": "local",
  "command": ["bunx", "-y", "@infisical/mcp"],
  "env": {
    "INFISICAL_UNIVERSAL_AUTH_CLIENT_ID": "${INFISICAL_CLIENT_ID}",
    "INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET": "${INFISICAL_CLIENT_SECRET}",
    "INFISICAL_HOST_URL": "http://localhost:8081",
    "INFISICAL_PROJECT_ID": "${INFISICAL_PROJECT_ID}"
  },
  "enabled": true
}
```

**Agent tools exposed**:
- `infisical_get_secret(name)` — Retrieve a secret
- `infisical_list_secrets()` — List all secrets
- `infisical_create_secret(name, value)` — Create new secret

## MCP Activation Flow

```
1. opencode starts → reads opencode.json
2. For each "enabled": true MCP server:
   a. Resolves Infisical URI references (infisical://...)
   b. Installs package if needed (bunx/uvx auto-install)
   c. Starts MCP server subprocess
   d. Registers tools from MCP server
3. Agents can now call tools from all registered MCP servers
```

## Adding a New MCP Server

```json
"new-server": {
  "type": "local",
  "command": ["bunx", "-y", "new-mcp-package"],
  "env": {
    "API_KEY": "infisical://dev-baile/new-server/api_key",
    "API_URL": "http://localhost:PORT"
  },
  "enabled": true
}
```

1. Add the block to `opencode.json` under `"mcp"`
2. Add any needed secrets to Infisical vault
3. Add the Infisical reference to `.infisical.env`
4. Run `bun run secrets:init` to hydrate
5. Restart opencode to pick up the new server
