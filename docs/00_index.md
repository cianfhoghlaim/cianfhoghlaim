---
title: 'Cianfhoghlaim Documentation Index'
domain: 'standards'
status: 'stable'
description: 'Master routing table for all canonical documentation. Read first.'
read_when:
  - starting any task in this codebase
  - looking for documentation on a specific topic
  - unsure which doc to read
last_reviewed: '2026-06-13'
ccc_query_hints:
  - cianfhoghlaim documentation index
  - which doc to read
---

# Cianfhoghlaim Documentation Index

> **1,834 source files consolidated into 7 canonical domains + 1 deploy-plans directory.**
> Every canonical file carries Cognee-clean frontmatter (`entities`,
> `related_skills`, `ccc_query_hints`, `supersedes`). Merged originals
> live in `docs/archive/2026-06-06-*` (and the 2026-06-13 cleanup
> deletes that archive since everything has been merged — see
> `docs/00-core/CLAUDE.md` §PROJECT_IDENTITY).

## 1. Quadrant map (5 top-level + 8 workspace members)

| Path | Quadrant | Purpose | uv workspace |
|---|---|---|---|
| `oideachais/` | **Data lakehouse** | Dagster + DLT + DuckLake + LanceDB + Cognee + CocoIndex | member |
| `tuatha/` | **Celtic MMO consumer** | FastAPI + Axum + Babylon.js + Crypteolas + x402 | member (+ 3 sub: codeolas, crypteolas, apps/crypteolas_demo) |
| `croilar/` | **Multi-persona portfolio** | TanStack + Hono + Convex + BetterAuth | member |
| `meaisínfhoghlaim/` | **AI/ML quadrant** | agents, OCR, Celtic language data, ML pipelines, evaluation, quality, catalog | member (adopted 2026-06-13) |
| `infrastructure/` | **Deploy** | Pangolin, Komodo, Forgejo, Infisical, Ansible, Pulumi, browser stack | member (+ 1 sub: browser) |

For project identity, see [`docs/00-core/CLAUDE.md`](00-core/CLAUDE.md).

## 2. Routing table — "I want to…, where do I go?"

| When you need to… | Read this | Domain |
|---|---|---|
| Understand the project identity / quadrant map | [Project Identity](00-core/CLAUDE.md) | `core` |
| See the critical constraints | [Constraints](00-core/CONSTRAINTS.md) | `core` |
| Set up a package workspace | [CLAUDE.md §Quadrant map](00-core/CLAUDE.md) | `core` |
| Add or audit a Docker Compose stack | `infrastructure/AGENTS.md` + `infrastructure/stacks/*` | `infrastructure` |
| Configure secrets (Infisical, Locket, mise) | `infrastructure/SECRETS-MANAGEMENT.md` | `infrastructure` |
| Deploy via Komodo GitOps | `infrastructure/komodo/` + `docs/01-platform-architecture/komodo-gitops.md` | `architecture` |
| Configure Pangolin networking / VPN / Traefik | `infrastructure/PANGOLIN-SETUP.md` | `architecture` |
| Design the data lakehouse architecture | [Data Architecture](02-data-platform/data-architecture.md) | `data_platform` |
| Understand the DuckLake / MotherDuck / Iceberg mental model | [Storage Mental Model](02-data-platform/storage-mental-model.md) | `data_platform` |
| Find the cross-domain asset-key contract | [Cross-Domain Registry](02-data-platform/cross-domain-registry.md) | `data_platform` |
| Write Dagster assets, sensors, schedules | [Dagster Orchestration](02-data-platform/dagster-orchestration.md) | `data_platform` |
| Write DLT pipelines (filesystem or REST API) | [DLT Pipelines](02-data-platform/dlt-pipelines.md) | `data_platform` |
| Use BAML / CocoIndex / Cognee / ccc | [LLM Stack Hierarchy](04-ai-ml/llm-stack-hierarchy.md) | `ai_ml` |
| Set up OCR / HTR for documents | `oideachais/ocr/README.md` | `ai_ml` |
| Evaluate or improve RAG quality | `docs/04-ai-ml/rag-evaluation.md` | `ai_ml` |
| Build or consume an agent framework | [Browser Automation](03-agents/browser-automation.md) | `agents` |
| Set up browser automation / scraping | [Browser Automation](03-agents/browser-automation.md) | `agents` |
| Build or consume an MCP server | `docs/03-agents/mcp-servers.md` | `agents` |
| Work with Celtic language AI (Irish, Welsh, Gaelic) | `docs/05-celtic-language/` | `celtic_language` |
| Configure Convex + Hono + BetterAuth | [Convex, Hono & Auth](05-web/convex-hono-auth.md) | `web` |
| Build UI components / design system | `docs/05-web/ui-components.md` | `web` |
| Front-end topology (which stack consumes which data plane) | [Front-end Topology](05-web/frontend-topology.md) | `web` |
| Design the Celtic MMO game | `docs/06-product/celtic-mmo.md` | `product` |
| Integrate crypto payments / Web3 | `docs/06-product/crypteolas.md` | `product` |
| Develop the game engine (Godot, wgpu) | `docs/06-product/game-development.md` | `product` |
| Design the educational platform experience | `docs/06-product/educational-platform.md` | `product` |
| Follow coding conventions and standards | [Project Conventions](07-standards/project-conventions.md) | `standards` |
| Set up observability (Datadog, MLflow, Langfuse) | [Observability Patterns](07-standards/observability-patterns.md) | `standards` |
| Start a deferred roadmap (tangent 1-5) | [`docs/00-deploy-plans/`](00-deploy-plans/STATUS.md) | `deploy_plans` |

