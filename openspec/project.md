# Cianfhoghlaim Project Conventions

## Project Overview

A bilingual (EN/GA) agentic educational platform covering 5 stages of the
Irish education system: Aistear, Primary, Junior Cycle, Senior Cycle, and
Tertiary. Powered by BAML extraction, Cognee + LanceDB + DuckLake
knowledge graph, Agno + Google ADK agents, and a TanStack Start /
CopilotKit AG-UI front-end. The monorepo is a **bun + uv + turbo polyglot
orchestration** of multiple subprojects and 70+ Docker Compose stacks.

## Subprojects (4 top-level quadrants)

| Subproject | Path | Wheel / Workspace | Purpose | README | AGENTS.md |
|:--|:--|:--|:--|:--|:--|
| `oideachais` | `oideachais/` | `oideachais` (uv) | Celtic education data platform (Dagster, DLT, LanceDB) | [README](../oideachais/README.md) | [AGENTS](../oideachais/AGENTS.md) |
| `meaisinfhoghlaim` | `meaisinfhoghlaim/` | `meaisinfhoghlaim` (uv) | AI/ML services (agents, OCR, Celtic-language, ML pipelines) | [README](../meaisinfhoghlaim/README.md) | [AGENTS](../meaisinfhoghlaim/AGENTS.md) |
| `tuatha` | `tuatha/` | `tuath` (uv) | Educational MMO (Babylon.js + Rust + SpacetimeDB) + crypteolas crypto | [README](../tuatha/README.md) | [AGENTS](../tuatha/AGENTS.md) |
| `croilar` | `croilar/` | (bun workspace) | Multi-persona portfolio + CV + data engineering subproject | [README](../croilar/README.md) | [AGENTS](../croilar/AGENTS.md) |

## Capability Areas (25 specs, 8 groups)

### Oideachais Quadrant (7 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `oideachais-pipeline` | Celtic education curriculum pipeline (Dagster + DLT + DuckLake + LanceDB + BAML, 5 stages) | Active |
| `oideachais-leabharlann` | 4 dlt sources (books, zotero, takeout, UoG) + 3 v1 CocoIndex Apps + 7 Dagster assets + full-stack demo | Active |
| `oideachais-baml-schemas` | 9 BAML files + 3 extraction clients (ExtractEn, ExtractEnStrong, LocalVision) | Active |
| `oideachais-cognify-knowledge-graph` | 5-stage cross-stage cognify + 3 leabharlann cognify datasets + 3 cross-archive FalkorDB edge types | Active |
| `oideachais-semantic-search` | Cross-corpus LanceDB HNSW search (BGE-M3 multilingual + BGE-large-en-v1.5 English) | Active |
| `oideachais-marimo-dashboards` | 11 Marimo notebooks (5 educational stages + cross-domain + ducklake + lakehouse + leabharlann full-stack demo) | Active |
| `ireland-primary-jc-dlt-baml` | Ireland Primary + Junior Cycle dlt + BAML loop (the recent `ireland-primary-jc-dlt-baml-and-full-stack-demo` change) | Active |

### Meaisínfhoghlaim Quadrant (3 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `meaisinfhoghlaim-platform` | 10 sub-packages + 4 heartbeat dagster assets + Dagster code-location | Active |
| `meaisinfhoghlaim-agent-frameworks` | 12 specialised agents (Root, Curriculum, Translation, Corpus, Geospatial, Statistics, Research, etc.) | Active |
| `meaisinfhoghlaim-ocr-htr` | 10 OCR models across 6 backends (Pylaia, TrOCR, PaddleOCR, Tesseract, dots.ocr, VLM) | Active |

### Tuatha Quadrant (1 spec)

| Capability | Description | Status |
|:--|:--|:--|
| `tuatha-platform` | Celtic educational MMO (Babylon.js + Rust + SpacetimeDB) + crypteolas crypto + BAML UI/image extraction | Active |

### Croílár Quadrant (3 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `croilar-portfolio` | Public TanStack Start site — multi-persona (aleyum, cianfhoghlaim, carlcashman) | Active |
| `croilar-data-engineering` | Dagster + DLT + CocoIndex + BAML pipelines for the croilar personas | Active |
| `croilar-cv-extraction` | BAML extraction of the author's CV / achievements / teaching PDFs | Active |

