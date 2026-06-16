# Croílár Quadrant — Agent Instructions

> **Multi-Persona Portfolio Platform.** *The personal portfolio of
> Cian de Búrca, refactored as a multi-persona, self-hosted, full-stack
> TypeScript + Python platform that doubles as a reference
> implementation for the rest of `kings_college_galway`.*

## Overview

`croilar/` is the **multi-persona portfolio + CV + data engineering
subproject** quadrant of the Cianfhoghlaim monorepo. It is a bun
workspace (TypeScript) that contains:

- **Public persona site** — TanStack Start at `croilar/apps/web/`
  serving 3 personas (aleyum, cianfhoghlaim, carlcashman) with
  bilingual (EN/GA) routing
- **Self-hosted platform dashboard** — TanStack Start at
  `croilar/apps/portal/` for the croilar admin + collab surfaces
  (auth-gated, Better Auth + SIWE + x402 + org-scoped JWT)
- **Storybook** — TanStack Start at `croilar/apps/storybook/` (UI
  explorer)
- **Agent OS** — `croilar/agent_os/` for the croilar-specific agents
  (separate from `meaisinfhoghlaim/agents/` which is the AI/ML
  quadrant's model-layer)
- **API** — Hono at `croilar/api/` (the unified API surface for the
  persona site + portal + storybook)
- **BAML schemas** — `croilar/baml_src/` (the persona-specific
  extractions)
- **Data engineering** — Dagster + DLT + CocoIndex + BAML pipelines
  at `croilar/dagster_assets/`, `croilar/dlt_sources/`,
  `croilar/cocoindex_flows/`, `croilar/baml/`
- **Notebooks** — Marimo at `croilar/notebooks/`

The 3 personas (aleyum, cianfhoghlaim, carlcashman) each have a
personal-portfolio surface + a `wow` or `Hades II` content surface
that consumes the tuatha MMO content.

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new persona | `croilar/config/personas.yaml` + `croilar/apps/web/src/routes/` |
| Add a new public route | `croilar/apps/web/src/routes/` (TanStack Start file-based routing) |
| Add a new portal route | `croilar/apps/portal/src/routes/` (auth-gated) |
| Add a new agent (croilar-specific) | `croilar/agent_os/` (separate from `meaisinfhoghlaim/agents/`) |
| Add a new BAML extraction | `croilar/baml_src/` + `croilar/baml/` |
| Add a new Dagster asset | `croilar/dagster_assets/` |
| Add a new DLT source | `croilar/dlt_sources/` |
| Add a new CocoIndex flow | `croilar/cocoindex_flows/` |
| Add a new API route | `croilar/api/` (Hono) |
| Add a new Marimo notebook | `croilar/notebooks/` |
| Add a new Convex function | `croilar/convex/` |
| Add a new i18n translation | `croilar/packages/i18n/src/` (bilingual EN/GA) |
| Add a new Wow / Hades II content surface | `tuatha/wow/` or `tuatha/Hades II/` (consumes the tuatha MMO content) |

## openspec specs that govern croilar

The 3 openspec specs for the croilar quadrant are:

- `croilar-portfolio` — the public TanStack Start site + the 3 personas
- `croilar-data-engineering` — the Dagster + DLT + CocoIndex + BAML
  pipelines for the croilar personas
- `croilar-cv-extraction` — the BAML extraction of the author's CV /
  achievements / teaching PDFs

Plus the shared specs (4):

- `agentic-frontend-frameworks` — TanStack Start + CopilotKit + AG-UI
- `agent-memory-systems` — Cognee + Graphiti + LanceDB + FalkorDB
- `agent-observability` — Langfuse + MLflow + RAGAS + Logfire + Datadog
- `dagger-pipelines` — Polyglot CI/CD via Dagger

And the related specs:

- `tuatha-platform` — the Celtic MMO + crypto content that croilar
  consumes (for the `wow` / `Hades II` subprojects)
- `oideachais-leabharlann` — the leabharlann corpus that croilar
  consumes (for the author's CV / teaching / identity PDFs)

## Related skills (in `.agents/skills/`)

- `tanstack-start/SKILL.md` — TanStack Start patterns
- `copilotkit/SKILL.md` — CopilotKit + AG-UI patterns
- `hono/SKILL.md` — Hono API patterns
- `convex/SKILL.md` — Convex patterns
- `dagster/SKILL.md` — Dagster asset patterns
- `dlt/SKILL.md` — DLT source patterns
- `baml/SKILL.md` — BAML schema patterns
- `cocoindex/SKILL.md` — CocoIndex v1 patterns
- `marimo/SKILL.md` — Marimo notebook patterns

## Cross-references

- [`croilar/README.md`](README.md) — the user-facing overview
- [`croilar/sources.md`](sources.md) — the croilar data source registry
- [`croilar/DEVELOPMENT.md`](DEVELOPMENT.md) — the dev quick-start
- [`croilar/prompts.md`](prompts.md) — the croilar BAML prompts
- [`oideachais/AGENTS.md`](../oideachais/AGENTS.md) — the oideachais
  quadrant (upstream of the leabharlann data)
- [`meaisinfhoghlaim/AGENTS.md`](../meaisinfhoghlaim/AGENTS.md) — the
  AI/ML quadrant (the model-layer agents)
- [`tuatha/AGENTS.md`](../tuatha/AGENTS.md) — the MMO + crypto quadrant
  (consumed by the croilar `wow` / `Hades II` subprojects)
- [`../openspec/AGENTS.md`](../openspec/AGENTS.md) — openspec workflow
- [`../AGENTS.md`](../AGENTS.md) — root agent instructions