## 3. Documents by domain

### 3.1 `00-core/` (3 active)
- [CLAUDE.md](00-core/CLAUDE.md) — project identity, quadrant map, constraints
- [CONSTRAINTS.md](00-core/CONSTRAINTS.md) — mandatory database + embedding rules
- `00-core/oideachas-pipeline.md`, `00-core/graphiti.md` — historical skill descriptions (kept for skill discovery)

### 3.2 `01-platform-architecture/` (16)
Pangolin, Komodo, Hon
o, Forgejo, Cloudflare, infrastructure stacks. The most cross-cutting
docs; these describe the *runtime* that everything else runs on.

### 3.3 `01-patterns/` (9)
Actionable pattern files used by agents at runtime (BAML, DAG, dagster,
dlt, embeddings, data pipeline, etc.). These are the files the agent
skill loader reads first.

### 3.4 `01-cognee/` (12)
Cognee integration reference. The `COGNEE_INTEGRATION.md` is the
authoritative setup doc.

### 3.5 `02-architecture/` (11)
High-level architecture: oideachais, tuatha, Aleyum portfolio, MMO,
document processing, multi-agent implementation. All rewritten this
round to use the post-restructure quadrant map.

### 3.6 `02-audit/` (6)
Audits from the 2026-06-06 restructure (cocoindex readiness, cognee
readiness, agent-skill consumability, consolidation plan, discovery
inventory). Kept for traceability of decisions.

### 3.7 `02-data-platform/` (13)
The 13 canonical data-platform docs. Most-load-bearing: `data-architecture.md`,
`dlt-pipelines.md`, `dagster-orchestration.md`, plus the 7 new docs
added this round (storage-mental-model, cross-domain-registry, llm-stack-hierarchy,
browser-automation, change-detection, frontend-topology, deploy-plans/STATUS).

