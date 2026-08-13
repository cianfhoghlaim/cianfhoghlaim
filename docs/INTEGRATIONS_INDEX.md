# INTEGRATIONS_INDEX — Legacy `docs/0X-*/` → New Home Router

> **Where did `docs/01-cognee/README.md` go?** The pre-v7
> numbered `docs/0X-*/` directories were absorbed into
> per-area `AGENTS.md` files + per-skill
> `.agents/skills/<skill>/SKILL.md` files + openspec
> specs during the v4 consolidation (2026-06-28), the v7
> flattening (2026-07-17), and the 2026-08-15
> central-registry trilogy. This file maps every legacy
> `docs/0X-*/` topic to its canonical new home.
>
> Added by `openspec/changes/2026-08-13-guides-yml-repair-and-docs-integrations-index-v1/`.

## Why this file exists

Before the v4 → v7 flattening cycles, the Cianfhoghlaim
monorepo organized its docs under 14 numbered directories:

```
docs/01-cognee/                 # Cognee knowledge graph
docs/01-platform-architecture/  # Architecture + secrets + IaC
docs/02-architecture/           # Legacy alias
docs/02-audit/                  # Consolidation + drift audits
docs/02-data-platform/          # Lakehouse + Dagster + DLT
docs/03-agents/                 # Agent frameworks
docs/03-pipelines/              # Pipeline code (.py)
docs/04-ai-ml/                  # Models + OCR + Celtic AI
docs/05-celtic-language/        # Celtic-language AI
docs/05-web/                    # TanStack + Convex + Hono
docs/06-product/                # Oideachais + Tuatha MMO
docs/07-skills/                 # Skill mirrors (now retired)
docs/07-standards/              # Project conventions
docs/08-examples/               # Worked examples
docs/CLAUDE.md                  # Migrated to root AGENTS.md
docs/PROJECT_SPEC.md            # Migrated to openspec/project.md
docs/CONSTRAINTS.md             # Migrated to root AGENTS.md
docs/docs_examples_consolidated/ # Migrated to .agents/skills/_template/
```

After the cycles, **all 14 directories are gone** (only the
legacy `docs/audit/`, `docs/audits/`, `docs/legacy/`,
`docs/plans/`, `docs/research/`, etc. survive — see §2).
The content was absorbed into:

- **Skill files** at `.agents/skills/<skill>/SKILL.md`
  (61 skills, all post-v7 canonical)
- **Per-area AGENTS.md** at the data-platform surface
  (`dlt_sources/AGENTS.md`, `baml_src/AGENTS.md`,
  `cocoindex/AGENTS.md`, `orchestration/AGENTS.md`,
  `meaisinfhoghlaim/README.md`) + the new
  `dlt_sources/DATA_PLATFORM_ROUTER.md` (added
  2026-08-13)
- **OpenSpec specs** at `openspec/specs/<spec>/spec.md`
  (92 specs across 8 groups)
- **CCC guides.yml** at `.cocoindex_code/guides.yml`
  (26 entries, all post-v7 — repaired 2026-08-13)

## §1. The 14 dead `docs/0X-*/` directories → new homes

