# Documentation Indexing & Consolidation — Integration Audit (2026-06-10)

> Built in Plan mode, then written up in build mode on 2026-06-10.
> Read-only survey of the post-rearrangement `docs/` layout against
> the existing ccc + Cognee integration state. Output of Phase 0.

## 1. Why this exists

A 2026-06-06 retrospective (now at `docs/02-audit/consolidation_plan.md`)
consolidated 1,038 source files into 36 canonical docs across 7
numbered domains. Between then and 2026-06-10, the user rearranged
`docs/` substantially — the 7 stable numbered dirs are preserved,
but 12 *new* extended-numbered dirs were added, 100 loose `.md`
files now sit at `docs/` root, and the old `docs/cognee/` and
`docs/archive/` directories are gone (their content moved inline
to `docs/01-cognee/` and `docs/2026-06-06-*`).

This audit is the bridge: what changed, what's still healthy, what
needs to be re-energised. It's the input to Phases 1-8.

## 2. New `docs/` layout (post-rearrangement)

### 2.1 Top-level (139 entries)

| Category | Count | Notes |
|:--|:-:|:--|
| Numbered dirs (`NN-*`) | 19 | the 7 stable + 12 extended, coexist at the same numeric prefix |
| Loose files at root (`.md`/`.py`/`.yaml`) | 100 | 87 .md + 11 .py + 2 .yaml |
| Loose PDFs at root | 5 | 5 papers / monographs |
| Non-numbered subdirs | 14 | the preserved prior subtrees (`baml/`, `dagster/`, `dlt/`, `web/`, `tuatha/`, etc.) |
| Date-stamped dirs | 2 | `docs/2026-06-06-data-engineering/`, `docs/2026-06-06-meaisinfhoghlaim/` |
| Total entries | 139 | |
| Total size | 901 MB | vs. the prior 480 KB before rearrangement |

### 2.2 The 19 numbered dirs (and what each is)

**Stable (from 2026-06-06 consolidation, preserved):**

| Dir | Files | Domain |
|:--|:-:|:-:|
| `01-platform-architecture/` | 9 | architecture, stacks, secrets, komodo, pangolin, k8s, monorepo |
| `02-data-platform/` | 4 | data architecture, dagster, dlt |
| `03-agents/` | 5+ | agent frameworks, BAML extraction, browser automation, MCP |
| `04-ai-ml/` | 8 | fine-tuning, OCR/HTR, RAG, knowledge graphs, embeddings, Celtic AI, ML pipelines |
| `05-web/` | 4 | frontend, convex/hono/auth, UI components |
| `06-product/` | 5 | Celtic MMO, crypteolas, game dev, educational platform |
| `07-standards/` | 2 | observability patterns, project conventions |

**Extended (new, 2026-06-10):**

| Dir | Files | Domain |
|:--|:-:|:-:|
| `00-core/` | — | project core (CLAUDE.md, PROJECT_SPEC.md, CONSTRAINTS.md, AGENTS.md) |
| `00-package-ecosystem/` | — | external skill-template bundles |
| `01-cognee/` | 10 | the 10 cognee docs, moved from old `docs/cognee/` |
| `01-patterns/` | 7 | domain-specific patterns (BAML, data pipeline, embeddings, observability, storage, web) |
| `02-architecture/` | 10 | high-level architecture documents |
| `02-audit/` | 5 | the 2026-06-06 retrospective + readiness audits |
| `03-pipelines/` | 8 | pipeline-specific code+config (`ag_ui_protocol.py`, `dagster_definitions.py`, etc.) |
| `05-celtic-language/` | 6 | bilingual edtech, Celtic AI, language architecture |
| `06-infrastructure/` | many | infrastructure-related docs (scraping, ansible, deployment, AI pipelines) |
| `07-skills/` | 10+ | per-tool skill docs (agno, baml, cocoindex, dagster, dlt, etc.) |
| `08-examples/` | 8 | worked examples |
| `08-screenshots/` | many | PNGs, images, ui-inspiration |

The **stable 7** and **extended 12** share numeric prefixes (e.g. `01-platform-architecture/` and `01-cognee/` both start with `01-*`) but don't overlap in content.

### 2.3 The 100 loose root files

