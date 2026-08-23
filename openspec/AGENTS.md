# OpenSpec Instructions for Cianfhoghlaim

## Priority quick reference

The 13 priority specs, the 8 priority commands, the 9 priority
skills, and the 4 priority mise tasks at a glance. **Read this
first**; the rest of the file is the full 97-spec catalogue.

### Priority specs (14 of 97)

| Spec | Quadrant | One-liner |
|:--|:--|:--|
| [`centralized-model-registry`](specs/centralized-model-registry/spec.md) | shared | **NEW 2026-08-15**: The single canonical model registry (76 entries / 7 families: ocr_vision / text_llm / embedder / rerank / image_gen / voice / translation) — drives LiteLLM, BAML, agents, embedders, image-gen, voice, translation |
| [`centralized-schema-registry`](specs/centralized-schema-registry/spec.md) | shared | **NEW 2026-08-15**: BAML is the single source of truth — Pydantic + Zod are codegen; 96 hand-written Pydantic duplicates removed |
| [`deployment-control-panel`](specs/deployment-control-panel/spec.md) | shared | **NEW 2026-08-15**: The 5-tab marimo control panel + web UI + CLI for picking models/pipelines/datasets/stacks; writes to `deployment-choice.yaml` |
| [`british-isles-education-pipeline`](specs/british-isles-education-pipeline/spec.md) | cianfhoghlaim | The flagship — 6 Irish LC priority subjects (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science) + gov.ie circulars — NCCA + SEC + DLT + BAML + 7 v1 CocoIndex flows + 42 Dagster assets + 6 marimo notebooks + 4 MotherDuck Dives + daily Flight |
| [`cianfhoghlaim-educational-mmo`](specs/cianfhoghlaim-educational-mmo/spec.md) | cianfhoghlaim | 8 NCCA LC subjects × per-subject quest packs × 8 ADK agents × hybrid x402 credential × TanStack Start 2D client |
| [`dagster-5-layer-component-architecture`](specs/dagster-5-layer-component-architecture/spec.md) | shared | 5 KCG Components (Ingestion / Materials / Model Lifecycle / Asset Generation / Agent Operations) + Dagster 1.13+ Declarative Automation + Virtual Assets + State-Backed Components + R1–R4 conformance at scaffold time |
| [`oideachais-pipeline`](specs/oideachais-pipeline/spec.md) | oideachais | Celtic education curriculum pipeline (Dagster + DLT + DuckLake + LanceDB + BAML) |
| [`oideachais-university-deep-extraction`](specs/oideachais-university-deep-extraction/spec.md) | oideachais | Per-university website deep extraction (BAML + DLT + Dagster + CocoIndex v1 + marimo + Cognee cross-archive) — the reusable template for any British Isles university |
| [`cianfhoghlaim-personal-archive-typed-modules`](specs/cianfhoghlaim-personal-archive-typed-modules/spec.md) | cianfhoghlaim | **NEW 2026-08-23**: F-granularity (per-question) typed pipeline that lifts `leabharlann/<university>/` to leaving-cycle feature parity — transferable to any user |
| [`infrastructure-stacks`](specs/infrastructure-stacks/spec.md) | shared | 94 Docker Compose stacks at `bonneagar/stacks/` + stack-doctor + Pangolin + Infisical + Locket + Komodo resource-syncs |
| [`agent-memory-systems`](specs/agent-memory-systems/spec.md) | shared | Cognee + Graphiti + LanceDB + FalkorDB + Memgraph agent memory |
| [`indexing-and-cognition`](specs/indexing-and-cognition/spec.md) | shared | CCC v1 code search + Cognee knowledge graph + OpenCode agent/MCP registry |
| [`knowledge-sync-loop`](specs/knowledge-sync-loop/spec.md) | shared | 5-layer pull-based sync (paths / CCC / Cognee / skills / MCP) + 6 `mise run sync:*` tasks + 3 feedback loops — keeps all 8 knowledge surfaces in sync |
| [`retrospective-cleanup`](specs/retrospective-cleanup/spec.md) | shared | **NEW 2026-08-15**: Retroactive cleanup of the 1959 pre-v7 path drift occurrences (47 auto-fixable + 1912 manual) + the Layer 6 sync:dagster + the safe --fix mode |
| [`dagger-pipelines`](specs/dagger-pipelines/spec.md) | shared | Polyglot CI/CD via Dagger (Python + TS) — 8-step GitOps |
| [`dev-tooling-surfaces`](specs/dev-tooling-surfaces/spec.md) | shared | **NEW 2026-08-19**: The canonical 3-tool developer surface — opencode (4 primary + 9 domain agents) + mise (9 task namespaces + task_templates + file tasks) + openspec (8 subcommands + spec-driven schema). Drives .agents/skills/{opencode,mise,openspec}/, .cocoindex_code/guides.yml, and the openspec/AGENTS.md routing table. |

