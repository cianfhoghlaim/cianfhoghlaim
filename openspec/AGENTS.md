# OpenSpec Instructions for Cianfhoghlaim

## Priority quick reference

The 5 priority specs, the 4 priority commands, the 5 priority
skills, and the 1 priority mise task at the glance. **Read this
first**; the rest of the file is the full 34-spec catalogue.

### Priority specs (5 of 35)

| Spec | Quadrant | One-liner |
|:--|:--|:--|
| [`cianfhoghlaim-educational-mmo`](specs/cianfhoghlaim-educational-mmo/spec.md) | cianfhoghlaim | 8 NCCA LC subjects × per-subject quest packs × 8 ADK agents × hybrid x402 credential × TanStack Start 2D client |
| [`oideachais-pipeline`](specs/oideachais-pipeline/spec.md) | oideachais | Celtic education curriculum pipeline (Dagster + DLT + DuckLake + LanceDB + BAML) |
| [`oideachais-university-deep-extraction`](specs/oideachais-university-deep-extraction/spec.md) | oideachais | Per-university website deep extraction (BAML + DLT + Dagster + CocoIndex v1 + marimo + Cognee cross-archive) — the reusable template for any British Isles university |
| [`infrastructure-stacks`](specs/infrastructure-stacks/spec.md) | shared | 70+ Docker Compose stacks + stack-doctor + Pangolin + Infisical + Locket |
| [`agent-memory-systems`](specs/agent-memory-systems/spec.md) | shared | Cognee + Graphiti + LanceDB + FalkorDB + Memgraph agent memory |
| [`indexing-and-cognition`](specs/indexing-and-cognition/spec.md) | shared | CCC v1 code search + Cognee knowledge graph + OpenCode agent/MCP registry |
| [`dagger-pipelines`](specs/dagger-pipelines/spec.md) | shared | Polyglot CI/CD via Dagger (Python + TS) — 8-step GitOps |

> **Note:** `tuatha-platform` is now a deprecated alias for
> `cianfhoghlaim-educational-mmo`. See the
> `cianfhoghlaim-educational-mmo-v1` openspec change.

### Priority commands

```bash
openspec list --specs              # list all 34 capability specs
openspec list                      # list all pending changes
openspec validate <change-id> --strict    # MUST pass before commit
openspec archive <change-id> --yes        # after deploy
```

### Priority skills (5 of 123)

| Skill | When to load |
|:--|:--|
| [`data-engineering-pipeline-documentation`](../.agents/skills/data-engineering-pipeline-documentation/SKILL.md) | Router for STATUS.md + REFACTORING.md + per-area READMEs |
| [`dagger-pipelines`](../.agents/skills/dagger-pipelines/SKILL.md) | The 8 callable Dagger functions + the 4 build pipelines |
| [`infrastructure-stacks`](../.agents/skills/infrastructure-stacks/SKILL.md) | The 6-file GOLD_STANDARD pattern for Docker Compose stacks |
| [`agent-memory-systems`](../.agents/skills/agent-memory-systems/SKILL.md) | The 5 memory backends (Cognee + Graphiti + LanceDB + FalkorDB + Memgraph) |
| [`oideachais-cocoindex-v1`](../.agents/skills/oideachais-cocoindex-v1/SKILL.md) | CocoIndex v1 App canonical pattern + 4-rule conformance contract + `_lifespan.py` shared home (REFACTORING.md item 12 enforcement precondition) |
| [`indexing-and-cognition`](../.agents/skills/INDEXING_AND_COGNITION.md) | CCC code search + Cognee knowledge graph (7 clusters) + OpenCode agent/MCP registry (7 agents, 10 MCPs, 13 model-layer agents) |

### Priority mise task

```bash
mise run lint:skills               # validate .agents/skills/ metadata (123/123 pass)
```

### ccc code search (for openspec work)

```bash
bun run ccc:search "spec delta format"      # find prior art in the openspec archive
```

## Quick Reference