| File count | Has ccc/cognee frontmatter | Notes |
|:-:|:-:|:--|
| 87 .md | 1 (`00_index.md`) | only the master index is frontmatter-clean |
| 11 .py | n/a | reference code, not docs |
| 2 .yaml | n/a | configs |
| 5 .pdf | n/a | papers / monographs |

**Critical observation:** of the 87 loose .md files, 86 lack ccc/cognee-clean frontmatter (`title`, `domain`, `status`, `description`, `read_when`). The canonical docs in the 7 stable dirs all have it; the loose files don't. This is the gap Phase 2 (frontmatter sweep) addresses.

### 2.4 Sample loose-file inventory (top 30 by likely importance)

(Verified to exist on 2026-06-10; not yet routed.)

| File | Likely target dir |
|:--|:--|
| `docs/CLAUDE.md` | `00-core/` |
| `docs/PROJECT_SPEC.md` | `00-core/` |
| `docs/CONSTRAINTS.md` | `00-core/` |
| `docs/AGENTS.md` | `00-core/` |
| `docs/OIDEACHAIS_SPEC.md` | `00-core/` or `02-architecture/` |
| `docs/OIDEACHAIS_PIPELINE.md` | `02-architecture/` or `03-pipelines/` |
| `docs/INDEX.md` | (deprecate — overlap with `00_index.md`) |
| `docs/DEPLOYMENT_STATUS.md` | `06-infrastructure/` |
| `docs/TECH_STACK.md` | `06-infrastructure/` |
| `docs/TODO_AUDIT.md` | `02-audit/` |
| `docs/BAML.md` | `07-skills/` (it's actually a SKILL doc) |
| `docs/cognee-sdk.md` | `07-skills/` |
| `docs/graphiti-sdk.md` | `07-skills/` |
| `docs/dagster.md` | `07-skills/` |
| `docs/dlt.md` | `07-skills/` |
| `docs/lancedb.md` | `07-skills/` |
| `docs/duckdb.md` | `07-skills/` |
| `docs/memgraph.md` | `07-skills/` |
| `docs/neo4j.md` | `07-skills/` |
| `docs/unsloth.md` | `07-skills/` |
| `docs/trl.md` | `07-skills/` |
| `docs/ragas.md` | `07-skills/` |
| `docs/sqlmesh.md` | `07-skills/` |
| `docs/ducklake.md` | `07-skills/` |
| `docs/cocoindex.md` | `07-skills/` |
| `docs/hono.md` | `07-skills/` |
| `docs/tanstack-start.md` | `07-skills/` |
| `docs/copilotkit.md` | `07-skills/` |
| `docs/cloudflare-r2.md` | `07-skills/` |
| `docs/crawl4ai-sdk.md` | `07-skills/` |
| `docs/patchright.md` | `07-skills/` |
| `docs/stagehand.md` | `07-skills/` |
| `docs/modal.md` | `07-skills/` |
| `docs/marimo.md` | `07-skills/` |
| `docs/observability_init.py` | `03-pipelines/` (or `06-infrastructure/`) |
| `docs/curriculum_embedding.py` | `03-pipelines/` |
| `docs/api_main.py` | `03-pipelines/` |
| `docs/ag_ui_protocol.py` | `03-pipelines/` |
| `docs/dagster_definitions.py` | `03-pipelines/` |
| `docs/dagster_factories.py` | `03-pipelines/` |
| `docs/storage_init.py` | `03-pipelines/` |
| `docs/browser_orchestrator.py` | `03-pipelines/` |
| `docs/browser_session.py` | `03-pipelines/` |
| `docs/durable_orchestrator.py` | `03-pipelines/` |
| `docs/celtic_ml_models.yaml` | `07-skills/` (or `05-celtic-language/`) |
| `docs/models_registry.yaml` | `07-skills/` |

(rough heuristic; Phase 2's LLM-driven classifier may adjust)

## 3. ccc (CocoIndex Code) state

### 3.1 Current index (post-rebuild but pre-rearrangement)

- **Chunks:** 277,947
- **Files:** 21,352
- **Top languages:** markdown (96,976), java (65,165), javascript (49,959), python (21,491), tsx (8,187)
- **Status:** indexed, but the index was built *before* the rearrangement. The new files are not findable.

### 3.2 Verified stale (probes return zero results)

- `ccc search --path "docs/CLAUDE.md" "AGENTS"` → no results
- `ccc search --path "docs/01-cognee/*" "cognee"` → no results
- `ccc search --path "docs/BAML.md" "type-safe LLM"` → no results
- `ccc search --path "tuatha/crypteolas/baml_src/*" "vulnerability"` → no results
- `ccc search --path "spaces/cianfhoghlaim/*" "Manannan"` → no results

But the *old* paths still return hits (e.g. `docs/archive/2026-06-06-agents/agent-frameworks.md`), which is misleading — those files have been moved.

### 3.3 Settings gap

`.cocoindex_code/settings.yml` has the standard include_patterns list but is missing `**/*.baml`. So 28 BAML files in `tuatha/` + 2 in `spaces/_common/` are permanently excluded regardless of re-index.

### 3.4 No `guides.yml` yet

The ccc `[guide]` feature (concept-guide hits in search results) is not configured. The user's "make ccc + Cognee deeply integrated" goal implies a `guides.yml` describing the 19 numbered domains is high-leverage.

## 4. Cognee state

### 4.1 Cognee Python package

- **Installed:** `cognee 1.0.1` in `.venv`
- **MCP server:** `cognee-mcp` available via `uvx cognee-mcp`
- **Block in `opencode.json`:** exists, points at `http://localhost:8100`, with env `COGNEE_API_URL` / `COGNEE_API_KEY` / `LLM_API_KEY`
- **Backends (default, local):** SQLite + LanceDB (no external services required)
- **Knowledge graph state:** empty — no `cognify()` has been run for the new docs

### 4.2 Cognee Docker stack (the user's preferred path)

- **Stack path:** `infrastructure/stacks/machine_learning/cognee/`
- **Files present:** `compose.yaml`, `secrets.env`, `pangolin.yaml`, `blueprint.yaml`, `README.md`
- **Files missing:** `sidecar.yaml` (Locket), `infrastructure/komodo/stacks/cognee-bunchloch.toml` (Komodo), `infrastructure/komodo/procedures/deploy-cognee-bunchloch.toml` (Komodo procedure)
- **`pangolin.yaml` uses old format** (`pangea:` block). Needs rewrite to the `services:` + `pangolin.private-resources.cognee.*` labels format used in `pocket-id/pangolin.yaml`
- **`compose.yaml` defaults:** `LLM_BASE_URL=http://litellm:4000/v1`, `LLM_MODEL=gemini-2.0-flash`, `LLM_PROVIDER=litellm` — needs switch to DeepSeek
- **On oci.arm1:** stack not running. Currently only `n8n-postgres` and `pangolin-postgres` are up. Cognee will be a first-time deploy.

### 4.3 Graphiti state

- **Stack path:** `infrastructure/stacks/machine_learning/graphiti/` (presumed to exist; needs audit in Phase 0's successor)
- **On oci.arm1:** not running
- **MCP block in `opencode.json`:** exists, `enabled: true`, points at `bolt://localhost:7687` (Neo4j)
- **Bring-up cost:** 30-60 min if the compose file exists; longer if we need to add the Locket + Komodo + Pangolin wiring

## 5. Existing infra that does work

| Component | Status | Where |
|:--|:--|:--|
| `mise` task `ccc:init` | exists | `mise.toml` |
| `mise` task `ccc:index` | exists | `mise.toml` |
| `mise` task `ccc:search` | exists | `mise.toml` |
| `mise` task `docs:cognee` | exists | `mise.toml` |
| `mise` task `docs:cognee:domain` | exists | `mise.toml` |
| `mise` task `docs:cognee:summary` | exists | `mise.toml` |
| `infrastructure/scripts/cognee-ingest-docs.py` | exists, well-built (298 lines) | `infrastructure/scripts/` |
| `.agents/skills/ccc/SKILL.md` | exists | `.agents/skills/ccc/` |
| `.agents/skills/cognee/SKILL.md` | exists | `.agents/skills/cognee/` |
| `.agents/skills/ccc/references/management.md` | exists | ccc install instructions |

## 6. What needs to be built (work product)

| Phase | Title | Build items |
|:-:|:--|:--|
| 1 | ccc refresh | settings.yml +1 line, guides.yml new, `ccc reset` + re-index |
| 2 | Promote loose files | `scripts/promote-loose-docs.py` new, 100 file moves + 100 frontmatter patches |
| 3 | Cognee Docker | compose + secrets + .env + env.example + sidecar + blueprint + pangolin + komodo-stack + komodo-procedure + README (10 files) |
| 4 | Cognee ingest | extend `cognee-ingest-docs.py` for 19 domains, run `mise run docs:cognee` |
| 5a | Archive ingest | new `cognee-ingest-archive.py`, run with dedup |
| 5b | Graphiti bring-up | 5-6 files (compose + sidecar + blueprint + pangolin + README + 2 komodo) |
| 6 | Cross-ref | survey doc (queries + summarisation) |
| 7 | Consolidation | `docs/09-cross-references.md` + `00_index.md` patch + survey doc |
| 8 | Integration | 3-4 skill doc updates + `cognee-mcp-quickstart.md` |

## 7. Phasing rationale

- **Phase 0 (this doc) is read-only.** Pure inventory. No code changes.
- **Phase 1 is independent of Cognee.** ccc is the semantic search surface; rebuilding it is useful even if Cognee is never brought online. ~1 hour.
- **Phase 2 is a prerequisite for Phase 4.** Cognee ingest needs frontmatter on every doc to assign `domain` correctly. Without Phase 2, the loose files would land in the wrong datasets. ~2-3 hours (LLM-batched).
- **Phase 3 can run in parallel with Phase 1+2.** The Docker bring-up is independent of the ccc work. The user's "I want this done properly" framing means getting the Komodo + Locket + Pangolin wiring right the first time.
- **Phase 4 is the first cognify.** Depends on Phases 2 (frontmatter) + 3 (Cognee running).
- **Phase 5a depends on Phase 4.** We need a working Cognee before we can ingest more.
- **Phase 5b is parallel to 5a.** Graphiti is a separate backend.
- **Phases 6-7 are composition work** that depend on Phase 5's ingested data.
- **Phase 8 is the final integration** — the docs/skill updates that make this all usable by future agents.
- **Phase 9 is the close-out** — 1 commit per phase, push, update STATUS.md.

## 8. What I'm NOT proposing

- **Reverting the rearrangement.** The new layout is the user's choice; the work is to align our tooling with it, not to argue.
- **Heavy consolidation of the loose files into the stable/extended dirs.** Phase 2 *promotes* them; the content stays as-is. The 2026-06-06 audit said heavy merging is done.
- **A second 1,038 → 36-style consolidation.** Same reason. Light touch only.
- **CI/CD integration of ccc or Cognee.** Out of scope; the indexes stay local.
- **Removing the loose .py files or the PDFs at root.** They're reference material (code-as-doc; papers/monographs). Cognee ingests them in Phase 5a; ccc indexes them already.
- **Migrating the `baml/`, `dagster/`, `dlt/`, `web/`, `tuatha/`, etc. subdirs at `docs/` root into numbered dirs.** Same reason — they're preserved subtrees from the prior structure.

## 9. Open items for the user (not blocking)

- **The `oideachais` Python venv has `cognee 1.0.1` installed.** This is a *different* runtime from the Docker stack. Both can be used; they share `~/.cognee/` config if the volume is mounted. Decision: use the Docker stack for the bring-up (per user direction) and the Python package for ad-hoc queries from the venv.
- **The Cognee compose file's `litellm:4000` upstream.** If anyone else (e.g. `oideachais` Dagster assets) expects `litellm:4000` to proxy to DeepSeek, they'll need a separate config. This will be noted in the new README.
- **The Komodo `cognee-bunchloch.toml` stack entry** I plan to create is parallel to the existing `oideachais-bunchloch.toml`. They're independent stacks; can be deployed separately.
- **The `~/.cache/cognee-dedup.json` cache** is a per-user file. If multiple agents work on the same machine, they may want separate caches (per-user subdir). Default behaviour is fine for now; can be made per-user later.

## 10. Total scope

- **Phases 0-9**: 8-15 hours of agent work, spread over multiple sessions
- **Commits:** ~9 (one per phase, plus a final close-out)
- **New files:** ~20 (scripts, compose additions, survey docs, guides.yml, cross-references doc)
- **Modified files:** ~25 (frontmatter on 100 loose files, mise tasks, skill docs, compose files, .env)

The next action is Phase 1: ccc refresh.