> **Note:** `tuatha-platform` has been **retired** (2026-07-06 by the
> `2026-07-06-drift-cleanup-and-v4-alignment` change). Its content has
> been absorbed into `cianfhoghlaim-educational-mmo`.

### Priority commands

```bash
openspec list --specs              # list all 97 capability specs (was 96; +1 for dev-tooling-surfaces)
openspec list                      # list all pending changes
openspec view                      # NEW 1.4: interactive dashboard of all specs + changes
openspec status <change-id>        # NEW 1.4: per-artifact completion check
openspec show <change-id|spec>     # NEW 1.4: formatted view of one item
openspec instructions <artifact>   # NEW 1.4: enriched template for one artifact
openspec update                    # NEW 1.10: re-emit OpenSpec instruction files
openspec schemas                   # NEW 1.10: list available workflow schemas (spec-driven, opsx, workspace-planning)
openspec schemas --json            # NEW 1.10: same as above, JSON output
openspec feedback <message>        # NEW 1.10: submit feedback to OpenSpec maintainers
openspec templates                 # NEW 1.10: show resolved template paths for a schema
openspec config                    # NEW 1.10: view and modify global OpenSpec configuration
openspec workspace                 # NEW 1.10: set up and inspect coordination workspaces
openspec context-store             # NEW 1.10: set up and inspect local context stores
openspec initiative                # NEW 1.10: create and list coordinated initiatives
openspec validate <change-id> --strict    # MUST pass before commit
openspec validate --all --strict   # NEW: CI gate (equivalent to mise run openspec:validate-all)
openspec archive <change-id> --yes        # after deploy
```

### Priority skills (6 of 166)

| Skill | When to load |
|:--|:--|
| [`openspec`](../.agents/skills/openspec/SKILL.md) | **NEW**: The 8 standard subcommands + spec delta format + legacy-vs-OPSX note |
| [`data-engineering-pipeline-documentation`](../.agents/skills/data-engineering-pipeline-documentation/SKILL.md) | Router for STATUS.md + REFACTORING.md + per-area READMEs |
| [`dagger-pipelines`](../.agents/skills/dagger-pipelines/SKILL.md) | The 8 callable Dagger functions + the 4 build pipelines |
| [`infrastructure-stacks`](../.agents/skills/infrastructure-stacks/SKILL.md) | The 6-file GOLD_STANDARD pattern for Docker Compose stacks |
| [`agent-memory-systems`](../.agents/skills/agent-memory-systems/SKILL.md) | The 5 memory backends (Cognee + Graphiti + LanceDB + FalkorDB + Memgraph) |
| [`oideachais-cocoindex-v1`](../.agents/skills/oideachais-cocoindex-v1/SKILL.md) | CocoIndex v1 App canonical pattern + 4-rule conformance contract + `_lifespan.py` shared home (REFACTORING.md item 12 enforcement precondition) |
| [`indexing-and-cognition`](../.agents/skills/INDEXING_AND_COGNITION.md) | CCC code search + Cognee knowledge graph (7 clusters) + OpenCode agent/MCP registry (7 agents, 10 MCPs, 13 model-layer agents) |
| [`mise`](../.agents/skills/mise/SKILL.md) | **NEW**: mise-en-place task authoring (TOML tasks + file tasks + task_templates + monorepo mode) |
| [`opencode`](../.agents/skills/opencode/SKILL.md) | **NEW**: OpenCode agent configuration (primary/subagent modes + permission API + MCP providers) |

### Priority mise tasks

The mise.toml task catalogue is now organized by **6 domain namespaces**
(post the 2026-08-19-domain-driven-mise-task-catalog-v1 change).
For openspec work specifically:

```bash
mise run openspec:validate-all     # the canonical CI gate — validate every change + every spec in strict mode (132 items)
mise run openspec:validate <id>   # validate one change with --strict (MUST pass before commit)
mise run openspec:archive <id>    # archive a deployed change (merges deltas into canonical specs)
mise run openspec:view            # interactive dashboard of all specs + changes (1.4+)
mise run openspec:list-specs       # list all 97 capability specs
mise run lint:skills               # validate .agents/skills/ metadata (166 skills pass)
mise run lint:drift-docs           # validate every AGENTS.md number claim against ground truth
mise run sync:all                  # run all 14 sync layers (paths + ccc + cognee + skills + mcp + dagster + drift-docs + spec-agents + baml + stacks + dlt + agents + notebooks + firecrawl)
```

