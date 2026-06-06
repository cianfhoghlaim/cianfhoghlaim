# Infrastructure Stacks

Reorganised per Phase 0 (2026-06-04). See `infrastructure/AGENTS.md` for the
categorisation philosophy and `infrastructure/GOLD_STANDARD.md` for the
6-file template that every stack SHALL follow.

## At a Glance

| Category | Stacks | Purpose |
|:--|--:|:--|
| `storage/` | 5 | Foundational substrates (Garage S3, Lakekeeper, LakeFS, Beszel, Forgejo Runner) |
| `infrastructure/` | 12 | Control plane (Pangolin, Komodo, Pocket ID, Forgejo, Backrest, Vaultwarden, Glance, Pulumi, Headscale, Headplane, DNS, Monitoring) |
| `engineering/` | 17 | Gateways + services (LiteLLM, llama-swap, MLX-Omni, InvokeAI, Dagster, Marimo, Bytebase, Gluetun, Pipecat, Dragonfly, Crawl4AI, Coder, Windmill, MCPJungle, DevDocs, N8n, Networking) |
| `machine_learning/` | 16 | AI services (Cognee, Graphiti, Langfuse, LMNR, Olake, Qdrant, Memgraph, FalkorDB, LanceDB, MLflow, Logfire, Nimtable, RisingWave, Docling-Serve, OlmOCR, Unstract) |
| `tools/` | 24 | Productivity + media (SearXNG, Karakeep, Termix, Paperless-NGX, IT-Tools, Audiobookshelf, Vikunja, etc.) |

**Total:** 74 stacks (changes as new ones are added via the stack-ops skill).

## Quick Navigation — "I need a..."

| If you need to... | Look at... |
|:--|:--|
| S3-compatible object storage | `storage/garage/` (local, Hetzner) or Cloudflare R2 adapter |
| Iceberg / DuckLake catalog | `storage/lakehouse/` (Lakekeeper + Lance Namespace + Postgres + Garage) |
| Git-for-data | `storage/lakefs/` |
| Git hosting (self-hosted Forge) | `infrastructure/forgejo/` |
| VPN / reverse proxy / OIDC | `infrastructure/pangolin/` |
| Container orchestration | `infrastructure/komodo/` |
| OIDC identity provider | `infrastructure/pocket-id/` |
| Backup / disaster recovery | `infrastructure/backrest/`, `infrastructure/vaultwarden/` |
| IaC for cloud | `infrastructure/pulumi/` (multi-cloud) |
| Monitoring (Prom + Graf + Loki) | `infrastructure/monitoring/` |
| LLM gateway | `engineering/litellm/` (Postgres + Prometheus) |
| MLX OpenAI-compatible server | `engineering/mlx-omni/` (Apple Silicon) |
| Image generation (SDXL) | `engineering/invokeai/` |
| Data pipeline orchestration | `engineering/dagster/` |
| Reactive Python notebooks | `engineering/marimo/` |
| Database UI | `engineering/bytebase/` |
| VPN tunnel (Gluetun) | `engineering/gluetun/` |
| Real-time voice pipeline | `engineering/pipecat/` |
| In-memory cache (Redis-compatible) | `engineering/dragonfly/` |
| Web crawling API | `engineering/crawl4ai/` |
| Cloud dev environment | `engineering/coder/` |
| Workflow automation | `engineering/windmill/`, `engineering/n8n/` |
| MCP server manager | `engineering/MCPJungle/` |
| Dev documentation UI | `engineering/DevDocs/` |
| Network diagnostic toolbox | `engineering/networking-toolbox/` |
| Knowledge graph (Cognee) | `machine_learning/cognee/` |
| Temporal knowledge graph (Graphiti) | `machine_learning/graphiti/` |
| LLM observability (Langfuse) | `machine_learning/langfuse/` |
| Vector search | `machine_learning/qdrant/`, `machine_learning/lancedb/` |
| Graph database | `machine_learning/memgraph/`, `machine_learning/falkordb/` |
| ML experiment tracking | `machine_learning/mlflow/` |
| Pydantic Python tracing | `machine_learning/logfire/` |
| Streaming SQL | `machine_learning/risingwave/` |
| Document AI / OCR | `machine_learning/docling-serve/`, `machine_learning/olmocr/` |
| Iceberg catalog UI | `machine_learning/nimtable/` |
| MongoDB → Iceberg CDC | `machine_learning/olake/` |
| LLM eval/observability | `machine_learning/lmnr/` |
| Unstructured data extraction | `machine_learning/unstract/` |
| Private search engine | `tools/searxng/` |
| Bookmark manager | `tools/karakeep/` |
| SSH/Terminal in browser | `tools/termix/` |
| Document scanning | `tools/paperless-ngx/` |
| IT admin toolbox | `tools/IT-Tools/` |
| Self-hosted audiobooks | `tools/audiobookshelf/` |
| Kanban + Gantt | `tools/vikunja/` |
| Web analytics | `tools/rybbit/` |
| Comic library | `tools/Kapowarr/` |
| Email server | `tools/mailcow-dockerized/` |
| Budget tracker | `tools/actual/` |
| Slide presentations | `tools/presenton/` |
| Paste sharing | `tools/pastemax/` |

## Standard Stack Structure

Every stack under `infrastructure/stacks/<category>/<name>/` SHALL follow
the 6-file GOLD_STANDARD pattern. See `infrastructure/GOLD_STANDARD.md`
for the full template and exemplars.

```
stacks/<category>/<name>/
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
cd infrastructure/stacks/<category>/<name>
docker compose -f compose.yaml -f sidecar.yaml up -d

# Tail logs
docker compose logs -f

# Tear down
docker compose down

# Validate all 74 stacks against the GOLD_STANDARD
bun run validate-stacks
```

The `validate-stacks` turbo task is the `stack-doctor` audit that checks
each stack has the 6 GOLD_STANDARD files and follows the
`pangolin.private-resources.<name>.*` 6-label pattern (see
`.agents/skills/stack-ops/SKILL.md`).

## Critical Path

Not all stacks are equal. The 88-stack critical path on the data
platform side is:

```
Infisical -> Garage (storage/garage) -> Lakehouse (storage/lakehouse)
  -> LiteLLM (engineering/litellm) -> Langfuse (machine_learning/langfuse)
  -> Cognee (machine_learning/cognee)
```

These six must exist (in that order) before any data pipeline can run.
See `infrastructure/README.md` § "Critical Path" for the full sequence.

## Related Documentation

- `infrastructure/README.md` — 10-step bring-up, 88-stack categorised view, control plane pipeline
- `infrastructure/AGENTS.md` — agent instructions for working with stacks
- `infrastructure/GOLD_STANDARD.md` — 6-file template + exemplars
- `.agents/skills/stack-ops/SKILL.md` — operational skill for adding/fixing stacks
- `infrastructure/komodo/procedures/` — Komodo GitOps procedures (8 for croilar, 5+ for others)
- `infrastructure/dagger/` — Dagger CI/CD modules