```bash
# List specs and changes
openspec list --specs
openspec list

# Validate before implementation
openspec validate <change-id> --strict

# Archive after deployment
openspec archive <change-id> --yes
```

## Workflow

### Creating Changes

1. Check existing specs: `openspec list --specs`
2. Create change directory: `openspec/changes/<change-id>/`
3. Write `proposal.md`, `tasks.md`, and spec deltas
4. Validate: `openspec validate <change-id> --strict`
5. Request review before implementing
6. Implement after approval
7. Archive after deployment: `openspec archive <change-id> --yes`

### Spec Delta Format

```markdown
## ADDED Requirements
### Requirement: New Feature
The system SHALL provide...

#### Scenario: Success case
- **WHEN** user performs action
- **THEN** expected result

## MODIFIED Requirements
### Requirement: Existing Feature
[Complete modified requirement with all scenarios]

## REMOVED Requirements
### Requirement: Old Feature
**Reason**: [Why removing]
**Migration**: [How to handle]
```

## Capability Specs (34)

The Cianfhoghlaim platform has **34 capability specs** organised into
**8 groups** by quadrant. Each spec is a thin capability pointer; the
**authoritative details** live in the corresponding
`.agents/skills/<skill>/SKILL.md` and the source code.

| Spec | Quadrant | One-liner |
|:--|:--|:--|
| `oideachais-pipeline` | oideachais | Celtic education curriculum pipeline (Dagster + DLT + DuckLake + LanceDB + BAML) |
| `oideachais-leabharlann` | oideachais | 4 dlt sources + 3 v1 CocoIndex Apps for the leabharlann/ corpus |
| `oideachais-baml-schemas` | oideachais | 9 BAML files + 3 extraction clients (ExtractEn, ExtractEnStrong, LocalVision) |
| `oideachais-cognify-knowledge-graph` | oideachais | 5-stage cross-stage cognify + 3 leabharlann cognify + 3 cross-archive FalkorDB edges |
| `oideachais-semantic-search` | oideachais | Cross-corpus LanceDB HNSW search (BGE-M3 + BGE-large-en-v1.5) |
| `oideachais-marimo-dashboards` | oideachais | 11 Marimo notebooks for the 5 educational stages + leabharlann full-stack demo |
| `upstream-package-monitoring` | oideachais | 3 CocoIndex v1 Apps + 4 Firecrawl monitors + 1 n8n bridge + 5 Dagster assets + 1 breaking-change sensor for motherduck / dlthub / lancedb / cocoindex |
| `ireland-primary-jc-dlt-baml` | oideachais | Ireland Primary + Junior Cycle dlt + BAML loop |
| `official-media-pipeline` | oideachais | Instagram-export → British-Isles government source enrichment (DLT + BAML `ClassifyOfficialMedia` + 4-lookup resolver) |
| `official-media-fediverse` | oideachais | Mastodon webfinger + Bluesky xrpc + Wikipedia + Companies House / CRO lookup (pure library) |
| `official-media-marimo` | oideachais | Marimo mission control + TanStack Start `/official-media` + Cognee dataset `oideachais_official_media` |
| `celtic-data-engineering-pipeline` | oideachais | dbt-duckdb project at `sruth/oideachais/dbt_project/` + `CelticDagsterDbtTranslator` + 2 marimo notebooks under `sruth/meaisinfhoghlaim/marimo/` (the `celtic-data-engineering-patterns` change) |
| `meaisinfhoghlaim-platform` | meaisinfhoghlaim | 10 sub-packages + 4 heartbeat dagster assets + Dagster code-location |
| `meaisinfhoghlaim-agent-frameworks` | meaisinfhoghlaim | 12 specialised agents (Root, Curriculum, Translation, Corpus, etc.) |
| `meaisinfhoghlaim-ocr-htr` | meaisinfhoghlaim | 10 OCR models across 6 backends (Pylaia, TrOCR, PaddleOCR, Tesseract, dots.ocr, VLM) |
| `gradio-ensemble-pattern` | meaisinfhoghlaim | `build_ensemble_interface()` helper + `push_model_to_hub()` HF Hub push helper (the ensemble UI pattern from `spaces/anti-phish/6_Gradio_Front_End.ipynb`) |
| `tuatha-platform` | tuatha | Celtic MMO (Babylon.js + Rust + SpacetimeDB) + crypteolas crypto platform |
| `croilar-portfolio` | croilar | Public TanStack Start site — multi-persona (aleyum, cianfhoghlaim, carlcashman) |
| `croilar-data-engineering` | croilar | Dagster + DLT + CocoIndex + BAML pipelines for croilar personas |
| `croilar-cv-extraction` | croilar | BAML extraction of the author's CV / achievements / teaching PDFs |
| `agent-memory-systems` | shared | Cognee + Graphiti + LanceDB + FalkorDB + Memgraph agent memory |
| `indexing-and-cognition` | shared | CCC v1 code search + Cognee 7-cluster knowledge graph + OpenCode agent/MCP registry (7 agents, 10 MCPs, 13 model-layer agents); supersedes `chunkhound-code-search` |
| `agent-observability` | shared | Langfuse + MLflow + RAGAS + Logfire |
| `agentic-frontend-frameworks` | shared | TanStack Start + CopilotKit + AG-UI + Hono + Convex |
| `dagger-pipelines` | shared | Polyglot CI/CD via Dagger (Python + TS) — 8-step GitOps |
| `infrastructure-stacks` | shared | 70+ Docker Compose stacks + stack-doctor.sh + Pangolin + Infisical + Locket |
| `data-engineering-pipeline-documentation` | shared | sruth/oideachais/STATUS.md + sruth/oideachais/REFACTORING.md + per-area READMEs |
| `spaces-cicd-pipeline` | shared | Reusable GH Action at `infrastructure/ci/spaces-sync.yml` for publishing any `spaces/*/` dir to a HF Space (gradio / docker / static SDKs) |
| `celtic-data-engineering-pipeline` | shared | dbt-duckdb at `sruth/oideachais/dbt_project/` + marimo notebooks at `sruth/meaisinfhoghlaim/marimo/` (the `celtic-data-engineering-patterns` change) |
| `gradio-ensemble-pattern` | shared | `sruth/meaisinfhoghlaim/pipelines/ensemble_gradio.py` + `spaces/_common/hf_hub_push.py` (sister to `celtic-data-engineering-patterns`) |
| `workflow-automation` | team | n8n + LLM pipelines (OpenCode Go API) |
| `task-management` | team | Vikunja kanban + Gantt + list + team sharing |
| `scheduling` | team | cal-diy team + per-member booking pages |
| `chunkhound-code-search` | tooling | Semantic code search with MVCC |
| `documentation` | tooling | Canonical docs/ structure (8 numbered domains), frontmatter schema |