| Legacy path (pre-v7) | Status | New home |
|:--|:--|:--|
| `docs/01-cognee/README.md` | GONE | `.agents/skills/INDEXING_AND_COGNITION.md` + `.agents/skills/cognee/SKILL.md` |
| `docs/01-cognee/ARCHITECTURE.md` | GONE | `.agents/skills/INDEXING_AND_COGNITION.md` (the consolidated 655-line doc) |
| `docs/01-cognee/COGNEE_INTEGRATION.md` | GONE | `.agents/skills/cognee/SKILL.md` |
| `docs/01-cognee/MCP_SERVERS.md` | GONE | `.agents/skills/INDEXING_AND_COGNITION.md` §3 (the 9 MCP servers) |
| `docs/01-cognee/INGESTION.md` | GONE | `.agents/skills/cognee/SKILL.md` + `scripts/cognee_ingest_*.py` |
| `docs/01-cognee/CCC_INTEGRATION.md` | GONE | `.agents/skills/ccc/SKILL.md` + `.agents/skills/INDEXING_AND_COGNITION.md` §10 |
| `docs/01-cognee/INFRASTRUCTURE.md` | GONE | `bonneagar/AGENTS.md` + `bonneagar/stacks/{cognee,graphiti}/` |
| `docs/01-platform-architecture/platform-overview.md` | GONE | `AGENTS.md` (root) + `bonneagar/AGENTS.md` |
| `docs/01-platform-architecture/monorepo-strategy.md` | GONE | `AGENTS.md` (root) + `.agents/skills/centralized-registry/SKILL.md` |
| `docs/01-platform-architecture/infrastructure-stacks.md` | GONE | `.agents/skills/stacks-sync/SKILL.md` + `openspec/specs/infrastructure-stacks/spec.md` |
| `docs/01-platform-architecture/secrets-management.md` | GONE | `.agents/skills/secrets-management/SKILL.md` |
| `docs/01-platform-architecture/komodo-gitops.md` | GONE | `.agents/skills/komodo/SKILL.md` |
| `docs/01-platform-architecture/pangolin-networking.md` | GONE | `.agents/skills/pangolin/SKILL.md` |
| `docs/02-architecture/EDUCATION_ARCHITECTURE.md` | GONE | `openspec/specs/british-isles-education-pipeline/spec.md` + `agents/meaisinfhoghlaim/AGENTS.md` |
| `docs/02-architecture/OIDEACHAIS_PIPELINE.md` | GONE | `dlt_sources/british_isles/ireland/education/AGENTS.md` (via `dlt_sources/AGENTS.md`) |
| `docs/02-architecture/SRUTH_OVERVIEW.md` | GONE | `AGENTS.md` (the v7 flattening history section) |
| `docs/02-audit/consolidation_plan.md` | GONE | `docs/audits/2026-07-06-drift-audit.md` |
| `docs/02-audit/cocoindex_readiness_audit.md` | GONE | `.cocoindex_code/cocoindex.db` (the 8,845 file / 257,957 chunk index) + `.agents/skills/INDEXING_AND_COGNITION.md` §1 |
| `docs/02-audit/cognee_readiness_audit.md` | GONE | `.agents/skills/cognee/SKILL.md` + `INDEXING_AND_COGNITION.md` §2 (the 7 typed clusters) |
| `docs/02-audit/agent_skill_consumability.md` | GONE | `.agents/skills/INDEXING_AND_COGNITION.md` §8 (the 14-agent + 9-MCP registry) |
| `docs/02-audit/discovery_inventory.md` | GONE | `docs/plans/` (the post-v7 plan inventory) |
| `docs/02-data-platform/data-architecture.md` | GONE | `dlt_sources/DATA_PLATFORM_ROUTER.md` + `dlt_sources/AGENTS.md` |
| `docs/02-data-platform/dagster-orchestration.md` | GONE | `orchestration/AGENTS.md` + `.agents/skills/dagster/SKILL.md` |
| `docs/02-data-platform/dlt-pipelines.md` | GONE | `dlt_sources/AGENTS.md` + `.agents/skills/dlt/SKILL.md` |
| `docs/03-agents/agent-frameworks.md` | GONE | `.agents/skills/agent-fleet-orchestration/SKILL.md` |
| `docs/03-agents/browser-automation.md` | GONE | `.agents/skills/browser-tools/SKILL.md` + `.agents/skills/ag-ui/SKILL.md` |
| `docs/03-agents/mcp-servers.md` | GONE | `.agents/skills/INDEXING_AND_COGNITION.md` §3 (the 9 MCP servers) |
| `docs/03-agents/baml-extraction.md` | GONE | `baml_src/AGENTS.md` + `.agents/skills/baml/SKILL.md` |
| `docs/03-pipelines/dagster_definitions.py` | GONE | `orchestration/definitions.py` + `orchestration/AGENTS.md` |
| `docs/03-pipelines/dagster_factories.py` | GONE | `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py` |
| `docs/03-pipelines/api_main.py` | GONE | `agents/api/` (the Hono API routes) |
| `docs/03-pipelines/curriculum_embedding.py` | GONE | `cocoindex/biep_parity/` + `dlt_sources/DATA_PLATFORM_ROUTER.md` |
| `docs/03-pipelines/storage_init.py` | GONE | `orchestration/storage/` + `dlt_sources/common/destinations_cianfhoghlaim.py` |
| `docs/03-pipelines/observability_init.py` | GONE | `observability/` + `.agents/skills/agent-observability/SKILL.md` |
| `docs/03-pipelines/ag_ui_protocol.py` | GONE | `agents/ag_ui/` + `.agents/skills/ag-ui/SKILL.md` |
| `docs/03-pipelines/durable_orchestrator.py` | GONE | `orchestration/components/` (the 5 KCG components) |
| `docs/04-ai-ml/fine-tuning-guide.md` | GONE | `.agents/skills/unsloth/SKILL.md` + `.agents/skills/huggingface/SKILL.md` |
| `docs/04-ai-ml/ocr-htr.md` | GONE | `.agents/skills/centralized-registry/SKILL.md` §11 (OCR/VLM Pipeline) + `meaisinfhoghlaim/README.md` |
| `docs/04-ai-ml/rag-evaluation.md` | GONE | `.agents/skills/ragas/SKILL.md` + `.agents/skills/agent-observability/SKILL.md` |
| `docs/04-ai-ml/knowledge-graphs.md` | GONE | `.agents/skills/cognee/SKILL.md` + `.agents/skills/graphiti/SKILL.md` |
| `docs/04-ai-ml/vector-embeddings.md` | GONE | `.agents/skills/lancedb/SKILL.md` + `cocoindex/AGENTS.md` |
| `docs/04-ai-ml/celtic-language-ai.md` | GONE | `openspec/specs/celtic-language-pipeline/spec.md` |
| `docs/04-ai-ml/ml-pipelines.md` | GONE | `dlt_sources/DATA_PLATFORM_ROUTER.md` |
| `docs/05-celtic-language/BILINGUAL_EDTECH.md` | GONE | `agents/meaisinfhoghlaim/educational/` + `meaisinfhoghlaim/alignment/` |
| `docs/05-celtic-language/CELTIC_AI_RESOURCES.md` | GONE | `meaisinfhoghlaim/datasets/` + `.agents/skills/huggingface/SKILL.md` |
| `docs/05-celtic-language/LANGUAGE_ARCHITECTURE.md` | GONE | `openspec/specs/celtic-language-pipeline/spec.md` |
| `docs/05-celtic-language/IRISH_HUGGINGFACE.md` | GONE | `meaisinfhoghlaim/alignment/irish_g2p.py` + `.agents/skills/huggingface/SKILL.md` |
| `docs/05-web/frontend-stack.md` | GONE | `.agents/skills/agentic-frontend-frameworks/SKILL.md` + `.agents/skills/tanstack-start/SKILL.md` |
| `docs/05-web/convex-hono-auth.md` | GONE | `.agents/skills/convex/SKILL.md` + `.agents/skills/hono/SKILL.md` + `.agents/skills/better-auth/SKILL.md` |
| `docs/05-web/ui-components.md` | GONE | `web/apps/` (the 7 web apps) + `.agents/skills/copilotkit/SKILL.md` |
| `docs/06-product/educational-platform.md` | GONE | `openspec/specs/british-isles-education-pipeline/spec.md` + `agents/meaisinfhoghlaim/AGENTS.md` |
| `docs/06-product/celtic-mmo.md` | GONE | `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` + `agents/tuatha/AGENTS.md` |
| `docs/06-product/crypteolas.md` | GONE | `agents/tuatha/` (the tuatha monorepo) |
| `docs/06-product/game-development.md` | GONE | `.agents/skills/babylonjs/SKILL.md` + `agents/tuatha/` |
| `docs/07-skills/*.md` (all 9) | GONE | `.agents/skills/<skill>/SKILL.md` (the 61 real skills — no `docs/07-skills/` mirror) |
| `docs/07-standards/project-conventions.md` | GONE | `AGENTS.md` (the "Monorepo Topology" + "Conventions" sections) + `.agents/skills/dignified-python/SKILL.md` |
| `docs/07-standards/observability-patterns.md` | GONE | `.agents/skills/agent-observability/SKILL.md` + `observability/` |
| `docs/08-examples/BEADS TRACKER.md` | GONE | `openspec/AGENTS.md` (the task-tracking convention) + `openspec/project.md` |
| `docs/08-examples/DATA_ARCHITECTURE.md` | GONE | `dlt_sources/DATA_PLATFORM_ROUTER.md` + `dlt_sources/AGENTS.md` |
| `docs/08-examples/FRONTEND_STACK.md` | GONE | `.agents/skills/agentic-frontend-frameworks/SKILL.md` |
| `docs/08-examples/MODEL_FINETUNING.md` | GONE | `.agents/skills/unsloth/SKILL.md` + `.agents/skills/huggingface-llm-trainer/SKILL.md` |
| `docs/08-examples/IMPLEMENTATION_GUIDE.md` | GONE | `openspec/AGENTS.md` §Workflow |
| `docs/08-examples/OIDEACHAIS_SPEC.md` | GONE | `openspec/specs/british-isles-education-pipeline/spec.md` |
| `docs/08-examples/OPENSPEC_AGENTS.md` | GONE | `openspec/AGENTS.md` + `agents/AGENTS.md` |
| `docs/08-examples/SUBJECT_IMPLEMENTATIONS.md` | GONE | `baml_src/british_isles/ireland/education/` + `cocoindex/biep_parity/` |
| `doc/hackathons/build-small-2026-plan.md` | GONE | `docs/research/` + `docs/legacy/cianfhoghlaim-pkg-readme.md` |
| `doc/hackathons/build-small-2026-blog.md` | GONE | `docs/research/` |
| `doc/hackathons/cognee-integration-audit-2026-06-10.md` | GONE | `.agents/skills/cognee/SKILL.md` (the current audit) |
| `docs/CLAUDE.md` | GONE | `AGENTS.md` (root) + `openspec/AGENTS.md` |
| `docs/PROJECT_SPEC.md` | GONE | `openspec/project.md` |
| `docs/CONSTRAINTS.md` | GONE | `AGENTS.md` (the "Critical Rules" sections) |
| `docs/AGENTS.md` | GONE | `AGENTS.md` (root) |
| `docs/docs_examples_consolidated/` | GONE | `.agents/skills/_template/` + `.agents/skills/improve-skills/SKILL.md` |

