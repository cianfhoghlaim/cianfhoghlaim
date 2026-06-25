# Tasks: OpenSpec Consolidation & README/AGENTS.md Refresh

## Phase 1 — Spec consolidation (44 → 26)

### 1.1 Create 8 new canonical specs (the "ADDED" deltas)

- [ ] Create `openspec/specs/oideachais-leabharlann/spec.md` (the merged leabharlann pipeline: filesystem + takeout + BAML + cocoindex-v1)
- [ ] Create `openspec/specs/oideachais-baml-schemas/spec.md` (the merged BAML schemas: assessment + bilingual + author-archive)
- [ ] Create `openspec/specs/oideachais-cognify-knowledge-graph/spec.md` (the merged cognify: knowledge-graph + leabharlann-cognify-edges)
- [ ] Create `openspec/specs/oideachais-marimo-dashboards/spec.md` (the merged dashboards: leabharlann-full-stack-demo)
- [ ] Create `openspec/specs/tuatha-platform/spec.md` (first spec for the MMO + crypto quadrant)
- [ ] Create `openspec/specs/meaisinfhoghlaim-platform/spec.md` (first spec for the AI/ML quadrant)
- [ ] Create `openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md` (the 12 specialised agents)
- [ ] Create `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` (the 10 OCR models)
- [ ] Create `openspec/specs/dagger-pipelines/spec.md` (consolidated dagger: ci + forgejo + komodo + cloudflare + gitops)

### 1.2 Create 5 renamed canonical specs

- [ ] Create `openspec/specs/agent-memory-systems/spec.md` (renamed from `memory-systems`; shrunk)
- [ ] Create `openspec/specs/agent-observability/spec.md` (renamed from `observability`; shrunk)
- [ ] Create `openspec/specs/agentic-frontend-frameworks/spec.md` (renamed from `frontend-frameworks`; shrunk)
- [ ] Create `openspec/specs/oideachais-semantic-search/spec.md` (renamed from `semantic-search`; content preserved)

### 1.3 Delete 18 redundant specs

- [ ] Delete `openspec/specs/data-pipeline/`
- [ ] Delete `openspec/specs/curriculum-ingestion/`
- [ ] Delete `openspec/specs/site-analysis-mcp/`
- [ ] Delete `openspec/specs/domain-source-registry/`
- [ ] Delete `openspec/specs/stack-audit/`
- [ ] Delete `openspec/specs/croilar-self-hosted-portal/`
- [ ] Delete `openspec/specs/croilar-gradio-hf-demo/`
- [ ] Delete `openspec/specs/croilar-persona-registry/`
- [ ] Delete `openspec/specs/infrastructure/`
- [ ] Delete `openspec/specs/dagger-blockchain/`
- [ ] Delete `openspec/specs/dagger-ci/`
- [ ] Delete `openspec/specs/dagger-forgejo/`
- [ ] Delete `openspec/specs/dagger-komodo/`
- [ ] Delete `openspec/specs/dagger-cloudflare/`
- [ ] Delete `openspec/specs/dagger-gitops/`
- [ ] Delete `openspec/specs/agent-frameworks/`
- [ ] Delete `openspec/specs/memory-systems/`
- [ ] Delete `openspec/specs/observability/`
- [ ] Delete `openspec/specs/frontend-frameworks/`
- [ ] Delete `openspec/specs/semantic-search/`
- [ ] Delete `openspec/specs/leabharlann-ingestion/`
- [ ] Delete `openspec/specs/leabharlann-full-stack-demo/`
- [ ] Delete `openspec/specs/leabharlann-cognify-and-cross-archive-edges/`
- [ ] Delete `openspec/specs/author-archive-baml-extraction/`
- [ ] Delete `openspec/specs/ireland-primary-jc-dlt-baml/`
- [ ] Delete `openspec/specs/assessment-extraction/`
- [ ] Delete `openspec/specs/bilingual-content/`
- [ ] Delete `openspec/specs/knowledge-graph/`

### 1.4 Write the change's spec deltas (the `## ADDED Requirements` blocks)

- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/oideachais-leabharlann/spec.md` (delta)
- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/oideachais-baml-schemas/spec.md` (delta)
- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/oideachais-cognify-knowledge-graph/spec.md` (delta)
- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/oideachais-marimo-dashboards/spec.md` (delta)
- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/tuatha-platform/spec.md` (delta)
- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/meaisinfhoghlaim-platform/spec.md` (delta)
- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/meaisinfhoghlaim-agent-frameworks/spec.md` (delta)
- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/meaisinfhoghlaim-ocr-htr/spec.md` (delta)
- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/dagger-pipelines/spec.md` (delta)
- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/agent-memory-systems/spec.md` (delta)
- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/agent-observability/spec.md` (delta)
- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/agentic-frontend-frameworks/spec.md` (delta)
- [ ] Write `openspec/changes/openspec-consolidation-and-readme-refresh/specs/oideachais-semantic-search/spec.md` (delta)

### 1.5 Validate

- [ ] Run `openspec validate openspec-consolidation-and-readme-refresh --strict` — confirm green

## Phase 2 — In-flight change cleanup (14 → 9, 4 archived)

- [ ] Archive `author-archive-gemini-and-uos-ingestion` (already superseded)
- [ ] Archive `cianfhoghlaim-oideachais-baml-first` (BAML done; dlt in `ireland-primary-jc-dlt-baml-and-full-stack-demo`)
- [ ] Archive `state-of-art-5-workspaces` (never started)
- [ ] Verify `team-workflow-stack` is archived (or archive it)

## Phase 3 — README/AGENTS.md refresh (12 files)

### 3.1 Create 3 new AGENTS.md files

- [ ] Create `sruth/oideachais/AGENTS.md` (lakehouse + dlt + BAML + dagster surface; re-export shims to sruth/meaisinfhoghlaim/)
- [ ] Create `sruth/tuatha/AGENTS.md` (MMO + crypto scope, SpacetimeDB, BAML `ui_components.baml`)
- [ ] Create `sruth/croilar/AGENTS.md` (multi-persona model, 5 subprojects, the 4 openspec specs)

### 3.2 Refresh 4 README.md files

- [ ] Refresh `sruth/oideachais/README.md` (add link to new `sruth/oideachais/AGENTS.md` and the 7 oideachais-* openspec specs)
- [ ] Refresh `sruth/tuatha/README.md` (add link to new `sruth/tuatha/AGENTS.md` and the `tuatha-platform` spec)
- [ ] Refresh `sruth/croilar/README.md` (add link to new `sruth/croilar/AGENTS.md` and the 3 croilar-* specs)
- [ ] Refresh `sruth/meaisinfhoghlaim/README.md` (light refresh; add links to the 3 new meaisinfhoghlaim-* openspec specs)

### 3.3 Refresh 2 existing AGENTS.md files

- [ ] Light-refresh `sruth/meaisinfhoghlaim/AGENTS.md` (add links to the 3 new specs)
- [ ] Light-refresh `AGENTS.md` (root) — add `sruth/meaisinfhoghlaim/` to the workspace table; add `sruth/tuatha/AGENTS.md` and `sruth/croilar/AGENTS.md` references

### 3.4 Rewrite the 2 openspec meta files

- [ ] Rewrite `openspec/AGENTS.md` (flat 26-row capability table; 4-quadrant workflow recipe; new in-flight changes table)
- [ ] Rewrite `openspec/project.md` (new 26-capability table; 4 quadrants section; updated in-flight changes table)

### 3.5 Refresh 1 doc

- [ ] Refresh `docs/00_index.md` (update openspec links)

## Phase 4 — Final validate, commit, push, archive

- [ ] Run `openspec validate openspec-consolidation-and-readme-refresh --strict` — confirm green
- [ ] Run `git status` and stage relevant files (one commit per phase)
- [ ] Push to origin
- [ ] Archive the change: `openspec archive openspec-consolidation-and-readme-refresh --yes`
- [ ] Commit the archive metadata
- [ ] Final `git push` and confirm "up to date with origin"
