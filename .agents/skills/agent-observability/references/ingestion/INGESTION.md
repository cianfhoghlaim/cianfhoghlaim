# Cognee Ingestion — Operator Runbook

Step-by-step guide for ingesting the canonical `docs/` tree into the
Cognee knowledge graph. Complements `WORKFLOW.md` (which describes the
high-level 7-phase cognition pipeline) by focusing on the concrete
operational steps for the **canonical-docs → Cognee** path.

## When to Run This

- **First time**: after the Cognee stack is up and `LLM_API_KEY` is
  configured
- **After a major docs change**: when a canonical document is added
  or significantly rewritten, re-ingest just that domain
- **Weekly**: the `cognee-ingest` GitHub Action runs on Sunday at
  04:00 UTC; this catches any drift
- **Before a GraphRAG query that you expect to return rich answers**:
  if the knowledge graph is stale, queries return less

## Pre-Flight Checklist

1. **Cognee stack is up**:
   ```bash
   docker ps --filter "name=cianfhoghlaim-cognee" --format "{{.Names}}: {{.Status}}"
   # Expected: cianfhoghlaim-cognee: Up <N> (healthy)
   ```
   If not running, bring it up:
   ```bash
   cd infrastructure/stacks/cognee
   docker compose -f compose.yaml -f sidecar.yaml up -d
   ```

2. **Cognee REST API is reachable**:
   ```bash
   curl -sf http://localhost:8100/health | jq
   # Expected: {"status": "ok"} or similar
   ```

3. **`LLM_API_KEY` is set** (needed for Phase 2 cognify):
   ```bash
   echo $LLM_API_KEY | head -c 8
   # Expected: sk-... (DeepSeek API key)
   ```
   If empty, the mise hooks should have hydrated it from
   `.env`. Verify with:
   ```bash
   grep DEEPSEEK_API_KEY .env
   ```

4. **The script is in place**:
   ```bash
   ls -lh infrastructure/scripts/cognee-ingest-docs.py
   uv run python infrastructure/scripts/cognee-ingest-docs.py --summary --all
   # Expected: 7 dataset summaries, 36 canonical docs, ~6,377 KB total
   ```

## The 3 Ways to Run

### Method 1: Mise task (local, recommended)

```bash
# Plan only — see what would be ingested
mise run docs:cognee:summary

# Single domain
mise run docs:cognee:domain standards

# All 7 domains
mise run docs:cognee
```

The mise task wraps the script with all the right env vars from
`.env` (mise-hydrated).

### Method 2: Script directly (dev, debugging)

```bash
# Plan only
uv run python infrastructure/scripts/cognee-ingest-docs.py --dry-run --all

# Per-domain summary as JSON
uv run python infrastructure/scripts/cognee-ingest-docs.py --summary --all

# Single domain
uv run python infrastructure/scripts/cognee-ingest-docs.py --domain ai-ml

# All domains, store only (no cognify)
uv run python infrastructure/scripts/cognee-ingest-docs.py --all --no-cognify

# All domains, full pipeline
uv run python infrastructure/scripts/cognee-ingest-docs.py --all
```

### Method 3: GitHub Action / Forgejo workflow (CI)

The `cognee-ingest` workflow at `.github/workflows/cognee-ingest.yaml`
(and the Forgejo mirror) supports:

- **Manual trigger** via the Actions tab: pick a domain or run all
- **Schedule trigger**: every Sunday at 04:00 UTC
- **Required secrets** (configured in repo settings):
  - `COGNEE_API_URL` — the Cognee REST API URL (e.g.
    `http://cianfhoghlaim-cognee:8000` for in-cluster, or
    `http://localhost:8100` for local)
  - `COGNEE_API_KEY` — the Cognee API key (if configured)
  - `LLM_API_KEY` — the DeepSeek API key (for cognify)

The workflow uploads a `cognee-ingest-log` artifact on every run
(14-day retention) for debugging.

## Per-Domain Datasets

| Dataset | Domain | Files | Size |
|:--|:--|--:|--:|
| `docs-architecture` | Platform & infrastructure | 8 | 78.9 KB |
| `docs-data-platform` | Lakehouse, Dagster, DLT | 4 | 57.9 KB |
| `docs-agents` | Agno, ADK, BAML, browser, MCP | 5 | 66.0 KB |
| `docs-ai-ml` | Fine-tuning, OCR, RAG, KG, vectors, Celtic | 8 | 6,059.1 KB |
| `docs-web` | TanStack, Convex+Hono, UI | 4 | 41.1 KB |
| `docs-product` | Celtic MMO, Crypteolas, game dev, ed platform | 5 | 52.0 KB |
| `docs-standards` | Project conventions, observability | 2 | 22.6 KB |
| **Total** | | **36** | **~6,377 KB** |

The `docs-ai-ml` dataset is the largest (6 MB) because it absorbed the
two largest pre-consolidation subtrees (`meaisínfhoghlaim/` and
`teanga/` totalling 394 files).

## What Happens During Cognify

The cognify phase is LLM-driven. For each dataset, Cognee:

1. **Chunks** each canonical doc by its `##` headings (Cognee's
   default chunker is heading-aware)
2. **Extracts entities** using the configured LLM (DeepSeek V4 Pro
   via OpenAI-compatible API). Named entities, tools, protocols,
   services all become graph nodes
3. **Infers relationships** between entities. Explicit relationships
   in the prose (e.g. "A depends on B", "A writes to B") become typed
   edges
4. **Generates embeddings** using `text-embedding-3-small` (the
   configured embedding model)
5. **Stores** the graph in Neo4j (shared with Graphiti) and the
   vectors in LanceDB (pgvector)

