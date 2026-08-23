# `tuatha-british-isles-mmo` — Agent Routing

> `tuatha-british-isles-mmo` is the canonical capability for the
> **Tuatha** project — the British Isles Formative Assessment
> MMO. The implementation lives at
> `/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/`
> (the new independent sub-project, soon to be the GitHub repo at
> `github.com/cianmacandeisigh/tuatha.git`).

## Routing

Load this AGENTS.md when the parent spec (`./spec.md`) is in scope.
Use it to find the most relevant mise tasks + skills + adjacent files
without re-reading the full spec.

## Quick start

```bash
# The new tuatha project (Phase 3 build time)
cd /Users/cianmacandeisigh/dev/kings_college_galway/tuatha/
cat README.md                                # the canonical British Isles MMO README
cat BUILD_PLAN.md                            # the per-step execution plan
# (the actual build happens in subsequent turns per the BUILD_PLAN.md)
```

## Key sources

- `openspec/specs/tuatha-british-isles-mmo/spec.md` — the canonical spec
- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — the spec
  that the new tuatha implements
- `tuatha/CONSOLIDATION_PLAN.md` — the high-level consolidation plan
- `tuatha/BUILD_PLAN.md` — the per-step execution plan
- `agents/agent_registry.py:AGENT_REGISTRY` — the registration
  for the 14 main agents + the 8 NCCA subject specialists (re-routed)

## Adjacent specs

- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — the
  spec the new tuatha implements
- `openspec/specs/tuatha-platform/spec.md` — the DEPRECATED
  spec (superseded by cianfhoghlaim-educational-mmo)
- `openspec/specs/repo-hygiene-agent-routing/spec.md` — the
  per-spec AGENTS.md convention

## DO NOT

- **Never** add back the Pent-Elemental Cosmology + Babylon.js +
  SpacetimeDB + Crypteolas + Anam Cara + Brown Ajah theming —
  these are HARD-ARCHIVED per the consolidation change
- **Never** create a per-app `apps/<app>/apps/api/src/` for
  CopilotKit actions — they live at `tuatha/web/hono-api/src/routes/copilotkit/`
- **Never** hardcode a model string in any extractor — route
  through `MODEL_REGISTRY.resolve(family, role)`
- **Never** use a Plan B or Plan C Firecrawl tool when the
  keyless tier is active (Plan A is the default)
- **Never** commit a copyrighted comic panel image, animation
  frame still, or game screenshot to the repo (the
  `shippable: false` invariant — the descriptor is
  description-only)
- **Never** declare `shippable_default: true` without explicit
  operator override
- **Never** add a new source without a `source.yaml` manifest
- **Never** skip the `legal_notes` field in any `source.yaml`
- **Never** use "Wikipedia Foundation" as `rights_holder` — use
  the original publisher of the official document (e.g.,
  "An Garda Síochána", "Metropolitan Police Service", "Crown
  copyright")

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`ccc`](../.agents/skills/ccc/SKILL.md) | for semantic code search across the new tuatha/ project |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | MODEL_REGISTRY + schema + codegen patterns |
| [`british-isles-formative-assessment`](../.agents/skills/british-isles-formative-assessment/SKILL.md) | the 5 curriculum frameworks + the 4 feedback channels |
| [`baml`](../.agents/skills/baml/SKILL.md) | BAML extraction patterns + the 8-stage BAML lifecycle |
| [`dlt`](../.agents/skills/dlt/SKILL.md) | DLT source patterns + the `source.yaml` manifest |
| [`dagster`](../.agents/skills/dagster/SKILL.md) | the 5-layer KCG Component Architecture |
| [`agent-fleet-orchestration`](../.agents/skills/agent-fleet-orchestration/SKILL.md) | the 12-agent fleet wiring + the 5-framework runtime + the LiteLLM routing keyword map |
| [`dignified-python`](../.agents/skills/dignified-python/SKILL.md) | production Python standards |
| [`motherduck`](../.agents/skills/motherduck/SKILL.md) | the lakehouse / DuckDB / MotherDuck query surface |

<!-- generated: 2026-08-25 by 2026-08-25-tuatha-british-isles-mmo-consolidation-v1; do not hand-edit -->
