# Infrastructure Stacks

Reorganised per Phase 1 (2026-06-23): stacks are now **flat** — one
directory per stack under `infrastructure/stacks/<name>/`, with no
category subdirectory. See `infrastructure/AGENTS.md` for the canonical
stack inventory and `infrastructure/GOLD_STANDARD.md` for the
6-file template that every stack SHALL follow.

## At a Glance

| Property | Value |
|:--|:--|
| Layout | Flat — every stack is a direct child of `infrastructure/stacks/` |
| Total stacks | **93** (as of 2026-06-24; changes as new ones are added via the stack-ops skill) |
| Standard file count | 6 (compose, sidecar, pangolin, secrets, blueprint, .env.example) |
| Stack directory | `infrastructure/stacks/<name>/` |

The 93 stacks are listed in full in `infrastructure/AGENTS.md` § "Stack
Inventory" (alphabetical, with purpose and key ports). The
[`infrastructure/QUADRANT-TO-STACK-MAP.md`](../QUADRANT-TO-STACK-MAP.md)
file groups them by which workspace-member quadrant consumes them.

## Quick Navigation — "I need a..."

| If you need to... | Look at... |
|:--|:--|
| S3-compatible object storage | `infrastructure/stacks/garage/` (local, Hetzner) or Cloudflare R2 adapter |
| Iceberg / DuckLake catalog | `infrastructure/stacks/lakehouse/` (Lakekeeper + Lance Namespace + Postgres + Garage) |
| Git-for-data | `infrastructure/stacks/lakefs/` |
| Git hosting (self-hosted Forge) | `infrastructure/stacks/forgejo/` |
| VPN / reverse proxy / OIDC | `infrastructure/stacks/pangolin/` |
| Container orchestration | `infrastructure/stacks/komodo/` |
| OIDC identity provider | `infrastructure/stacks/pocket-id/` |
| Backup / disaster recovery | `infrastructure/stacks/backrest/`, `infrastructure/stacks/vaultwarden/` |
| IaC for cloud | `infrastructure/stacks/pulumi/` (multi-cloud) |
| LLM gateway | `infrastructure/stacks/litellm/` (Postgres) |
| MLX OpenAI-compatible server | `infrastructure/stacks/mlx-omni/` (Apple Silicon) |
| Image generation (SDXL) | `infrastructure/stacks/invokeai/` |
| Data pipeline orchestration | `infrastructure/stacks/dagster/` |
| Reactive Python notebooks | `infrastructure/stacks/marimo/` |
| Database UI | `infrastructure/stacks/bytebase/` |
| VPN tunnel (Gluetun) | `infrastructure/stacks/gluetun/` |
| Real-time voice pipeline | `infrastructure/stacks/pipecat/` |
| In-memory cache (Redis-compatible) | `infrastructure/stacks/dragonfly/` |
| Web crawling API | `infrastructure/stacks/crawl4ai/` |
| Cloud dev environment | `infrastructure/stacks/coder/` |
| Workflow automation | `infrastructure/stacks/windmill/`, `infrastructure/stacks/n8n/` |
| MCP server manager | `infrastructure/stacks/MCPJungle/` |
| Dev documentation UI | `infrastructure/stacks/DevDocs/` |
| Network diagnostic toolbox | `infrastructure/stacks/networking-toolbox/` |
| Knowledge graph (Cognee) | `infrastructure/stacks/cognee/` |
| Temporal knowledge graph (Graphiti) | `infrastructure/stacks/graphiti/` |
| LLM observability (Langfuse) | `infrastructure/stacks/langfuse/` |
| Vector search | `infrastructure/stacks/qdrant/`, `infrastructure/stacks/lancedb/` |
| Graph database | `infrastructure/stacks/memgraph/`, `infrastructure/stacks/falkordb/` |
| ML experiment tracking | `infrastructure/stacks/mlflow/` |
| Pydantic Python tracing | `infrastructure/stacks/logfire/` |
| Streaming SQL | `infrastructure/stacks/risingwave/` |
| Document AI / OCR | `infrastructure/stacks/docling-serve/`, `infrastructure/stacks/olmocr/` |
| Iceberg catalog UI | `infrastructure/stacks/nimtable/` |
| MongoDB → Iceberg CDC | `infrastructure/stacks/olake/` |
| LLM eval/observability | `infrastructure/stacks/lmnr/` |
| Unstructured data extraction | `infrastructure/stacks/unstract/` |
| Private search engine | `infrastructure/stacks/searxng/` |
| Bookmark manager | `infrastructure/stacks/karakeep/` |
| SSH/Terminal in browser | `infrastructure/stacks/Termix/` |
| Document scanning | `infrastructure/stacks/paperless-ngx/` |
| IT admin toolbox | `infrastructure/stacks/it-tools/` |
| Self-hosted audiobooks | `infrastructure/stacks/audiobookshelf/` |
| Kanban + Gantt | `infrastructure/stacks/vikunja/` |
| Web analytics | `infrastructure/stacks/rybbit/` |
| Comic library | `infrastructure/stacks/Kapowarr/` |
| Email server | `infrastructure/stacks/mailcow-dockerized/` |
| Budget tracker | `infrastructure/stacks/actual/` |
| Slide presentations | `infrastructure/stacks/presenton/` |
| Paste sharing | `infrastructure/stacks/pastemax/` |

## Standard Stack Structure

Every stack under `infrastructure/stacks/<name>/` SHALL follow
the 6-file GOLD_STANDARD pattern. See `infrastructure/GOLD_STANDARD.md`
for the full template and exemplars.

```
stacks/<name>/
├── compose.yaml           # Docker service definitions (health checks, restart, volumes, network)
├── pangolin.yaml          # Traefik routing + TinyAuth (if web-facing)
├── sidecar.yaml           # Locket container for Infisical injection
├── secrets.env            # Infisical URI references (committed, no plaintext)
├── blueprint.yaml         # Komodo resource sync definition
└── .env.example           # Local-dev placeholder env vars
```

## Operational Workflows

```bash
# Bring up a single stack
cd infrastructure/stacks/<name>
docker compose -f compose.yaml -f sidecar.yaml up -d

# Tail logs
docker compose logs -f

# Tear down
docker compose down

# Validate all 94 stacks against the GOLD_STANDARD
bun run validate-stacks
```

The `validate-stacks` turbo task is the `stack-doctor` audit that checks
each stack has the 6 GOLD_STANDARD files and follows the
`pangolin.private-resources.<name>.*` 6-label pattern (see
`.agents/skills/stack-ops/SKILL.md`).

## Critical Path

Not all stacks are equal. The 6-stack critical path on the data
platform side is:

```
Infisical -> Garage (garage) -> Lakehouse (lakehouse)
  -> LiteLLM (litellm) -> Langfuse (langfuse)
  -> Cognee (cognee)
```

These six must exist (in that order) before any data pipeline can run.
See `infrastructure/README.md` § "Critical Path" for the full sequence.

## Related Documentation

- `infrastructure/README.md` — 10-step bring-up, 94-stack flat view, control plane pipeline
- `infrastructure/AGENTS.md` — agent instructions for working with stacks (canonical inventory)
- `infrastructure/GOLD_STANDARD.md` — 6-file template + exemplars
- `infrastructure/QUADRANT-TO-STACK-MAP.md` — quadrant → stack routing
- `.agents/skills/stack-ops/SKILL.md` — operational skill for adding/fixing stacks
- `infrastructure/komodo/procedures/` — Komodo GitOps procedures (8 for croilar, 5+ for others)
- `infrastructure/dagger/` — Dagger CI/CD modules