### 3.8 `03-agents/` (54)
The biggest non-archived subdir. Agent framework references (Agno, ADK,
CopilotKit, A2UI), browser automation, MCP servers, multi-agent
implementations. The most useful: `browser-automation.md` (this
round's rewrite) and `change-detection.md` (new).

### 3.9 `03-pipelines/` (1 md + 7 py snippets)
The `AI_ML_PIPELINE.md` plus code snippets (ag_ui_protocol.py,
api_main.py, curriculum_embedding.py, dagster_definitions.py, etc.).
Mixed; probably belongs in `02-data-platform/` or `08-examples/`.

### 3.10 `04-ai-ml/` (20)
Fine-tuning (Unsloth, LoRA/QLoRA), OCR/HTR, knowledge graphs, RAG
evaluation, vector embeddings, celtic-language AI.

### 3.11 `05-celtic-language/` (8)
Bilingual education (en/ga), Helsinki OPUS-MT, Celtic AI resources.

### 3.12 `05-web/` (6)
Front-end stack + topology. The `frontend-topology.md` (this round)
is the new authoritative map.

### 3.13 `06-infrastructure/` (190)
The largest. Contains stack-specific docs and many PDFs. The 1.1G of
data is dominated by:
- `KOMODO_COMPLETE_GUIDE.md` and the Komodo stack docs
- `SECRETS MANAGEMENT_GUIDE.md`
- `agentic-scraping-architecture.md`
- `infrastructure-knowledge-graph.md`
- many stack-specific deployment guides

### 3.14 `06-product/` (8)
BabylonJS, Celtic MMO, Crypteolas, educational platform, game
development.

### 3.15 `07-standards/` (2)
Project conventions + observability patterns. The two highest-value
docs in the canonical tree.

### 3.16 `07-skills/` (12)
Skill descriptions mirroring the agent skills in `.agents/skills/`.

### 3.17 `08-examples/` (8)
Code examples (BAML extraction, model finetuning, data architecture,
frontend stack, implementation guide, BEADS TRACKER).

### 3.18 `00-deploy-plans/` (NEW this round)
The 5 deferred roadmap tangents, each rewritten from the 50-line
research fragment into a ~300-line deploy plan. See
[`00-deploy-plans/STATUS.md`](00-deploy-plans/STATUS.md).

## 4. Skill-to-Doc map (curated subset)

| Agent skill | Primary doc |
|---|---|
| `dagster` | [02-data-platform/dagster-orchestration.md](02-data-platform/dagster-orchestration.md) |
| `dlt` | [02-data-platform/dlt-pipelines.md](02-data-platform/dlt-pipelines.md) |
| `motherduck` | [02-data-platform/storage-mental-model.md](02-data-platform/storage-mental-model.md) |
| `duckdb` / `ducklake` | [02-data-platform/data-architecture.md](02-data-platform/data-architecture.md) |
| `lancedb` | [02-data-platform/data-architecture.md](02-data-platform/data-architecture.md) |
| `cognee` | [01-cognee/COGNEE_INTEGRATION.md](01-cognee/COGNEE_INTEGRATION.md) |
| `graphiti-core` | [04-ai-ml/knowledge-graphs.md](04-ai-ml/knowledge-graphs.md) |
| `baml` | [01-patterns/BAML.md](01-patterns/BAML.md) + [04-ai-ml/llm-stack-hierarchy.md](04-ai-ml/llm-stack-hierarchy.md) |
| `cocoindex` | `docs/cocoindex/` (library) + the canonical embedding patterns in [02-data-platform/dagster-orchestration.md](02-data-platform/dagster-orchestration.md) |
| `ccc` (cocoindex-code) | [04-ai-ml/llm-stack-hierarchy.md §ccc](04-ai-ml/llm-stack-hierarchy.md) |
| `browser` / `browserbase-cli` / `firecrawl` | [03-agents/browser-automation.md](03-agents/browser-automation.md) |
| `agno` | [03-agents/agent-frameworks.md](03-agents/agent-frameworks.md) |
| `google-adk` | [03-agents/agent-frameworks.md](03-agents/agent-frameworks.md) |
| `mcp-builder` | [03-agents/mcp-servers.md](03-agents/mcp-servers.md) |
| `unsloth` | [04-ai-ml/fine-tuning-guide.md](04-ai-ml/fine-tuning-guide.md) |
| `ragas` | [04-ai-ml/rag-evaluation.md](04-ai-ml/rag-evaluation.md) |
| `langfuse` | [07-standards/observability-patterns.md](07-standards/observability-patterns.md) |
| `mlflow` | [07-standards/observability-patterns.md](07-standards/observability-patterns.md) |
| `irish-edtech` | [05-celtic-language/](05-celtic-language/) |
| `document-intelligence` | [04-ai-ml/ocr-htr.md](04-ai-ml/ocr-htr.md) |
| `tanstack-start` | [05-web/frontend-stack.md](05-web/frontend-stack.md) |
| `hono` | [05-web/convex-hono-auth.md](05-web/convex-hono-auth.md) |
| `convex` | [05-web/convex-hono-auth.md](05-web/convex-hono-auth.md) |
| `pulumi` | `infrastructure/pulumi/` + [01-platform-architecture/komodo-gitops.md](01-platform-architecture/komodo-gitops.md) |
| `pangolin` | [01-platform-architecture/pangolin-networking.md](01-platform-architecture/pangolin-networking.md) |
| `komodo` | [01-platform-architecture/komodo-gitops.md](01-platform-architecture/komodo-gitops.md) |
| `dagger` | [01-platform-architecture/monorepo-strategy.md](01-platform-architecture/monorepo-strategy.md) |
| `stack-ops` | [01-platform-architecture/infrastructure-stacks.md](01-platform-architecture/infrastructure-stacks.md) |
| `infisical` | [01-platform-architecture/secrets-management.md](01-platform-architecture/secrets-management.md) |

## 5. OpenSpec workflow

- **`openspec/changes/`** — proposed work. `openspec validate <id> --strict`; `openspec archive <id> --yes` after deploy.
- **`openspec/specs/`** — 32 canonical capability specs. Each spec needs ≥ 1 Requirement + ≥ 1 Scenario.
- **`openspec/plans/`** — research artefacts and deferred roadmaps. `STATUS.md` index lists `status: research | deferred` per file.
- **`docs/00-deploy-plans/`** — concrete deployment plans derived from the consolidated docs. `STATUS.md` index.

## 6. What's NOT in the canonical tree (and where to find it)

These are **reference libraries** — research + scraped-upstream content. Not part of the canonical 7-domain tree, but useful for development context. Each has its own README pointing to the canonical counterpart.

- `docs/lance/` — LanceDB reference (18M, 14 example apps in `examples/`, 4 strategic docs at root, 1 PDF). See [README](lance/README.md).
- `docs/web/` — Web architecture library (3.1M, 98 .md reorganized into 10 topical subdirs). See [README](web/README.md).
- `docs/dlt/` — dlt (Data Load Tool) library (10M, 25 .md + 3 example subdirs). See [README](dlt/README.md).
- `docs/cocoindex/` — CocoIndex library (28M, 21 example subdirs + best-practices summary + cocoindex-code-mcp-server/ as reference). See [README](cocoindex/README.md) and [Best Practices](cocoindex/cocoindex-best-practices.md).
- `docs/dagster/` — Dagster library (5.4M after dedup, 27 root .md + 7 integration subdirs). See [README](dagster/README.md).
- `docs/baml/` — 4 date-coded BAML project snapshots (3.6M). Per "h skip baml" decision, not yet consolidated.
- `docs/notebooks/` — 343 Jupyter notebooks organised by snakecase topic (95M). See [README](notebooks/README.md).
- `docs/marimo/` — Marimo reference (2.6M after upstream mirror move). See [README](marimo/README.md).
- `docs/08-mirrors/` — 2 upstream mirrors: `marimo/` (169MB, 3,641 files) + `marimo-docs/` (6.2MB).

- `docs/tuatha/` — Celtic MMO + Cianfhoghlaim stack reference (consolidated 2026-06-13; 8 topical subdirs).
- `docs/hackathons/`, `docs/hmgcc/`, `docs/docs_examples_consolidated/`, `docs/08-screenshots/` — **example / archive** material. Not part of the canonical tree.
- `docs/archive/2026-06-06-*` — **deleted** (480 files, 101M). All content is in the canonical 7-domain tree.

## 7. Supersedes

- `docs/CLAUDE.md` (root, the old AGENTS.md)
- `docs/00-core/CLAUDE.md` (prior version, this round's rewrite)
- All of `docs/archive/2026-06-06-*` (per the 2026-06-06 consolidation)
- `openspec/plans/tangent_1_micro_credentials.md` etc. (moved to `docs/00-deploy-plans/`)
