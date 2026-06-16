# Tuatha Quadrant — Agent Instructions

> **The Celtic Educational MMO + Crypto Platform.** *Educational MMO
> front-end, BAML-driven Celtic content extraction, Rust + SpacetimeDB
> game engine, and the crypteolas crypto data platform — all
> consolidated into the `tuath` uv workspace member.*

## Overview

`tuatha/` is the **Celtic educational MMO + crypto platform** quadrant
of the Cianfhoghlaim monorepo. It is a uv workspace member that contains:

- **Game front-end** — Babylon.js scene graph at `tuatha/game/` for the
  Celtic educational MMO client
- **Game engine** — Rust + SpacetimeDB server at `tuatha/crates/` for
  the MMO server
- **Crypto data platform** — `tuatha/crypteolas/` for the in-game
  currency (CELT) and the Bitcoin / Ethereum / Solana / SpacetimeDB
  settlement layer
- **UI** — TanStack Start front-end at `tuatha/ui/` for the educational
  game and the BAML-driven Celtic content extraction
- **Knowledge graph** — `tuatha/knowledge_graph/` (the Celtic-learning
  graph that the MMO uses for NPC dialogue + quest generation)
- **Celtic language** — `tuatha/gaeilge.md` (Irish) + `tuatha/anam.md`
  (soul/spirit) are the Irish-language content surfaces

The consumer relationship to croilar:

- The croilar personal-portfolio platform has a `game` subproject that
  consumes the tuatha MMO content.
- The 3 croilar personas (aleyum, cianfhoghlaim, carlcashman) each have
  a `wow` or `Hades II` content surface (see `tuatha/wow/` and
  `tuatha/Hades II/`).
- The croilar `wow` content is integrated with the tuatha Babylon.js
  scene.

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new MMO scene | `tuatha/game/scenes/` (Babylon.js) |
| Add a new MMO server module | `tuatha/crates/game_server/src/` (Rust + SpacetimeDB) |
| Add a new crypto settlement rule | `tuatha/crypteolas/` |
| Add a new UI component | `tuatha/ui/` (TanStack Start) |
| Add a new BAML extraction for Celtic content | `baml_src/ui_components.baml` or `baml_src/image_generation.baml` |
| Add a new NPC or quest | `tuatha/knowledge_graph/` + `baml_src/ui_components.baml` |
| Add a new Dagster asset for the tuatha code-location | `tuatha/dagster_assets/` |
| Add a new Irish-language content surface | `tuatha/gaeilge.md` + `tuatha/anam.md` |
| Integrate the MMO content with a croilar persona | `croilar/apps/web/` (the `game` subproject) |
| Add a new SpacetimeDB table | `tuatha/crates/game_server/src/tables/` |

## openspec spec that governs tuatha

The single openspec spec for the tuatha quadrant is:

- `tuatha-platform` — the 4 sub-modules + the BAML Celtic content
  extraction + the croilar consumer integration

Plus the shared specs (4):

- `agentic-frontend-frameworks` — TanStack Start + CopilotKit + AG-UI
- `agent-memory-systems` — Cognee + Graphiti + LanceDB + FalkorDB
- `agent-observability` — Langfuse + MLflow + RAGAS + Logfire + Datadog
- `dagger-pipelines` — Polyglot CI/CD via Dagger

## Related skills (in `.agents/skills/`)

- `dagger/SKILL.md` — Dagger CI/CD (the SpacetimeDB Rust build is in
  the Dagger pipeline)
- `devops-architect/SKILL.md` — infrastructure patterns
- `baml/SKILL.md` — BAML schema patterns
- `tanstack-start/SKILL.md` — TanStack Start patterns
- `copilotkit/SKILL.md` — CopilotKit + AG-UI patterns
- `hono/SKILL.md` — Hono API patterns
- `celtic-language-ai/SKILL.md` — Celtic-language model patterns

## Cross-references

- [`tuatha/README.md`](README.md) — the user-facing overview
- [`tuatha/dg.toml`](dg.toml) — the local Dagster code-location config
- [`tuatha/gaeilge.md`](gaeilge.md) — Irish-language content
- [`tuatha/anam.md`](anam.md) — Irish soul/spirit content
- [`oideachais/AGENTS.md`](../oideachais/AGENTS.md) — the oideachais
  quadrant
- [`meaisinfhoghlaim/AGENTS.md`](../meaisinfhoghlaim/AGENTS.md) — the
  AI/ML quadrant
- [`croilar/AGENTS.md`](../croilar/AGENTS.md) — the portfolio quadrant
  (the consumer of tuatha content)
- [`../openspec/AGENTS.md`](../openspec/AGENTS.md) — openspec workflow
- [`../AGENTS.md`](../AGENTS.md) — root agent instructions