### Agent + Observability + Frontend (4 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `agent-memory-systems` | Cognee + Graphiti + LanceDB + FalkorDB + Memgraph agent memory (renamed from `memory-systems`) | Active |
| `agent-observability` | Langfuse + MLflow + RAGAS + Logfire + Datadog (renamed from `observability`) | Active |
| `agentic-frontend-frameworks` | TanStack Start + CopilotKit + AG-UI + Hono + Convex (renamed from `frontend-frameworks`, merged `agent-frameworks`) | Active |
| `dagger-pipelines` | Polyglot CI/CD via Dagger (Python + TS) — 5 separate `dagger-*` specs merged into 1 (8-step GitOps) | Active |

### Infrastructure + Tooling (4 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `infrastructure-stacks` | 70+ Docker Compose stacks + stack-doctor.sh + Pangolin + Infisical + Locket (absorbed `infrastructure` + `stack-audit`) | Active |
| `data-engineering-pipeline-documentation` | `oideachais/STATUS.md` + `oideachais/REFACTORING.md` + per-area READMEs (the new doc surface from this change) | Active |
| `chunkhound-code-search` | Semantic code search with MVCC | Active |
| `documentation` | Canonical `docs/` structure (8 numbered domains), frontmatter schema, Cognee ingestion | Active |

### Team Workflow (3 specs)

| Capability | Description | Status |
|:--|:--|:--|
| `workflow-automation` | n8n + LLM pipelines (OpenCode Go API) | Active |
| `task-management` | Vikunja kanban + Gantt + list + team sharing | Active |
| `scheduling` | cal-diy team + per-member booking pages | Active |

## Conventions

All specs MUST respect constraints from `docs/context/00-core/CONSTRAINTS.md`:

1. **Database:** Single-threaded DuckDB, MVCC LanceDB
2. **Embeddings:** Batch minimum 100 texts
3. **Irish language:** Use specialized models (UCCIX, GaBERT)
4. **BAML:** Schema validation required for LLM extraction
5. **Secrets:** Infisical is the source of truth; Locket injects at runtime; never commit `.env`
6. **Image registry:** `ghcr.io/cianfhoghlaim/`, pinned to `<major>.<minor>.<patch>`, never `:latest`
7. **Multi-arch:** Every in-repo image built for `linux/amd64,linux/arm64`

## Requirement Language

- Use **SHALL** for normative requirements
- Use **SHOULD** for recommendations
- Use **MAY** for optional features

## Scenario Format

```markdown
#### Scenario: Descriptive name
- **GIVEN** initial context
- **WHEN** action occurs
- **THEN** expected result
```

## File Locations

- Specs: `openspec/specs/<capability>/spec.md` (25 canonical specs)
- Changes: `openspec/changes/<change-id>/`
- Archives: `openspec/changes/archive/YYYY-MM-DD-<change-id>/`
- Historical research: `docs/openspec/` (point-in-time, do not edit)
- Agent skills: `.agents/skills/<skill-name>/SKILL.md`
- Docker stacks: `infrastructure/stacks/<category>/<name>/`
- Canonical docs: `docs/0*-<domain>/<topic>.md` (frontmatter required)
- Doc index: `docs/00_index.md`
- Doc archive: `docs/archive/YYYY-MM-DD-<subtree>/`

## Review Process

1. Create proposal in `changes/<change-id>/`
2. Validate with `openspec validate <change-id> --strict`
3. Request review
4. Implement after approval
5. Archive after deployment

## Current In-Flight Changes

(Updated as changes move through the workflow. The 4 stale changes
`author-archive-gemini-and-uos-ingestion`, `cianfhoghlaim-oideachais-baml-first`,
`state-of-art-5-workspaces`, `team-workflow-stack` were archived on
2026-06-16 by the `openspec-consolidation-and-readme-refresh` change.)

| Change | Status |
|:--|:--|
| `consolidate-external-libs-into-tuatha` | in-flight (2/68 tasks) |
| `croilar-devtools-hub` | in-flight (6/55 tasks) |
| `croilar-personas-to-streams` | in-flight (6/45 tasks) |
| `croilar-portfolio` | in-flight (18/34 tasks) |
| `croilar-revitalisation` | in-flight (11/69 tasks) |
| `dagger-monorepo-integration` | in-flight (0/22 tasks) |
| `docs-restructuring` | in-flight (28/30 tasks) |
| `docs-skills-consolidation-pipeline` | in-flight (0/26 tasks) |
| `fix-existing-stacks` | in-flight (15/22 tasks) |
| `ireland-primary-jc-dlt-baml-and-full-stack-demo` | in-flight (0/22 tasks) |
| `leaving-cert-2026` | scaffold (0/28 tasks) |
| `monorepo-restructure-v2` | in-flight (19/20 tasks) |
| `openspec-consolidation-and-readme-refresh` | **this change** (Phase 1+2 done; Phase 3+4 in-flight) |