### Quadrant map (1 consolidated package — v4)

> **NOTE:** As of 2026-06-28 (the `2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4` change),
> the 4 quadrants (oideachais, meaisinfhoghlaim, tuatha, croilar) + browser + crypteolas
> have been consolidated into a single `cianfhoghlaim/` package. The 4 former quadrant
> AGENTS.md files are preserved at their new in-package locations for backward navigation.

| Package | Path | Wheel name | README | AGENTS.md |
|:--|:--|:--|:--|:--|
| **Cianfhoghlaim** (consolidated) | `cianfhoghlaim/` | `cianfhoghlaim` (uv) + `codeolas` (uv sub-package) | `cianfhoghlaim/README.md` | `cianfhoghlaim/AGENTS.md` |
| **Oideachais sub-tree** (in cianfhoghlaim) | `cianfhoghlaim/web/apps/oideachais-web/` + `core/baml/_oideachais_src/` + `assets/_oideachais_dagster_defs/` | (part of `cianfhoghlaim`) | `cianfhoghlaim/web/apps/_oideachais_apps/README.md` | `cianfhoghlaim/web/apps/_oideachais_apps/AGENTS.md` |
| **Meaisínfhoghlaim sub-tree** (in cianfhoghlaim) | `cianfhoghlaim/agents/meaisinfhoghlaim/` + `ocr/_meaisinfhoghlaim_src/` | (part of `cianfhoghlaim`) | `cianfhoghlaim/agents/meaisinfhoghlaim/README.md` | `cianfhoghlaim/agents/meaisinfhoghlaim/AGENTS.md` |
| **Tuatha sub-tree** (in cianfhoghlaim) | `cianfhoghlaim/agents/tuatha/` + `web/apps/tuatha-ui/` | (part of `cianfhoghlaim`) | `cianfhoghlaim/agents/tuatha/README.md` | `cianfhoghlaim/agents/tuatha/AGENTS.md` |
| **Croílár sub-tree** (in cianfhoghlaim) | `cianfhoghlaim/web/apps/croilar-web/` + `assets/_croilar_dagster/` | (part of `cianfhoghlaim`) | `cianfhoghlaim/web/apps/_croilar_apps/README.md` | `cianfhoghlaim/web/apps/_croilar_apps/AGENTS.md` |

