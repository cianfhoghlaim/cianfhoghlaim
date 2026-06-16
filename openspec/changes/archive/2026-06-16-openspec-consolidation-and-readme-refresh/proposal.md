# OpenSpec Consolidation & README/AGENTS.md Refresh

## Why

The Cianfhoghlaim monorepo has grown to **44 capability specs** (5,337 lines) covering 4 quadrants + infrastructure + tooling. A deep audit reveals substantial redundancy and staleness:

1. **11 spec pairs are pure duplication** (e.g. `infrastructure/` vs `infrastructure-stacks/`; 6 separate `dagger-*` specs each describe a single sub-module; 3 separate `croilar-*` tiny specs that should be sections of bigger ones).
2. **5 specs are generic-tooling theory** (393-441 lines each, duplicating the corresponding `.agents/skills/{dagster,dlt,memory,observability}/SKILL.md` content). The skills are the source of truth; the specs should be 1-paragraph capability pointers.
3. **2 specs describe capabilities that were never built** (`site-analysis-mcp`, `domain-source-registry`, both from the archived `lateralise-british-isles-domains` change; will be re-proposed as `data-platform-source-registry` when there's bandwidth).
4. **1 quadrant is undocumented in openspec** — `meaisinfhoghlaim/` is a real, mature top-level uv-workspace member (15K+ LOC, 10 sub-packages, 4 heartbeat dagster assets, registered in root `dg.toml`) but has **zero openspec specs** describing it.
5. **3 quadrants have no `AGENTS.md`** — `oideachais/`, `tuatha/`, `croilar/` all have `README.md` but lack the developer-quick-reference files that `meaisinfhoghlaim/AGENTS.md` already has. Only the root `AGENTS.md` and the meaisín `AGENTS.md` exist.
6. **14 in-flight changes** with **0/N tasks** for >4h (some >12d); 4 are clearly superseded by other changes that already landed.

This change **consolidates** the 44 specs into **26** (41% smaller), **adds the missing meaisinfhoghlaim** group, **adds the 3 missing `AGENTS.md`** files, **refreshes** the 4 quadrant READMEs and the root `openspec/AGENTS.md` / `project.md`, and **archives** the 4 stale in-flight changes.

## What Changes

### 1. Spec consolidation (44 → 26)

| Action | Spec | Reason |
|:--|:--|:--|
| **KEEP** (canonical, well-scoped) | `oideachais-pipeline` | 226-line canonical spec for the lakehouse |
| **KEEP** | `oideachais-leabharlann` (new) | 1 of 7 in Group 1 — see §1.1 |
| **KEEP** | `oideachais-baml-schemas` (new) | absorbs `assessment-extraction` + `bilingual-content` + `author-archive-baml-extraction` |
| **KEEP** | `oideachais-cognify-knowledge-graph` (new) | absorbs `knowledge-graph` + `leabharlann-cognify-and-cross-archive-edges` |
| **KEEP** | `oideachais-semantic-search` (renamed from `semantic-search`) | 122 lines, well-scoped |
| **KEEP** | `oideachais-marimo-dashboards` (new) | absorbs `leabharlann-full-stack-demo` |
| **KEEP** | `ireland-primary-jc-dlt-baml` | 74 lines, recent |
| **KEEP** | `croilar-portfolio` (86 lines) | canonical |
| **KEEP** | `croilar-data-engineering` (81 lines) | canonical |
| **KEEP** | `croilar-cv-extraction` (77 lines) | canonical |
| **KEEP** | `tuatha-platform` (new) | first spec for the MMO + crypto quadrant |
| **KEEP** | `meaisinfhoghlaim-platform` (new) | first spec for the AI/ML quadrant (Phase 0.2 of `lateralise-british-isles-domains`) |
| **KEEP** | `meaisinfhoghlaim-agent-frameworks` (new) | the 12 specialised agents |
| **KEEP** | `meaisinfhoghlaim-ocr-htr` (new) | the 10 OCR models across 6 backends |
| **KEEP** | `agent-memory-systems` (renamed from `memory-systems`) | shrunk to 1 req pointing at skills |
| **KEEP** | `agent-observability` (renamed from `observability`) | shrunk to 1 req pointing at skills |
| **KEEP** | `agentic-frontend-frameworks` (renamed from `frontend-frameworks`) | shrunk to 1 req pointing at skills |
| **KEEP** | `dagger-pipelines` (new, consolidated) | absorbs `dagger-ci` + `dagger-forgejo` + `dagger-komodo` + `dagger-cloudflare` + `dagger-gitops` |
| **KEEP** | `infrastructure-stacks` (249 lines) | canonical; absorbs `infrastructure/` + `stack-audit` |
| **KEEP** | `data-engineering-pipeline-documentation` (98 lines) | canonical; the new STATUS.md / REFACTORING.md surface |
| **KEEP** | `workflow-automation` (98 lines) | n8n |
| **KEEP** | `task-management` (68 lines) | Vikunja |
| **KEEP** | `scheduling` (91 lines) | cal-diy |
| **KEEP** | `chunkhound-code-search` (123 lines) | code search |
| **KEEP** | `documentation` (152 lines) | docs/ taxonomy |
| **DELETE** | `data-pipeline` (393 lines) | generic Dagster/DLT theory; covered by skills + `oideachais-pipeline` |
| **DELETE** | `curriculum-ingestion` (59 lines) | subsumed by `oideachais-pipeline` |
| **DELETE** | `site-analysis-mcp` (68 lines) | never landed; will re-propose as `data-platform-source-registry` later |
| **DELETE** | `domain-source-registry` (74 lines) | same as above |
| **DELETE** | `stack-audit` (74 lines) | subsumed by `infrastructure-stacks` |
| **DELETE** | `croilar-self-hosted-portal` (52 lines) | merged into `croilar-portfolio` |
| **DELETE** | `croilar-gradio-hf-demo` (67 lines) | merged into `croilar-data-engineering` |
| **DELETE** | `croilar-persona-registry` (33 lines) | merged into `croilar-data-engineering` |
| **DELETE** | `infrastructure` (143 lines) | merged into `infrastructure-stacks` |
| **DELETE** | `dagger-blockchain` (113 lines) | deferred per `project.md` |
| **DELETE** | `dagger-ci` (93 lines) | section in `dagger-pipelines` |
| **DELETE** | `dagger-forgejo` (104 lines) | section in `dagger-pipelines` |
| **DELETE** | `dagger-komodo` (119 lines) | section in `dagger-pipelines` |
| **DELETE** | `dagger-cloudflare` (83 lines) | section in `dagger-pipelines` |
| **DELETE** | `dagger-gitops` (99 lines) | section in `dagger-pipelines` |
| **DELETE** | `agent-frameworks` (253 lines) | merged into `agentic-frontend-frameworks` |
| **DELETE** | `memory-systems` (419 lines) | renamed to `agent-memory-systems` (shrunk) |
| **DELETE** | `observability` (441 lines) | renamed to `agent-observability` (shrunk) |
| **DELETE** | `frontend-frameworks` (436 lines) | renamed to `agentic-frontend-frameworks` (shrunk) |
| **DELETE** | `semantic-search` (122 lines) | renamed to `oideachais-semantic-search` |
| **DELETE** | `leabharlann-ingestion` (110 lines) | merged into `oideachais-leabharlann` |
| **DELETE** | `leabharlann-full-stack-demo` (51 lines) | merged into `oideachais-marimo-dashboards` |
| **DELETE** | `leabharlann-cognify-and-cross-archive-edges` (36 lines) | merged into `oideachais-cognify-knowledge-graph` |
| **DELETE** | `author-archive-baml-extraction` (103 lines) | merged into `oideachais-baml-schemas` |
| **DELETE** | `ireland-primary-jc-dlt-baml` (74 lines) | superseded by `oideachais-pipeline` post-`ireland-primary-jc-dlt-baml-and-full-stack-demo` archive |
| **DELETE** | `assessment-extraction` (76 lines) | merged into `oideachais-baml-schemas` |
| **DELETE** | `bilingual-content` (77 lines) | merged into `oideachais-baml-schemas` |
| **DELETE** | `knowledge-graph` (133 lines) | merged into `oideachais-cognify-knowledge-graph` |

**Result: 44 → 26 specs (41% smaller), 5,337 → ~3,000 lines (44% smaller).**

### 2. In-flight change cleanup (14 → 9, 4 archived)

Archive (work has landed elsewhere or was never started):

- `author-archive-gemini-and-uos-ingestion` — superseded by `leabharlann-cocoindex-v1` + `leabharlann-cognify-and-cross-archive-edges` (both already archived).
- `cianfhoghlaim-oideachais-baml-first` — the BAML files exist; the dlt sources for Primary + JC are landing in `ireland-primary-jc-dlt-baml-and-full-stack-demo`.
- `state-of-art-5-workspaces` — 0/82 tasks for 10d; never started. The croilar changes (`croilar-portfolio`, `croilar-revitalisation`, `croilar-devtools-hub`, `croilar-personas-to-streams`) cover the same ground.
- `team-workflow-stack` — already complete per `openspec list`; ensure archived.

### 3. README/AGENTS.md refresh (12 files)

| File | Action |
|:--|:--|
| `openspec/AGENTS.md` | **rewrite** — flat 26-row capability table; 4-quadrant workflow recipe; new "in-flight changes" table |
| `openspec/project.md` | **rewrite** — new 26-capability table; 4 quadrants section; updated in-flight changes table |
| `oideachais/AGENTS.md` | **create** — lakehouse + dlt + BAML + dagster surface; AI/ML services live in `meaisinfhoghlaim/`, the `oideachais/{agents,ocr,memory,graph,knowledge_graph}/` dirs are re-export shims |
| `tuatha/AGENTS.md` | **create** — MMO + crypto scope, SpacetimeDB stack, BAML `ui_components.baml`, the consumer relationship to croilar |
| `croilar/AGENTS.md` | **create** — multi-persona model, 5 subprojects, the 4 openspec specs that govern croilar |
| `oideachais/README.md` | minor refresh — add link to new `oideachais/AGENTS.md` and the 7 oideachais-* openspec specs |
| `tuatha/README.md` | minor refresh — add link to new `tuatha/AGENTS.md` and the `tuatha-platform` spec |
| `croilar/README.md` | minor refresh — add link to new `croilar/AGENTS.md` and the 3 croilar-* specs |
| `meaisinfhoghlaim/README.md` | light refresh — add links to the 3 new meaisinfhoghlaim-* openspec specs |
| `meaisinfhoghlaim/AGENTS.md` | light refresh — add links to the 3 new specs (existing content is excellent) |
| `AGENTS.md` (root) | light refresh — add `meaisinfhoghlaim/` to the workspace table; add `tuatha/AGENTS.md` and `croilar/AGENTS.md` references |
| `docs/00_index.md` | minor refresh — update openspec links to reflect new spec names |

### 4. Re-export shim clarification (in `oideachais/AGENTS.md`)

The `oideachais/AGENTS.md` (new) will document the re-export shim relationship:

- `oideachais/agents/{adk,agno}/` — application-layer agent surfaces (front-end CopilotKit / AG-UI)
- `oideachais/ocr/` — application-layer OCR (handwriting OCR for the leabharlann handwritten_pages resource)
- `oideachais/memory/` — application-layer Cognee + Graphiti wrappers
- `oideachais/graph/` — application-layer FalkorDB / Memgraph clients
- `oideachais/knowledge_graph/` — application-layer `cross_stage_cognify` (the 5-stage curriculum knowledge graph)

These are *not* duplicates of `meaisinfhoghlaim/{agents,ocr,language,alignment,evaluation,quality}/` — they're the application-facing facades that the oideachais dlt + dagster assets import. The actual model layer lives in `meaisinfhoghlaim/`.

## Impact

| Layer | Files | Description |
|:--|:--|:--|
| Specs (new) | `openspec/specs/{oideachais-leabharlann,oideachais-baml-schemas,oideachais-cognify-knowledge-graph,oideachais-marimo-dashboards,tuatha-platform,meaisinfhoghlaim-platform,meaisinfhoghlaim-agent-frameworks,meaisinfhoghlaim-ocr-htr,dagger-pipelines,agent-memory-systems,agent-observability,agentic-frontend-frameworks,oideachais-semantic-search}/spec.md` | 13 new canonical specs (8 new + 5 renamed) |
| Specs (deleted) | 18 spec.md files | merged into the 13 new ones |
| Specs (preserved) | 13 spec.md files | kept as-is (oideachais-pipeline, ireland-primary-jc-dlt-baml, the 3 croilar, infrastructure-stacks, data-engineering-pipeline-documentation, workflow-automation, task-management, scheduling, chunkhound-code-search, documentation) |
| Changes (archived) | 4 in-flight change dirs | see §2 above |
| Docs | `openspec/AGENTS.md` (rewrite), `openspec/project.md` (rewrite) | new content |
| AGENTS.md (new) | `oideachais/AGENTS.md`, `tuatha/AGENTS.md`, `croilar/AGENTS.md` | 3 new files |
| AGENTS.md (refreshed) | `meaisinfhoghlaim/AGENTS.md`, `AGENTS.md` (root) | light refresh |
| README.md (refreshed) | `oideachais/README.md`, `tuatha/README.md`, `croilar/README.md`, `meaisinfhoghlaim/README.md` | light refresh |
| Docs | `docs/00_index.md` | minor refresh |

## Out of scope (deferred)

- Skill consolidation (4 browser skills, 3 scraping skills, 4 graph skills) — defer to a follow-up `openspec-changes/.agents-skills-consolidation` change.
- `data-platform-source-registry` capability — the merged version of `site-analysis-mcp` + `domain-source-registry` — defer to a follow-up when there's bandwidth.
- Phase 2 of the `leabharlann-cognify-and-cross-archive-edges` change (FalkorDB edge-population via `cognee cognify --graph-database-provider=falkordb`) — already out of scope of that change.
