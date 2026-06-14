---
title: 'OpenSpec Plans — Status Index'
domain: 'standards'
status: 'stable'
description: 'Status index for openspec/plans/ (research artefacts and deferred roadmaps). Each plan has a status: research | deferred. Deferral plans are moved to docs/00-deploy-plans/.'
read_when:
  - looking for an existing plan before starting a change
  - reviewing what work was deferred
updated: '2026-06-13'
ccc_query_hints:
  - openspec plans status index
  - research deferred roadmap
---

# OpenSpec Plans — Status Index

> `openspec/plans/` holds **research artefacts and deferred roadmaps** —
> not active work. Active work is in `openspec/changes/`.
> See [`docs/00_index.md` §5 OpenSpec workflow](../../docs/00_index.md)
> for the full lifecycle.

## Status: research (kept for traceability)

| Plan | Last touched | Supersedes | Note |
|---|---|---|---|
| `data_engineering_deep_dive.md` | 2026-06-13 | superseded by [`oideachais-pipeline` spec](../specs/oideachais-pipeline/spec.md) + [`data-pipeline` spec](../specs/data-pipeline/spec.md) + [`docs/02-data-platform/data-architecture.md`](../../docs/02-data-platform/data-architecture.md) | keep for the architectural insights |
| `deployment_and_ai_strategy.md` | 2026-06-13 | superseded by [`infrastructure` spec](../specs/infrastructure/spec.md) + [`docs/01-platform-architecture/`](../../docs/01-platform-architecture/) | keep |
| `deployment_stack_strategy.md` | 2026-06-13 | superseded by [`infrastructure-stacks` spec](../specs/infrastructure-stacks/spec.md) | keep |
| `education_audit_plan.md` | 2026-06-13 | **the live one** — points at the post-restructure placeholders we fix in Phase 1 | keep |
| `exponential_improvement_roadmap.md` | 2026-06-13 | research; insights distributed across 4 specs already | keep |
| `final_exponential_strategy.md` | 2026-06-13 | research; superseded by the LLM-stack-hierarchy doc | keep |
| `gcp_ai_optimization_strategy.md` | 2026-06-13 | research; never deployed (we run OCI Ampere A1, not GCP) | keep |
| `infrastructure_deep_dive.md` | 2026-06-13 | superseded by [`infrastructure` spec](../specs/infrastructure/spec.md) | keep |
| `machine_learning_deep_dive.md` | 2026-06-13 | superseded by [`oideachais-pipeline` spec](../specs/oideachais-pipeline/spec.md) + [`data-pipeline` spec](../specs/data-pipeline/spec.md) | keep |
| `package-updates.md` | 2026-06-13 | research (the only plan with substantive content; 277 lines) | keep |
| `web_and_dashboards_deep_dive.md` | 2026-06-13 | research; partially superseded by [`frontend-frameworks` spec](../specs/frontend-frameworks/spec.md) + [`docs/05-web/frontend-topology.md`](../../docs/05-web/frontend-topology.md) | keep |

## Status: deferred → moved to `docs/00-deploy-plans/`

The 5 tangent roadmaps become concrete deploy plans in
[`docs/00-deploy-plans/`](../../docs/00-deploy-plans/) (Phase 5 of the
docs-consolidation plan, completed 2026-06-13). The originals are
archived at `openspec/plans/archive/` for traceability.

| Original plan (now archived) | New deploy plan | Quadrants |
|---|---|---|
| `archive/tangent_1_micro_credentials.md` | `docs/00-deploy-plans/01-micro-credentials.md` | oideachais + meaisinfhoghlaim |
| `archive/tangent_2_generative_tutoring.md` | `docs/00-deploy-plans/02-generative-tutoring.md` | oideachais + meaisinfhoghlaim + croilar |
| `archive/tangent_3_automated_assessment.md` | `docs/00-deploy-plans/03-automated-assessment.md` | oideachais + meaisinfhoghlaim |
| `archive/tangent_4_immersive_content.md` | `docs/00-deploy-plans/04-immersive-content.md` | tuatha + oideachais + meaisinfhoghlaim |
| `archive/tangent_5_policy_simulator.md` | `docs/00-deploy-plans/05-policy-simulator.md` | oideachais only |

The deploy plans are the **canonical** work; the archived tangents are
provenance. New code MUST reference `docs/00-deploy-plans/*.md`, not
`openspec/plans/archive/tangent_*.md`.

## Status: complete (changes that were archived)

The plan-md files for the *complete* changes were archived already
(see `openspec/changes/archive/`).

## How to use this index

1. **Before starting a change**, scan the table above to see if there's
   a plan that already covers the work.
2. If the plan is `research`, it may contain useful architectural
   insights — read it for context.
3. If the plan is `deferred`, check `docs/00-deploy-plans/STATUS.md` to
   see if the deploy plan is now ready to pick up.
4. If the plan is `complete`, ignore (the change is already shipped).

## See also

- [`docs/00-deploy-plans/STATUS.md`](../../docs/00-deploy-plans/STATUS.md) — the deploy-plans index
- [`openspec/specs/`](../specs/) — the 32 canonical capability specs
- [`openspec/changes/`](../changes/) — the 13 active change proposals