## §2. The surviving `docs/` subdirectories

Not everything under `docs/` was deleted. The following
subdirectories still hold active content:

| Subdirectory | Contents | Purpose |
|:--|:--|:--|
| `docs/agents/` | 20+ markdown files | Agent transcripts + per-feature agent docs (e.g. `dev-env-demo-transcript.md`, `meaisin-v3-*.md`) |
| `docs/audit/` | 5 files | The 2026-08-15 audit trail (`baml-merger-plan.md`, `dagster-component-migration-plan.md`, `ocr-model-audit.md`, `stacks-deferral-note.md`, `web-app-consolidation-plan.md`) |
| `docs/audits/` | 1 file | The 2026-07-06 drift audit (`2026-07-06-drift-audit.md`) |
| `docs/baml/` | (legacy baml client snapshots) | Old BAML client generations (kept for reference) |
| `docs/biiep-v3/` | 6 files | BIEP v3 quickstart + FAQ + storage layout (the per-subject pipeline docs) |
| `docs/comics/` | (illustrations + research) | Reference comic-book scans |
| `docs/dagster/` | (legacy Dagster docs) | Pre-v7 Dagster definitions |
| `docs/deploy-runbooks/` | 1+ files | The `PHASE_0.3_DEPLOY_RUNBOOK.md` + other deploy procedures |
| `docs/dlthub-ai-workbench/` | (workbench artifacts) | dlthub AI workbench session outputs |
| `docs/email-inbox/` | (inbox snapshots) | Reference email-inbox exports |
| `docs/firecrawl/` | (Firecrawl session outputs) | Firecrawl scrape outputs |
| `docs/lakehouse/` | (lakehouse docs) | Lakehouse architecture diagrams |
| `docs/legacy/` | 1 file | `cianfhoghlaim-pkg-readme.md` (the pre-v7 package README — kept as historical) |
| `docs/observability/` | (observability artifacts) | Langfuse + MLflow session outputs |
| `docs/ops/` | (operational runbooks) | Operational procedures |
| `docs/pangolin-komodo/` | (IaC session outputs) | Pangolin + Komodo stack outputs |
| `docs/plans/` | (planning docs) | Project plans + roadmaps |
| `docs/research/` | (research artifacts) | Research session outputs + paper clippings |
| `docs/stacks/` | (stack session outputs) | Stack deployment outputs |
| `docs/theses/` | (thesis drafts) | Research thesis drafts |
| `docs/ui-inspiration/` | (UI design references) | UI design references |

