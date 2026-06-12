# Cognee — AI Memory System with GraphRAG

## Overview

Cognee is an open-source AI memory and knowledge management framework that builds dynamic knowledge graphs from documents, conversations, and data pipelines. It supports multiple graph backends (Neo4j, Memgraph, FalkorDB), provides GraphRAG capabilities, and integrates with LLMs for semantic retrieval and reasoning over structured knowledge.

## Why This Matters for Kings' College Galway

Cognee is the primary knowledge graph builder for the curriculum extraction pipeline. When Dagster processes a Leaving Cert Mathematics syllabus, Cognee extracts entities (learning outcomes, prerequisite concepts, assessment criteria), builds a graph with weighted edges representing prerequisite relationships, and serves GraphRAG queries so the web app can answer "what do I need to understand before tackling differentiation?" This graph is the pedagogical backbone — it encodes the dependency structure that teachers use to sequence lessons, and it does so automatically from unstructured syllabus documents.

## Key Features

- **Multi-backend graphs** — Neo4j, Memgraph, FalkorDB (all three deployed in this infrastructure)
- **GraphRAG** — Retrieval-augmented generation over knowledge graphs
- **Document ingestion** — Automatic entity extraction and relationship inference
- **MCP integration** — Cognee MCP server for Cursor/Claude Desktop/VS Code integration
- **Temporal awareness** — Track how knowledge evolves as curricula change

## Stack Composition (2026-06-12)

| Service | Image | Port | Purpose |
|:--|:--|:--|:--|
| `cognee` | `cognee/cognee:latest` | 8000 (host: 8100) | REST API + 6-dataset knowledge graph (aistear / primary / junior_cycle / senior_cycle / tertiary / cross_stage) |
| `cognee-postgres` | `pgvector/pgvector:pg17` | 5432 (internal) | Postgres + pgvector for graph + embedding storage (`USE_UNIFIED_PROVIDER=pghybrid`) |
| `locket` | `ghcr.io/bpbradley/locket:infisical` | — (sidecar) | Infisical secret injection (production); no-op in dev |

## LLM Routing

Cognee delegates LLM calls to the **LiteLLM proxy** at `http://litellm:4000/v1`
(deployed in `infrastructure/stacks/engineering/litellm`). This means:
- **One key** to manage (LITELLM_MASTER_KEY) — not one per provider
- **Fallback chains** defined centrally in `litellm/config/config.yaml`
- **Easy model swaps** via `COGNEE_LLM_MODEL` env var (no rebuild)

### Default model: `deepseek/deepseek-chat`

The `deepseek/deepseek-chat` route is defined in `litellm/config/config.yaml` as:
```yaml
- model_name: deepseek/deepseek-chat
  litellm_params:
    model: openai/deepseek-chat
    api_base: https://api.deepseek.com/v1
    api_key: os.environ/DEEPSEEK_API_KEY
```

DeepSeek was chosen over the `extract` alias (Gemini 2.5 Pro → GLM 4.6 → Gemini Flash)
because the current Gemini API key is blocked (403 PERMISSION_DENIED).

### Why LLM_API_KEY=no-key-needed?

The cognee openai client sends `Authorization: Bearer <LLM_API_KEY>` to the
LiteLLM proxy. The proxy then **forwards** the client's bearer token as the
upstream API key. If the client sends the LiteLLM master key, DeepSeek rejects
it as invalid. Setting `LLM_API_KEY=no-key-needed` is a sentinel that tells
litellm "no valid client key" → use the proxy's own DEEPSEEK_API_KEY env var.

### Override options (via `COGNEE_LLM_MODEL` env)

| Alias | Use case | Cost |
|:--|:--|:--|
| `deepseek/deepseek-chat` (default) | Cost-sensitive extraction | $0.14 / $0.28 per 1M tokens |
| `extract` | General BAML extraction (currently broken by Gemini 403) | Mixed |
| `local/irish/uccix` | Irish-language entity names | Free (local GGUF) |
| `openai/glm-4.6` | Coding-style entity names | $0.50 / $2.00 per 1M tokens |

### Default embedding: `openai/text-embedding-3-small`

The full litellm model path is required because cognee validates the
embedding model name against tiktoken at startup. LiteLLM alias names
like `embedding` or `embedding-curriculum` are not tiktoken-recognizable.

## Deployment

### Local (dev)

```bash
# From infrastructure/stacks/machine_learning/cognee/
docker compose -f compose.yaml -f sidecar.yaml -f compose.dev.yaml up -d

# Verify
curl -s http://localhost:8100/health | jq
```