> **Back-compat:** the old bare/colon task names (e.g. `lint`,
> `sync:all`, `dagster:dev`, `cic:stack-doctor`, `iac:health`) remain
> valid for 1 release cycle as aliases.

### OPSX vs legacy schema (NEW 2026-08-19)

OpenSpec 1.4 ships **two schemas**:

- **Legacy `spec-driven` schema** (used by this repo) — proposal.md +
  tasks.md + spec deltas under `openspec/changes/<id>/`. All 78 pending
  + 96 archived changes use this format. Migration would require
  re-archiving every change; not worth the cost.
- **Experimental `OPSX` schema** — external YAML + Markdown templates,
  DAG dependencies, `openspec status <id>` command. Available via
  `openspec schemas` + `openspec schema which --all`. **NOT ADOPTED** in
  this repo (per the `dev-tooling-surfaces` spec Requirement § openspec-
  schema-stability).

The new 1.4 subcommands (`view`, `status`, `show`, `instructions`,
`schemas`) work with both schemas — no migration required to use them.

### ccc code search (for openspec work)

```bash
bun run ccc:search "spec delta format"      # find prior art in the openspec archive
bun run ccc:search "AGENTS.md convention"   # find per-spec AGENTS.md generator pattern
```

### Firecrawl search (for upstream-version verification, added 2026-08-14)

Every openspec change that pins a dependency version in `pyproject.toml` / `package.json` / `mise.toml` MUST cite at least one Firecrawl result proving the version is current. Pair with a `ccc:search` query so both tool names appear in the Langfuse trace.

```bash
# Via the FirecrawlMCPClient wrapper (Pydantic + Langfuse @observe)
python -c "from agents.meaisinfhoghlaim.firecrawl_mcp import FirecrawlMCPClient; c = FirecrawlMCPClient(); print(c.search('Dagster 1.13 release notes', categories=['developer'], limit=3))"

# Or via MCP directly (keyless tier — search/scrape/parse only)
# firecrawl_search "Dagster 1.13 release notes" --categories developer --limit 3
```

### Routing table: when to use firecrawl_search vs ccc:search

| Question | Tool | Output |
|:--|:--|:--|
| "What does our code do for X?" | `bun run ccc:search "X"` | local code |
| "What does our docs corpus say about X?" | `cognee.search(X)` | local docs |
| "What does upstream say about X right now?" | `firecrawl_search` (categories: `["developer"]`) | live web |
| "What does the upstream source code actually say?" | `firecrawl_developer_search` | GitHub issues/PRs/README |
| "Show me the page at <known URL>" | `firecrawl_scrape` | page markdown + summary |
| "Find papers / read passages / citations" | `firecrawl_research_*` | 43M-paper index |
| "Recurring check on a page" | `firecrawl_monitor_*` (deferred to v2) | webhook + email notifications |

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

## Per-spec `AGENTS.md` convention (NEW 2026-07-29)

Per the `repo-hygiene-agent-routing` spec (added by the
`2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1` change),
every `openspec/specs/<name>/` directory ships with a sibling
`AGENTS.md` file (≤30 lines) that follows the canonical 6-section
outline: routing sentence, quick start, key sources, adjacent specs,
DO NOT, skill pointers. The per-spec AGENTS.md is regenerated by
`uv run python scripts/sync/spec_agents.py` (or by `mise run sync:all`)
whenever its `spec.md` is updated.

The anti-drift contract (`centralize-cross-cutting-docs` spec) enforces
this convention via `mise run lint:drift-docs` (the CI gate that
validates every AGENTS.md number claim against ground truth) plus
`.github/workflows/lint-drift-docs.yaml` + the Forgejo mirror.

## Cross-references

- [`specs/repo-hygiene-agent-routing/spec.md`](./specs/repo-hygiene-agent-routing/spec.md) — the per-spec AGENTS.md convention
- [`specs/centralize-cross-cutting-docs/spec.md`](./specs/centralize-cross-cutting-docs/spec.md) — the anti-drift contract
- [`specs/knowledge-sync-loop/spec.md`](./specs/knowledge-sync-loop/spec.md) — the 7-layer sync architecture (paths + ccc + cognee + skills + mcp + drift-docs + dagster)
- [`../AGENTS.md`](../AGENTS.md) — the consolidated cianfhoghlaim AGENTS.md (post-v4)