Plus the surviving top-level files:
- `docs/README.md` — the `docs/` directory's own README
- `docs/RESEARCH_REPORT.md` — the master research report
- `docs/CHOP_AND_CHANGE_GUIDE.md` — the chop-and-change guide
- `docs/p3-skill-mcp-migration-status.md` — the p3 skill/MCP migration status
- `docs/per-subject-pipeline.md` — the per-subject pipeline doc
- `docs/PHASE_0.3_DEPLOY_RUNBOOK.md` — the Phase 0.3 deploy runbook
- `docs/user-guide.md` — the user guide
- `docs/THESES.py` — the theses source file
- `docs/stremio_real_debrid_lower_socioeconomic_moral_piracy_guide.png` — illustration

## §3. Topic-by-topic mapping

For agents searching by topic (not by file path), here's
the canonical mapping:

| Topic | New home |
|:--|:--|
| **Cognee knowledge graph** | `.agents/skills/cognee/SKILL.md` + `.agents/skills/INDEXING_AND_COGNITION.md` §2 |
| **CCC semantic code search** | `.agents/skills/ccc/SKILL.md` + `.agents/skills/INDEXING_AND_COGNITION.md` §1 + §10 |
| **OCR/VLM pipeline** | `.agents/skills/centralized-registry/SKILL.md` §11 + `meaisinfhoghlaim/README.md` |
| **BAML extraction** | `baml_src/AGENTS.md` + `.agents/skills/baml/SKILL.md` + `.agents/skills/baml-schema-sync/SKILL.md` |
| **DLT ingestion** | `dlt_sources/AGENTS.md` + `.agents/skills/dlt/SKILL.md` + `.agents/skills/dlt-sync/SKILL.md` |
| **CocoIndex v1 embedding** | `cocoindex/AGENTS.md` + `.agents/skills/cocoindex/SKILL.md` |
| **Dagster orchestration** | `orchestration/AGENTS.md` + `.agents/skills/dagster/SKILL.md` + `.agents/skills/dagster-asset-sync/SKILL.md` |
| **MotherDuck + DuckLake** | `motherduck/README.md` + `.agents/skills/motherduck/SKILL.md` + `.agents/skills/ducklake/SKILL.md` |
| **LanceDB vector store** | `.agents/skills/lancedb/SKILL.md` |
| **Infisical + Locket secrets** | `.agents/skills/secrets-management/SKILL.md` |
| **Komodo + Pangolin IaC** | `.agents/skills/komodo/SKILL.md` + `.agents/skills/pangolin/SKILL.md` + `.agents/skills/stacks-sync/SKILL.md` |
| **Agent fleet (12-agent)** | `.agents/skills/agent-fleet-orchestration/SKILL.md` + `.agents/skills/agents-sync/SKILL.md` + `agents/AGENTS.md` |
| **Google ADK agents** | `.agents/skills/google-adk/SKILL.md` |
| **Agno team-based research** | `.agents/skills/agno/SKILL.md` |
| **Pydantic AI type-safe agents** | `.agents/skills/pydantic/building-pydantic-ai-agents/SKILL.md` |
| **TanStack Start frontend** | `.agents/skills/tanstack-start/SKILL.md` |
| **Convex realtime backend** | `.agents/skills/convex/SKILL.md` |
| **Hono API gateway** | `.agents/skills/hono/SKILL.md` |
| **Better Auth authentication** | `.agents/skills/better-auth/SKILL.md` |
| **CopilotKit agent UI** | `.agents/skills/copilotkit/skills/copilotkit-develop/SKILL.md` |
| **AG-UI protocol** | `.agents/skills/ag-ui/SKILL.md` |
| **Marimo notebooks** | `.agents/skills/marimo/SKILL.md` + `.agents/skills/notebooks-sync/SKILL.md` |
| **Babylon.js 3D** | `.agents/skills/babylonjs/SKILL.md` |
| **Unsloth fine-tuning** | `.agents/skills/unsloth/SKILL.md` |
| **Hugging Face Hub** | `.agents/skills/huggingface/SKILL.md` |
| **Langfuse + MLflow observability** | `.agents/skills/agent-observability/SKILL.md` + `.agents/skills/langfuse/SKILL.md` + `.agents/skills/mlflow/SKILL.md` |
| **RAGAS evaluation** | `.agents/skills/ragas/SKILL.md` |
| **Graphiti temporal memory** | `.agents/skills/graphiti/SKILL.md` + `.agents/skills/agent-memory-systems/SKILL.md` |
| **FalkorDB graph + vector** | `.agents/skills/falkordb/SKILL.md` |
| **Memgraph production graph** | `.agents/skills/memgraph/SKILL.md` |
| **LiteLLM gateway** | `.agents/skills/litellm/SKILL.md` |
| **Firecrawl web scraping** | `.agents/skills/firecrawl/SKILL.md` + `.agents/skills/browser-tools/SKILL.md` |
| **Cloudflare Workers + Durable Objects** | `.agents/skills/cloudflare/SKILL.md` |
| **Dignified Python standards** | `.agents/skills/dignified-python/SKILL.md` |
| **BIEP v3 (6 LC subjects)** | `openspec/specs/british-isles-education-pipeline/spec.md` + `dlt_sources/DATA_PLATFORM_ROUTER.md` |
| **Irish / Celtic language AI** | `openspec/specs/celtic-language-pipeline/spec.md` + `meaisinfhoghlaim/alignment/` |
| **OpenSpec workflow** | `openspec/AGENTS.md` |