The `compose.dev.yaml` replaces the production Locket sidecar with a no-op
alpine container and sources secrets from the local `.env` (hydrated by `mise`
hooks from Infisical).

### Local (mock-only, no LLM)

For smoke-testing compose without LiteLLM running, set in `.env`:
```bash
LITELLM_API_KEY=sk-1234
COGNEE_LLM_MODEL=deepseek/deepseek-chat
```
The `sk-1234` placeholder will let cognee start; the first entity-extraction
call will fail (which is fine for compose linting).

### Production (via Komodo)

```bash
km run procedure deploy-cognee-bunchloch
```

5-stage deploy: prereqs → litellm + lakehouse + lancedb → cognee → pangolin
routes → health checks.

### Direct (via Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml up -d
```

Locket reads `secrets.env` (which contains `infisical://dev-baile/...` URI
references) and writes the resolved values to a shared tmpfs volume that
cognee reads at startup.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `LITELLM_API_KEY` | Yes | LiteLLM master key (set to `no-key-needed` in compose.yaml to force proxy to use its own DEEPSEEK_API_KEY) | `no-key-needed` |
| `COGNEE_POSTGRES_PASSWORD` | Yes | Postgres password for the cognee vector store | `devpassword` |
| `LANCEDB_API_KEY` | Yes | API key for the lakehouse Lance Namespace (`lakehouse-lance-namespace:8182`) | `devtoken` |
| `COGNEE_LLM_MODEL` | No | LiteLLM model alias for entity extraction | `deepseek/deepseek-chat` |
| `COGNEE_EMBEDDING_MODEL` | No | LiteLLM model alias for embeddings | `openai/text-embedding-3-small` |
| `ENVIRONMENT` | No | Runtime environment | `production` |
| `LOG_LEVEL` | No | Log verbosity | `INFO` |
| `REQUIRE_AUTHENTICATION` | No | Disable cognee's bearer-token auth (set to `true` in production) | `false` |
| `ENABLE_BACKEND_ACCESS_CONTROL` | No | Disable cognee's multi-tenant mode (set to `true` in production) | `false` |

## Access

- **API**: `http://localhost:8100` (or `https://cognee.cianfhoghlaim.ie` via Pangolin)
- **Health**: `GET /health` returns `{"status": "ready","health":"healthy",...}` when ready
- **MCP**: `cognee-mcp` is configured in `opencode.json` at the repo root and
  routes to `COGNEE_API_URL=http://localhost:8100` (the cognee REST API itself)

## Datasets

Cognee serves 6 bilingual EN/GA datasets, one per curriculum stage plus a
cross-stage synthesis:

| Dataset | Stage | Source |
|:--|:--|:--|
| `oideachais.aistear` | Early childhood (0-6) | Aistear framework PDFs |
| `oideachais.primary` | Primary (4-12) | NCCA primary curriculum |
| `oideachais.junior_cycle` | Junior cycle (12-16) | NCCA junior cycle spec |
| `oideachais.senior_cycle` | Senior cycle (16-19) | NCCA leaving cert spec |
| `oideachais.tertiary` | Tertiary / FET | QQI awards + HE frameworks |
| `oideachais.cross_stage` | Bridges between stages | Computed cross-stage edges (BRIDGES_TO, PREPARES_FOR, etc.) |

The 8 cross-stage edge types are enumerated in `blueprint.yaml`.

## Bring-up Status (2026-06-12)

The stack was brought up locally on bunchloch and verified:

```bash
$ curl -s http://localhost:8100/health
{"status":"ready","health":"healthy","version":"1.1.2-local"}
```

The container pulls the `cognee/cognee:latest` image, creates a pgvector-
enabled Postgres, and serves the REST API. LLM roundtrips work — the
cognee → litellm → deepseek pipeline is functional end-to-end.

**Caveat**: The current `DEEPSEEK_API_KEY` in `.env` is a placeholder. Real
entity extraction will fail with `Authentication Fails` until the key is
replaced with a valid one. This is a `.env` issue, not a stack issue.

## Upstream

- **Repository**: <https://github.com/topoteretes/cognee>
- **Documentation**: <https://cognee.ai>
- **Latest**: Active development (2025) — GraphRAG improvements, multi-model LLM support, MCP server integration

## Related

- `infrastructure/scripts/cognee-ingest-docs.py` — bulk ingestion script (runs
  `mise run docs:cognee`)
- `.agents/skills/cognee/SKILL.md` — agent-facing guide
- `docs/01-cognee/` — canonical docs for the cognee integration
- `infrastructure/komodo/stacks/cognee-bunchloch.toml` + `deploy-cognee-bunchloch.toml` — Komodo deploy
