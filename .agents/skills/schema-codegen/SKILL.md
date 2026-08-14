---
name: schema-codegen
description: The schema-driven codegen pipeline that takes BAML .baml files as the source of truth and emits Convex schemas + CopilotKit actions + AG-UI event types + per-subject TanStack Start routes for all 60 subjects × 4 stages. Use when adding a new BAML function, wiring a new schema, generating CopilotKit actions for a subject, or building the per-subject web surface. Triggers: 'BAML', 'Zod schema', 'Convex schema', 'CopilotKit actions', 'AG-UI types', 'per-subject routes', 'codegen', 'schema-driven codegen', '60 subjects', 'schema:generate'.
---

# Schema-Driven Codegen Pipeline

> **The canonical BAML → Zod → Convex → CopilotKit → AG-UI pipeline.**
> Added by the
> [2026-08-13-web-monorepo-consolidation-and-agent-integration-v1](https://github.com/cianfhoghlaim/cianfhoghlaim)
> change (Phase O).

## What this pipeline does

The pipeline takes the BAML `.baml` files at `baml_src/` as the
**canonical source of truth** and emits 5 categories of artifacts:

1. **TypeScript types + Zod schemas** (`baml_client/typescript/...`)
2. **Convex table definitions** (`web/apps/oideachais-dashboard/convex/<stage>/<subject>.ts`)
3. **CopilotKit v2 action registries** (`web/hono-api/src/routes/copilotkit/<stage>/<subject>.ts` + `web/apps/oideachais/src/lib/copilotkit/<stage>/<subject>.ts`)
4. **AG-UI protocol event type wrappers** (`web/apps/oideachais/src/lib/ag-ui/<stage>/<subject>.ts`)
5. **Per-subject TanStack Start routes** (`web/apps/oideachais/routes/<stage>/<subject>/{index,$topicId}.tsx`)

The pipeline is **idempotent** — running it twice on the same input
produces byte-identical output.

## Quick start

```bash
# Run the full pipeline for all 60 subjects × 4 stages
mise run codegen:all

# Dry-run (preview without writing files)
mise run codegen:all:dry-run

# Run for one subject
mise run codegen:subject mathematics

# Run for one stage
mise run codegen:stage lc

# Run a single step (1-5)
bun run scripts/schema-codegen/index.ts --step 3
```

## The 5 sub-generators

| Step | Script | Output |
|:--|:--|:--|
| 1 | `baml-to-ts.ts` | `baml_client/typescript/...` + `codegen-manifest.json` |
| 2 | `convex-from-zod.ts` | `web/apps/oideachais-dashboard/convex/<stage>/<subject>.ts` |
| 3 | `copilotkit-actions.ts` | `web/hono-api/src/routes/copilotkit/<stage>/<subject>.ts` + `web/apps/oideachais/src/lib/copilotkit/<stage>/<subject>.ts` |
| 4 | `ag-ui-types.ts` | `web/apps/oideachais/src/lib/ag-ui/<stage>/<subject>.ts` |
| 5 | `per-subject-routes.ts` | `web/apps/oideachais/routes/<stage>/<subject>/{index,$topicId,AGENTS}.tsx\|md` |

## The 60-subject matrix

The pipeline covers 60 subjects × 4 stages:

- **14 LC subjects** (Mathematics, Chemistry, Physics, Biology, English, Gaeilge, French, History, Geography, Business, Accounting, Art, Music, Computer Science)
- **8 JC subjects** (Mathematics, English, Gaeilge, Science, History, Geography, French, Business)
- **9 GCSE subjects** (Mathematics, English Literature, English Language, Biology, Chemistry, Physics, History, Geography, Modern Foreign Languages)
- **15+ A-Level subjects** (Mathematics, Further Mathematics, Chemistry, Biology, Physics, English Literature, English Language, History, Geography, Psychology, Economics, Business, Politics, Sociology, Modern Foreign Languages)

Each subject has:

- 8 BAML extraction functions (`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`, `ExtractMarkingScheme`, `ExtractCrossLinguistic`, `ExtractSyllabusDiagram`, `ExtractLearningOutcome`, `ExtractKeyTerm`, `ExtractTopicGraph`)
- 1 Convex table schema (with `app + stage + subject` field filter)
- 13 CopilotKit actions (`get_syllabus_topics`, `get_exam_papers`, `get_marking_schemes`, `get_topic_detail`, `get_cross_jurisdictional_equivalences`, `semantic_search`, `extract_syllabus_from_pdf`, `save_annotation`, `track_progress`, `get_study_plan`, `compare_curricula`, `get_glossary_term`, `extract_learning_outcome`)
- 1 AG-UI event types file (10 typed wrappers + 1 RunAgentInput + 1 Tools interface + 1 Event union)
- 1 TanStack Start landing route + 1 topic detail route + 1 per-subject AGENTS.md

## Configuration

| Flag | Description |
|:--|:--|
| `--subject <slug>` | Run for one subject (e.g. `--subject mathematics`) |
| `--stage <stage>` | Run for one stage (`lc` \| `jc` \| `gcse` \| `a-level`) |
| `--step <1-5>` | Run a single step |
| `--dry-run` | Preview without writing files |
| `--root <path>` | Override the repo root |

## Key sources

| Path | Why it matters |
|:--|:--|
| `scripts/schema-codegen/index.ts` | The orchestrator (calls the 5 sub-generators) |
| `scripts/schema-codegen/baml-to-ts.ts` | Step 1 — BAML → TypeScript types |
| `scripts/schema-codegen/convex-from-zod.ts` | Step 2 — Convex table definitions |
| `scripts/schema-codegen/copilotkit-actions.ts` | Step 3 — CopilotKit v2 actions |
| `scripts/schema-codegen/ag-ui-types.ts` | Step 4 — AG-UI 17-event-type wrappers |
| `scripts/schema-codegen/per-subject-routes.ts` | Step 5 — TanStack Start routes |
| `baml_src/<area>/<stage>/<subject>/` | The BAML source (the canonical truth) |
| `scripts/_zod-from-duckdb.ts` | The DuckDB → Zod mapping (the existing R30 codegen) |
| `scripts/schema-generate.ts` | The existing lineage + DuckDB → Zod codegen (extended by step 2) |
| `scripts/schema-validate.ts` | The CI drift gate (validates schema codegen output) |

## Adjacent specs

- [`schema-driven-codegen`](../../openspec/specs/schema-driven-codegen/spec.md) — the canonical contract
- [`per-subject-coverage`](../../openspec/specs/per-subject-coverage/spec.md) — the 60-subject matrix
- [`per-subject-agents`](../../openspec/specs/per-subject-agents/spec.md) — the 60 per-subject agents
- [`tanstack-ai-agui-integration`](../../openspec/specs/tanstack-ai-agui-integration/spec.md) — TanStack AI + AG-UI compliance
- [`web-monorepo-consolidation`](../../openspec/specs/web-monorepo-consolidation/spec.md) — the consolidated web structure
- [`centralized-model-registry`](../../openspec/specs/centralized-model-registry/spec.md) — the model + schema registry

## DO NOT

- **Never** edit the generated files by hand — re-run the pipeline
- **Never** add a BAML function without re-running `mise run codegen:all`
- **Never** bypass the pipeline by writing artifacts directly
- **Never** add per-subject files outside the canonical structure

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`centralized-registry`](../centralized-registry/SKILL.md) | The model + schema registry that the codegen reads from |
| [`schema-codegen`](../schema-codegen/SKILL.md) | This skill (the schema-driven codegen pipeline) |
| [`tanstack-start`](../tanstack-start/SKILL.md) | TanStack Start file-based routing |
| [`baml`](../baml/SKILL.md) | The BAML extraction framework |
| [`cocoindex`](../cocoindex/SKILL.md) | The CocoIndex v1 embedding layer |
| [`agentic-frontend-frameworks`](../agentic-frontend-frameworks/SKILL.md) | TanStack Start + CopilotKit + AG-UI + Hono + Convex |

<!-- generated: 2026-08-13 (per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change, Phase O) -->
