---
title: 'Deploy Plans — Status & Roadmap'
domain: deploy-plan
status: stable
description: 'Index of the 5 active deploy plans for the Cianfhoghlaim platform, each grounded in the 5-quadrant monorepo topology, the LLM stack, and the storage layering.'
read_when:
  - 'choosing which plan to staff first'
  - 'reviewing the deploy-plans pipeline as a whole'
supersedes: []
superseded_by: []
truth: sole
last_touched: 2026-06-13
---

# Deploy Plans — Status & Roadmap

## Purpose

This directory (`docs/00-deploy-plans/`) holds the **canonical deploy
plans** for the 5 forward-looking initiatives that emerged from the
2026-06-13 strategic review (the original "tangents"). Each plan is
grounded in the actual monorepo — 5 quadrants, 8 workspace members,
the LLM stack, the storage layer, the browser automation ladder — and
references specific DLT sources, BAML schemas, Dagster assets, and
agents.

The original `openspec/plans/tangent_*.md` files are kept for
provenance (see `openspec/plans/STATUS.md`) but are **superseded** by
the files in this directory.

## Plans

| # | Plan | Primary quadrant | LLM stack | Storage target | Status |
|:--|:--|:--|:--|:--|:--|
| 01 | [Micro-Credentials & Cross-Border Equivalence Ledger](01-micro-credentials.md) | `oideachais/` + `infrastructure/` | BAML → Cognee | DuckLake writes, MotherDuck reads | draft |
| 02 | [Cross-Lingual Generative Tutoring Engine](02-generative-tutoring.md) | `meaisinfhoghlaim/` + `oideachais/` | BAML → litellm → Cognee → LanceDB | LanceDB Cloud + MotherDuck | draft |
| 03 | [Automated Assessment & Grade Forecasting Oracle](03-automated-assessment.md) | `meaisinfhoghlaim/ocr/` + `oideachais/` | BAML → litellm | DuckLake historical, MotherDuck query | draft |
| 04 | [Immersive Multi-Modal Content Generation](04-immersive-content.md) | `oideachais/` + `meaisinfhoghlaim/` | BAML → litellm → mlflow | DuckLake + MotherDuck Dives | draft |
| 05 | [Cross-Border Policy Impact Simulator](05-policy-simulator.md) | `oideachais/` + `meaisinfhoghlaim/` | BAML → Cognee | DuckLake append-only | draft |

## Shared dependencies

All 5 plans depend on the following foundations (each lives in a
canonical doc):

| Foundation | Doc | Owner |
|:--|:--|:--|
| 5-quadrant topology | `docs/00-core/CLAUDE.md` | Operator |
| 8 workspace members | `docs/00-core/CLAUDE.md` §WORKSPACE | Operator |
| Storage layering (DuckLake / MotherDuck / Iceberg) | `docs/02-data-platform/storage-mental-model.md` | Operator |
| Source registry (8 nations, 7 kinds) | `docs/02-data-platform/cross-domain-registry.md` | `oideachais/sources.yaml` |
| LLM stack (BAML → litellm → Cognee → LanceDB) | `docs/04-ai-ml/llm-stack-hierarchy.md` | `meaisinfhoghlaim/llm_stack/` |
| Browser automation ladder | `docs/03-agents/browser-automation.md` | `infrastructure/browser/` |
| Change detection | `docs/03-agents/change-detection.md` | `infrastructure/stacks/tools/changedetection/` |
| Front-end topology | `docs/05-web/frontend-topology.md` | `oideachais/web/` |

## Build ordering (recommended)

The 5 plans share a common ingestion pipeline (the 8-nation DLT
sources). Plan 01 is the **critical path** because it produces the
canonical `EquivalenceAssertion` and `CrossNationCurriculumSpec` rows
that Plans 02, 04, 05 all consume.

```
Plan 01 ──→ Plan 02 ──→ Plan 04
   │           │
   │           └──→ Plan 03
   │
   └──→ Plan 05
```

- **Plan 01** unblocks everything; it owns the source registry and
  the equivalence matrix.
- **Plan 02** depends on Plan 01's `EquivalenceAssertion` and adds
  the tutoring interaction layer.
- **Plan 03** depends on Plan 01's `MarkingScheme` and Plan 02's
  `ConceptMastery`; it adds the assessment loop.
- **Plan 04** depends on Plan 01's `CrossNationCurriculumSpec` and
  Plan 02's `LearningOutcome`; it adds content synthesis.
- **Plan 05** depends on Plan 01's `CrossNationCurriculumSpec` and
  Plan 02's Cognee graph; it adds the simulator.

## CI gates (Phase 4)

The plans are validated by:

- `bun run validate-docs` — fails if any plan references a legacy namespace
- `bun run validate-openspec-stale` — fails if a plan's underlying
  `openspec/changes/*/proposal.md` is idle >14 days
- `bun run validate-frontmatter` — fails if a plan is missing the
  `truth: sole` (or `partial` / `superseded`) field

## OpenSpec capability specs referenced

Each plan links to the canonical OpenSpec capabilities it exercises:

| Capability | Used by |
|:--|:--|
| `curriculum-ingestion` | Plans 01, 02, 04, 05 |
| `bilingual-content` | Plans 02, 04 |
| `knowledge-graph` | Plans 01, 02, 05 |
| `semantic-search` | Plan 02 |
| `assessment-extraction` | Plan 03 |
| `oideachais-pipeline` | All 5 |

When the underlying capability spec changes, the corresponding plan
should be re-validated. Add a CI step to detect drift:

```yaml
# .github/workflows/deploy-plan-drift.yml
- run: bun run scripts/validate-frontmatter.ts
- run: openspec validate <each referenced spec> --strict
```

## Handoff to operator

To pick up any plan:

1. Read the plan file in full.
2. Read every `## Cross-references` link in the plan (these are the
   minimum-viable context set).
3. Read the corresponding `openspec/specs/*/spec.md` for the
   requirements.
4. Read the SKILL.md files for the relevant skills.
5. Run `bun run validate-docs && bun run validate-frontmatter` to
   confirm no new violations.

## Provenance

| Plan | Derived from (deprecated) |
|:--|:--|
| 01 | `openspec/plans/tangent_1_micro_credentials.md` (politically-framed, kept for provenance) |
| 02 | `openspec/plans/tangent_2_generative_tutoring.md` |
| 03 | `openspec/plans/tangent_3_automated_assessment.md` |
| 04 | `openspec/plans/tangent_4_immersive_content.md` |
| 05 | `openspec/plans/tangent_5_policy_simulator.md` |