This typically takes 2-5 minutes per domain for the canonical
corpus. The `docs-ai-ml` domain takes longer (~10-15 minutes) because
of its size.

## Verifying the Ingestion

After a successful run, you should be able to query the knowledge
graph for any of the canonical docs' topics:

```bash
# Via the Cognee MCP server (if connected)
# In a Claude session with the cognee MCP server enabled:

# search: "Dagster asset partitioning"
# Expected: returns a GRAPH_COMPLETION that mentions MultiPartitionsDefinition,
# subject x language partition axes, the specific asset paths,
# and links to docs/02-data-platform/dagster-orchestration.md

# search: "Celtic MMO x402 protocol"
# Expected: returns mentions of SpacetimeDB, Anam Cara system,
# SIWE auth, TuathToken ERC-20, and links to docs/06-product/

# list_data
# Expected: shows all 7 datasets with their IDs
```

Via the Cognee REST API directly:

```bash
curl -s http://localhost:8100/api/v1/datasets | jq
# Expected: list of 7 datasets, all with status: "cognified"
```

## Troubleshooting

### `ConnectionRefusedError: [Errno 61]`

The Cognee REST API isn't reachable. Check:

```bash
docker ps --filter "name=cianfhoghlaim-cognee" --format "{{.Names}}: {{.Status}}"
# If not running:
cd infrastructure/stacks/cognee
docker compose -f compose.yaml -f sidecar.yaml up -d
docker compose logs -f cognee  # watch startup
```

### `LLMAPIKeyNotSetError: LLM API key is not set. (Status code: 422)`

The Cognee MCP server (or the Cognee process) doesn't have the LLM
key configured. Two places to check:

1. **The Cognee MCP server** (`opencode.json`):
   ```json
   "cognee": {
     "type": "local",
     "command": ["uvx", "cognee-mcp"],
     "env": {
       "LLM_API_KEY": "${DEEPSEEK_API_KEY}"
     }
   }
   ```
   The `${DEEPSEEK_API_KEY}` is expanded by OpenCode at subprocess
   launch from the process environment. Verify that
   `DEEPSEEK_API_KEY` is in `.env` (mise-hydrated) and that
   `echo $DEEPSEEK_API_KEY` shows the key.

2. **The Cognee container** (in `infrastructure/stacks/cognee/compose.yaml`):
   The container's env is hydrated by Locket sidecar from Infisical.
   Verify Locket is healthy:
   ```bash
   docker ps --filter "name=locket" --format "{{.Names}}: {{.Status}}"
   ```

   If Locket is healthy but Cognee still has no LLM key, check
   that the Cognee process env includes `LLM_API_KEY`:
   ```bash
   docker exec cianfhoghlaim-cognee printenv | grep LLM
   ```

### Add() succeeds but Cognify() hangs

Cognee is processing the dataset. Watch the logs:

```bash
docker logs -f cianfhoghlaim-cognee
```

If it hangs for >15 minutes on the `docs-ai-ml` dataset, that's
expected (it's 6 MB). If it hangs on a smaller dataset, check the
LLM API quota / rate limits.

### Cognify() fails with "graph database error"

Neo4j (or whichever graph database) is down or unhealthy:

```bash
docker ps --filter "name=neo4j" --format "{{.Names}}: {{.Status}}"
# If not running, start it via the cognee stack's depends_on
```

### Want to re-cognify from scratch

```bash
# Delete a specific dataset
curl -X DELETE http://localhost:8100/api/v1/datasets/docs-standards

# Or delete all and start over
# (Be careful — this wipes all knowledge graphs)
curl -X POST http://localhost:8100/api/v1/prune
uv run python infrastructure/scripts/cognee-ingest-docs.py --all
```

## Cost Estimate

Per the audit, ~$6 for 2,242 documents using DeepSeek V4 Pro. The
canonical corpus is 36 documents (much smaller than the full docs
tree), so actual cost is closer to **$0.50-1.00 per full ingest**.

Cost breakdown by domain (approximate, DeepSeek V4 Pro pricing):

| Domain | Cost |
|:--|--:|
| docs-standards | $0.01 |
| docs-architecture | $0.03 |
| docs-product | $0.02 |
| docs-web | $0.02 |
| docs-data-platform | $0.03 |
| docs-agents | $0.04 |
| docs-ai-ml | $0.40 (large content) |
| **Total** | **~$0.55** |

## Maintenance Schedule

- **Weekly** (Sunday 04:00 UTC): GitHub Action auto-runs the full
  ingestion. Check the workflow status in the Actions tab.
- **On canonical doc changes**: re-run the affected domain only
  (`mise run docs:cognee:domain <name>`)
- **When the LLM model changes**: re-run the full ingestion to
  rebuild the knowledge graph with the new model's entity
  extraction
- **Quarterly**: review the `entities:` fields in each canonical's
  frontmatter; update if new tools/protocols have been added since
  the last review

## Related Documentation

- `docs/cognee/WORKFLOW.md` — the 7-phase end-to-end cognition pipeline
- `docs/cognee/COGNEE_INTEGRATION.md` — Dagster asset graph integration
- `docs/cognee/COGNEE_SETUP.md` — initial Cognee stack setup
- `docs/cognee/MCP_SERVERS.md` — Cognee MCP server configuration
- `infrastructure/scripts/cognee-ingest-docs.py` — the script itself
- `openspec/changes/docs-restructuring/tasks.md` — Phase 4 validation
  tasks
- `.agents/skills/agent-docs/SKILL.md` — agent-docs skill (this runbook's
  agent counterpart)