## §4. For agents — quick routing

If you're an agent searching for content and you can't
find it:

1. **Run `bun run ccc:search "<query>"`** — semantic search
   over the entire codebase (8,845 files, 257,957 chunks).
2. **Read `AGENTS.md` (root)** — the canonical agent
   routing surface (priority quick reference, repo
   topology, conventions).
3. **Read `INDEXING_AND_COGNITION.md`** — the CCC + Cognee
   + MCP + agent registry surface.
4. **Read `dlt_sources/DATA_PLATFORM_ROUTER.md`** — if
   your task touches the data platform (DLT, BAML,
   CocoIndex, Dagster, OCR/VLM).
5. **Read `openspec/AGENTS.md`** — if your task involves
   opening a change or modifying a spec.
6. **Read this file (`docs/INTEGRATIONS_INDEX.md`)** — if
   you're looking for content from the pre-v7
   `docs/0X-*/` directories.

## §5. Validation

The `mise run lint:guides-yml` validation gate enforces
that every entry in `.cocoindex_code/guides.yml` points at
real on-disk paths. Run it after any docs restructure to
catch new drift.

## §6. Cross-references

- [`.cocoindex_code/guidesyml`](../.cocoindex_code/guides.yml) — the CCC concept-guide catalog (26 entries, all post-v7)
- [`../AGENTS.md`](../AGENTS.md) — root agent instructions
- [`../openspec/AGENTS.md`](../openspec/AGENTS.md) — openspec workflow
- [`../.agents/skills/INDEXING_AND_COGNITION.md`](../.agents/skills/INDEXING_AND_COGNITION.md) — CCC + Cognee + MCP + agent registry
- [`../dlt_sources/DATA_PLATFORM_ROUTER.md`](../dlt_sources/DATA_PLATFORM_ROUTER.md) — the data platform router
- [`openspec/changes/2026-08-13-skill-consolidation-and-extension-v1/`](../openspec/changes/2026-08-13-skill-consolidation-and-extension-v1/) — Change 1
- [`openspec/changes/2026-08-13-guides-yml-repair-and-docs-integrations-index-v1/`](../openspec/changes/2026-08-13-guides-yml-repair-and-docs-integrations-index-v1/) — this change

---

**Last updated**: 2026-08-13 (initial creation — `openspec/changes/2026-08-13-guides-yml-repair-and-docs-integrations-index-v1/`).
**Owner**: Build agent.