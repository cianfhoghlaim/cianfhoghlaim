# OpenSpec Instructions for Cianfhoghlaim

## Priority quick reference

The 5 priority specs, the 4 priority commands, the 5 priority
skills, and the 1 priority mise task at the glance. **Read this
first**; the rest of the file is the full 34-spec catalogue.

### Priority specs (8 of 48)

| Spec | Quadrant | One-liner |
|:--|:--|:--|
| [`british-isles-education-pipeline`](specs/british-isles-education-pipeline/spec.md) | cianfhoghlaim | The flagship — 6 Irish LC priority subjects (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science) + gov.ie circulars — NCCA + SEC + DLT + BAML + 7 v1 CocoIndex flows + 42 Dagster assets + 6 marimo notebooks + 4 MotherDuck Dives + daily Flight |
| [`cianfhoghlaim-educational-mmo`](specs/cianfhoghlaim-educational-mmo/spec.md) | cianfhoghlaim | 8 NCCA LC subjects × per-subject quest packs × 8 ADK agents × hybrid x402 credential × TanStack Start 2D client |
| [`dagster-5-layer-component-architecture`](specs/dagster-5-layer-component-architecture/spec.md) | shared | 5 KCG Components (Ingestion / Materials / Model Lifecycle / Asset Generation / Agent Operations) + Dagster 1.13+ Declarative Automation + Virtual Assets + State-Backed Components + R1–R4 conformance at scaffold time |
| [`oideachais-pipeline`](specs/oideachais-pipeline/spec.md) | oideachais | Celtic education curriculum pipeline (Dagster + DLT + DuckLake + LanceDB + BAML) |
| [`oideachais-university-deep-extraction`](specs/oideachais-university-deep-extraction/spec.md) | oideachais | Per-university website deep extraction (BAML + DLT + Dagster + CocoIndex v1 + marimo + Cognee cross-archive) — the reusable template for any British Isles university |
| [`infrastructure-stacks`](specs/infrastructure-stacks/spec.md) | shared | 94 Docker Compose stacks at `bonneagar/stacks/` + stack-doctor + Pangolin + Infisical + Locket + Komodo resource-syncs |
| [`agent-memory-systems`](specs/agent-memory-systems/spec.md) | shared | Cognee + Graphiti + LanceDB + FalkorDB + Memgraph agent memory |
| [`indexing-and-cognition`](specs/indexing-and-cognition/spec.md) | shared | CCC v1 code search + Cognee knowledge graph + OpenCode agent/MCP registry |
| [`dagger-pipelines`](specs/dagger-pipelines/spec.md) | shared | Polyglot CI/CD via Dagger (Python + TS) — 8-step GitOps |

> **Note:** `tuatha-platform` has been **retired** (2026-07-06 by the
> `2026-07-06-drift-cleanup-and-v4-alignment` change). Its content has
> been absorbed into `cianfhoghlaim-educational-mmo`.

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
mise run lint:skills               # validate .agents/skills/ metadata (53/53 pass as of v4 consolidation)
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

## Capability Specs (37)

The Cianfhoghlaim platform has **48 capability specs** organised into
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
| `meaisinfhoghlaim-platform` | meaisinfhoghlaim | 10 sub-packages + 4 heartbeat dagster assets + Dagster code-location |
| `meaisinfhoghlaim-agent-frameworks` | meaisinfhoghlaim | 12 specialised agents (Root, Curriculum, Translation, Corpus, etc.) |
| `meaisinfhoghlaim-ocr-htr` | meaisinfhoghlaim | 10 OCR models across 6 backends (Pylaia, TrOCR, PaddleOCR, Tesseract, dots.ocr, VLM) |
| `croilar-portfolio` | croilar | Public TanStack Start site — multi-persona (aleyum, cianfhoghlaim, carlcashman) |
| `croilar-data-engineering` | croilar | Dagster + DLT + CocoIndex + BAML pipelines for croilar personas |
| `croilar-cv-extraction` | croilar | BAML extraction of the author's CV / achievements / teaching PDFs |
| `agent-memory-systems` | shared | Cognee + Graphiti + LanceDB + FalkorDB + Memgraph agent memory |
| `indexing-and-cognition` | shared | CCC v1 code search + Cognee 7-cluster knowledge graph + OpenCode agent/MCP registry (7 agents, 10 MCPs, 13 model-layer agents); supersedes `chunkhound-code-search` |
| `agent-observability` | shared | Langfuse + MLflow + RAGAS + Logfire |
| `agentic-frontend-frameworks` | shared | TanStack Start + CopilotKit + AG-UI + Hono + Convex |
| `dagger-pipelines` | shared | Polyglot CI/CD via Dagger (Python + TS) — 8-step GitOps |
| `infrastructure-stacks` | shared | 94 Docker Compose stacks at `bonneagar/stacks/` + stack-doctor.sh + Pangolin + Infisical + Locket |
| `data-engineering-pipeline-documentation` | shared | STATUS.md + REFACTORING.md + per-area READMEs |
| `british-isles-education-pipeline` | cianfhoghlaim | 6 Irish LC priority subjects (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science) + gov.ie circulars — NCCA + SEC + gov.ie DLT + BAML + 7 v1 CocoIndex flows + 42 Dagster assets + 6 marimo notebooks + 4 MotherDuck Dives + daily Flight |
| `agent-platform-cluster` | shared | 8-stack cluster (lakehouse + litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb) + 3 agent surfaces (openclaw + openchamber + hermes); LiteLLM is the M3 chokepoint |
| `apple-photos-ingestion` | cianfhoghlaim | 5th leabharlann corpus via osxphotos → 3 v1 CocoIndex Apps (metadata + chunks + geospatial) + 5 Dagster assets + 2 routing + 1 cross-frame velocity; privacy gate `LEABHARLANN_PHOTOS_INCLUDE_GPS` (default false) |
| `dagster-5-layer-component-architecture` | shared | 5 KCG Components (Ingestion / Materials / Model Lifecycle / Asset Generation / Agent Operations) + Dagster 1.13+ Declarative Automation + Virtual Assets + State-Backed Components |
| `spaces-cicd-pipeline` | shared | Reusable GH Action at `infrastructure/ci/spaces-sync.yml` for publishing any `spaces/*/` dir to a HF Space (gradio / docker / static SDKs) |
| `workflow-automation` | team | n8n + LLM pipelines (OpenCode Go API) |
| `task-management` | team | Vikunja kanban + Gantt + list + team sharing |
| `scheduling` | team | cal-diy team + per-member booking pages |
| `chunkhound-code-search` | tooling | Semantic code search with MVCC |
| `documentation` | tooling | Canonical docs/ structure (8 numbered domains), frontmatter schema |
| `dev-env-demo-tools` | shared | 8 `FunctionTool`-wrapped dev-env capabilities (`ccc_search`, `ccc_index`, `drift_detect`, `firecrawl_refactor_discover`, `hf_best_model`, `openspec_list_specs`, `openspec_validate`, `mise_lint_skills`) + `dev_env_demo_agent` + 6 marimo notebooks + recorded transcript at `docs/agents/dev-env-demo-transcript.md` |