## Adding a New Capability

When a change introduces a new capability (not a MODIFIED of an existing one), follow this recipe:

1. **Add the capability** to the relevant section in [`project.md`](./project.md)
2. **Create a capability spec** at `openspec/specs/<capability>/spec.md` with at least 1 Requirement and 1 Scenario
3. **In the change's `specs/<capability>/spec.md`** (the delta file), use `## ADDED Requirements` header and a `### Requirement:` block with `#### Scenario:` children
4. **Validate with `openspec validate --strict`** — every Requirement needs at least one Scenario
5. **Cross-reference** related skills at `.agents/skills/<relevant-skill>/SKILL.md`

## Adding a New Docker Compose Stack

1. Create the directory: `infrastructure/stacks/<name>/`
2. Add the 6 GOLD_STANDARD files: `compose.yaml`, `sidecar.yaml`, `secrets.env`, `pangolin.yaml`, `blueprint.yaml`, `.env.example`
3. Use `pangolin.private-resources.<name>.*` (6-label pattern) — see `.agents/skills/stack-ops/SKILL.md`
4. Add a Komodo procedure: `infrastructure/komodo/procedures/<name>-*.toml`
5. Add Infisical items: `bun run scripts/init-vault.ts` after appending to root `.infisical.env`
6. Validate: `bun run validate-stacks` (the `stack-doctor` turbo task)

## Critical Rules

1. **NEVER skip validation** - Always run `openspec validate --strict`
2. **ALWAYS include scenarios** - Every requirement needs at least one
3. **Use correct headers** - `#### Scenario:` (4 hashtags)
4. **Respect constraints** - Architecture standardizes on **Infisical**, **Dagster**, **DuckLake**, **MCP** servers, and the 6-file GOLD_STANDARD stack pattern.
5. **Historical research lives in `docs/openspec/`** - never modify the 3 research files there; they're point-in-time artifacts.

## Cross-references

- [`project.md`](./project.md) — project conventions, capability list
- [`../docs/openspec/README.md`](../docs/openspec/README.md) — historical research material index
- [`../.agents/skills/stack-ops/SKILL.md`](../.agents/skills/stack-ops/SKILL.md) — operational skill for adding/fixing stacks
- [`../.agents/skills/chunkhound/SKILL.md`](../.agents/skills/chunkhound/SKILL.md) — semantic code search
- [`../AGENTS.md`](../AGENTS.md) — root agent instructions
- [`../sruth/oideachais/AGENTS.md`](../sruth/oideachais/AGENTS.md) — oideachais quadrant
- [`../sruth/meaisinfhoghlaim/AGENTS.md`](../sruth/meaisinfhoghlaim/AGENTS.md) — meaisinfhoghlaim quadrant
- [`../sruth/tuatha/AGENTS.md`](../sruth/tuatha/AGENTS.md) — tuatha quadrant
- [`../sruth/croilar/AGENTS.md`](../sruth/croilar/AGENTS.md) — croilar quadrant
