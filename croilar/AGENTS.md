# Croílár Quadrant — Agent Instructions

> **Multi-Persona Portfolio Platform.** *The personal portfolio of
> Cian de Búrca, refactored as a multi-persona, self-hosted, full-stack
> TypeScript + Python platform that doubles as a reference
> implementation for the rest of `kings_college_galway`.*

## Priority quick reference

The 8 priority skills, the 4 priority commands, the 5 user-named
compose stacks, and the 3 priority openspec specs at a glance.
**Read this first**; the rest of the file is the full 3-persona
routing.

### Priority skills (8 of 108)

| Skill | When to load |
|:--|:--|
| [`tanstack-start`](../.agents/skills/tanstack-start/SKILL.md) | TanStack Start (the public persona site + portal + storybook) |
| [`copilotkit`](../.agents/skills/copilotkit/SKILL.md) | CopilotKit + AG-UI (the agent UI for the portal) |
| [`hono`](../.agents/skills/hono/SKILL.md) | Hono API (the unified API surface for web + portal + storybook) |
| [`convex`](../.agents/skills/convex/SKILL.md) | Convex real-time backend (the auth + portal surfaces) |
| [`better-auth`](../.agents/skills/better-auth/SKILL.md) | BetterAuth OIDC + SIWE + 2FA (the auth layer) |
| [`baml`](../.agents/skills/baml/SKILL.md) | BAML extraction (the persona-specific schemas) |
| [`dagster`](../.agents/skills/dagster/SKILL.md) | Dagster asset patterns (the croilar data engineering) |
| [`dlt`](../.agents/skills/dlt/SKILL.md) | DLT source patterns (the 12 croilar DLT pipelines) |

### ccc + openspec commands

```bash
bun run ccc:search "persona routing table"             # semantic code search
openspec list --specs                                 # 32 specs total
openspec validate <change-id> --strict                # MUST pass before commit
openspec archive <change-id> --yes                    # after deploy
```

### Priority compose stacks (5 user-named croilar stacks)

| Stack | Port | Purpose |
|:--|--:|:--|
| `croilar-web` | per Komodo | The public persona site (TanStack Start) |
| `croilar-portal` | per Komodo | The self-hosted platform dashboard (auth-gated) |
| `croilar-dagster` | per Komodo | The croilar-scoped Dagster code-location |
| `croilar-hono-api` | per Komodo | The Hono API (Bun) |
| `croilar-marimo` | per Komodo | The croilar-scoped Marimo notebooks |

### Priority openspec specs for croilar

| Spec | One-liner |
|:--|:--|
| `croilar-portfolio` | Public TanStack Start site — multi-persona (aleyum, cianfhoghlaim, carlcashman) |
| `croilar-data-engineering` | Dagster + DLT + CocoIndex + BAML pipelines for croilar personas |
| `croilar-cv-extraction` | BAML extraction of the author's CV / achievements / teaching PDFs |

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

## Feedback loop (project → openspec → skill)

Per the `skills-as-project-docs` openspec change, this quadrant
participates in the formal feedback loop:

1. **When an openspec change is archived**, the canonical skill
   gets a "Post-archive update: YYYY-MM-DD-..." note in its
   "Pair this skill with" section.
2. **When this quadrant changes a BAML extraction / DLT source
   / Dagster asset**, the corresponding skill (`baml/SKILL.md`,
   `dlt/SKILL.md`, `dagster/SKILL.md`) gets a 1-line addition
   to its "When to use this skill" section.
3. **When this quadrant's `STATUS.md` / `REFACTORING.md` /
   README.md changes**, the
   `data-engineering-pipeline-documentation/SKILL.md` gets a
   link to the new content.

The lint script `mise run lint:skills` enforces the 4 metadata
rules (frontmatter, name match, description length, line count)
on every skill in `.agents/skills/`.