### Quadrant map (post-v7 — single flattened package)

> **NOTE:** As of 2026-07-17 (the
> `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/`
> change), the post-v4 `cianfhoghlaim/` nesting is removed — the
> Python package is the repo itself. The 4 former quadrant
> AGENTS.md files live directly under their respective sub-packages.

| Package | Path | Wheel name | README | AGENTS.md |
|:--|:--|:--|:--|:--|
| **Cianfhoghlaim** (post-v7 flat) | `.` (repo root) | `cianfhoghlaim` (uv) | `README.md` | `AGENTS.md` |
| **Oideachais sub-tree** (in this repo) | `web/apps/oideachais-web/` + `baml/education/` + `orchestration/` | (part of `cianfhoghlaim`) | `web/apps/_oideachais_apps/README.md` | `web/apps/_oideachais_apps/AGENTS.md` |
| **Meaisínfhoghlaim sub-tree** (in this repo) | `agents/meaisinfhoghlaim/` + `meaisinfhoghlaim/ocr/` | (part of `cianfhoghlaim`) | `agents/meaisinfhoghlaim/README.md` | `agents/meaisinfhoghlaim/AGENTS.md` |
| **Tuatha sub-tree** (in this repo) | `agents/tuatha/` + `web/apps/tuatha-ui/` | (part of `cianfhoghlaim`) | `agents/tuatha/README.md` | `agents/tuatha/AGENTS.md` |
| **Croílár sub-tree** (in this repo) | `web/apps/croilar-web/` + `croilar/` | (part of `cianfhoghlaim`) | `web/apps/_croilar_apps/README.md` | `web/apps/_croilar_apps/AGENTS.md` |
| **Bonneagar** (IaC sub-dir, in this repo) | `bonneagar/` (subdirectory) | (none — TypeScript IaC) | `bonneagar/README.md` | `bonneagar/AGENTS.md` |

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
- [`../web/apps/_oideachais_apps/AGENTS.md`](../web/apps/_oideachais_apps/AGENTS.md) — oideachais quadrant
- [`../agents/meaisinfhoghlaim/AGENTS.md`](../agents/meaisinfhoghlaim/AGENTS.md) — meaisinfhoghlaim quadrant *(if missing, see Cianfhoghlaim root AGENTS.md)*
- [`../agents/tuatha/AGENTS.md`](../agents/tuatha/AGENTS.md) — tuatha quadrant
- [`../web/apps/_croilar_apps/AGENTS.md`](../web/apps/_croilar_apps/AGENTS.md) — croilar quadrant

## Cross-repo sync convention

For openspec changes that touch more than one of the 3 repos
(cianfhoghlaim + bonneagar + leabharlann), include a
`cross-repo-sync.md` file at `openspec/changes/<id>/cross-repo-sync.md`
that lists:

1. The commit plan for each affected repo
2. The branch name + remote URL for each push target
3. The order of operations (which repo MUST be committed first)

The 2 repos MUST be committed in this order: **bonneagar first,
then cianfhoghlaim** (the IaC tests in bonneagar are a prerequisite
for the cianfhoghlaim openspec archive).

Single-repo changes (the common case) MAY omit the file, but if
included it MUST be referenced from `proposal.md`.

## Dependencies field convention

Every openspec change's `proposal.md` SHALL include a
`## Dependencies` section that declares:

```markdown
## Dependencies

`Blocked by: <change-id>` (topo ordering)
`Blocked by (soft): <change-id>` (this change extends but doesn't block)
`Affected repos: cianfhoghlaim, bonneagar, leabharlann` (which repos this change touches)
```

The change CANNOT archive until the blocker archives. The
`Blocked by (soft)` line declares an informational dependency
for sequencing but does not enforce archiving.

If the change has no dependencies, declare `Blocked by: none`.
- [`../AGENTS.md`](../AGENTS.md) — the consolidated cianfhoghlaim AGENTS.md (post-v4)
