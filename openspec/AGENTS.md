# OpenSpec Instructions for Cianfhoghlaim

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

## Capability Specs (25)

The Cianfhoghlaim platform has **25 capability specs** organised into
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
| `ireland-primary-jc-dlt-baml` | oideachais | Ireland Primary + Junior Cycle dlt + BAML loop |
| `official-media-pipeline` | oideachais | Instagram-export → British-Isles government source enrichment (DLT + BAML `ClassifyOfficialMedia` + 4-lookup resolver) |
| `official-media-fediverse` | oideachais | Mastodon webfinger + Bluesky xrpc + Wikipedia + Companies House / CRO lookup (pure library) |
| `official-media-marimo` | oideachais | Marimo mission control + TanStack Start `/official-media` + Cognee dataset `oideachais_official_media` |
| `celtic-data-engineering-pipeline` | oideachais | dbt-duckdb project at `oideachais/dbt_project/` + `CelticDagsterDbtTranslator` + 2 marimo notebooks under `meaisinfhoghlaim/marimo/` (the `celtic-data-engineering-patterns` change) |
| `meaisinfhoghlaim-platform` | meaisinfhoghlaim | 10 sub-packages + 4 heartbeat dagster assets + Dagster code-location |
| `meaisinfhoghlaim-agent-frameworks` | meaisinfhoghlaim | 12 specialised agents (Root, Curriculum, Translation, Corpus, etc.) |
| `meaisinfhoghlaim-ocr-htr` | meaisinfhoghlaim | 10 OCR models across 6 backends (Pylaia, TrOCR, PaddleOCR, Tesseract, dots.ocr, VLM) |
| `gradio-ensemble-pattern` | meaisinfhoghlaim | `build_ensemble_interface()` helper + `push_model_to_hub()` HF Hub push helper (the ensemble UI pattern from `spaces/anti-phish/6_Gradio_Front_End.ipynb`) |
| `tuatha-platform` | tuatha | Celtic MMO (Babylon.js + Rust + SpacetimeDB) + crypteolas crypto platform |
| `croilar-portfolio` | croilar | Public TanStack Start site — multi-persona (aleyum, cianfhoghlaim, carlcashman) |
| `croilar-data-engineering` | croilar | Dagster + DLT + CocoIndex + BAML pipelines for croilar personas |
| `croilar-cv-extraction` | croilar | BAML extraction of the author's CV / achievements / teaching PDFs |
| `agent-memory-systems` | shared | Cognee + Graphiti + LanceDB + FalkorDB + Memgraph agent memory |
| `agent-observability` | shared | Langfuse + MLflow + RAGAS + Logfire + Datadog |
| `agentic-frontend-frameworks` | shared | TanStack Start + CopilotKit + AG-UI + Hono + Convex |
| `dagger-pipelines` | shared | Polyglot CI/CD via Dagger (Python + TS) — 8-step GitOps |
| `infrastructure-stacks` | shared | 70+ Docker Compose stacks + stack-doctor.sh + Pangolin + Infisical + Locket |
| `data-engineering-pipeline-documentation` | shared | oideachais/STATUS.md + oideachais/REFACTORING.md + per-area READMEs |
| `spaces-cicd-pipeline` | shared | Reusable GH Action at `infrastructure/ci/spaces-sync.yml` for publishing any `spaces/*/` dir to a HF Space (gradio / docker / static SDKs) |
| `celtic-data-engineering-pipeline` | shared | dbt-duckdb at `oideachais/dbt_project/` + marimo notebooks at `meaisinfhoghlaim/marimo/` (the `celtic-data-engineering-patterns` change) |
| `gradio-ensemble-pattern` | shared | `meaisinfhoghlaim/pipelines/ensemble_gradio.py` + `spaces/_common/hf_hub_push.py` (sister to `celtic-data-engineering-patterns`) |
| `workflow-automation` | team | n8n + LLM pipelines (OpenCode Go API) |
| `task-management` | team | Vikunja kanban + Gantt + list + team sharing |
| `scheduling` | team | cal-diy team + per-member booking pages |
| `chunkhound-code-search` | tooling | Semantic code search with MVCC |
| `documentation` | tooling | Canonical docs/ structure (8 numbered domains), frontmatter schema |

### Quadrant map (4 top-level quadrants)

| Quadrant | Path | Wheel name | README | AGENTS.md |
|:--|:--|:--|:--|:--|
| **Oideachais** | `oideachais/` | `oideachais` | `oideachais/README.md` | `oideachais/AGENTS.md` |
| **Meaisínfhoghlaim** | `meaisinfhoghlaim/` | `meaisinfhoghlaim` | `meaisinfhoghlaim/README.md` | `meaisinfhoghlaim/AGENTS.md` |
| **Tuatha** | `tuatha/` | `tuath` (uv) | `tuatha/README.md` | `tuatha/AGENTS.md` |
| **Croílár** | `croilar/` | (TypeScript) | `croilar/README.md` | `croilar/AGENTS.md` |

## Adding a New Capability

When a change introduces a new capability (not a MODIFIED of an existing one), follow this recipe:

1. **Add the capability** to the relevant section in [`project.md`](./project.md)
2. **Create a capability spec** at `openspec/specs/<capability>/spec.md` with at least 1 Requirement and 1 Scenario
3. **In the change's `specs/<capability>/spec.md`** (the delta file), use `## ADDED Requirements` header and a `### Requirement:` block with `#### Scenario:` children
4. **Validate with `openspec validate --strict`** — every Requirement needs at least one Scenario
5. **Cross-reference** related skills at `.agents/skills/<relevant-skill>/SKILL.md`

## Adding a New Docker Compose Stack

1. Create the directory: `infrastructure/stacks/<category>/<name>/`
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
- [`../oideachais/AGENTS.md`](../oideachais/AGENTS.md) — oideachais quadrant
- [`../meaisinfhoghlaim/AGENTS.md`](../meaisinfhoghlaim/AGENTS.md) — meaisinfhoghlaim quadrant
- [`../tuatha/AGENTS.md`](../tuatha/AGENTS.md) — tuatha quadrant
- [`../croilar/AGENTS.md`](../croilar/AGENTS.md) — croilar quadrant
