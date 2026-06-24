# Tuatha Quadrant — Agent Instructions

> **The British Isles Formative Assessment MMO.** *An
> educational MMO that delivers continuous formative feedback
> (not summative) during quests, mapped to the NCCA / CfE / CfW /
> CCEA / SQA curriculum frameworks. Babylon.js 3D game front-end,
> Rust + SpacetimeDB game engine, TanStack Start web app, and the
> Crypteolas educational-achievement ledger (skill-tree badges,
> not a financial token) — all consolidated into the `tuath` uv
> workspace member.*

## Overview

`tuatha/` is the **British Isles Formative Assessment MMO** quadrant
of the Cianfhoghlaim monorepo. It is a uv workspace member that
contains:

- **Game front-end** — Babylon.js scene graph at `tuatha/game/` for the
  British Isles formative assessment MMO client
- **Game engine** — Rust + SpacetimeDB server at `tuatha/crates/` for
  the MMO server
- **Educational-achievement ledger** — `tuatha/crypteolas/achievements/`
  for the skill-tree badges (per curriculum framework × level) +
  x402 settlement for **gated game features only** (cosmetics,
  premium quests, paid DLC — never for educational content)
- **UI** — TanStack Start front-end at `tuatha/ui/` for the educational
  game and the BAML-driven Celtic content extraction
- **Knowledge graph** — `tuatha/knowledge_graph/` (the Celtic-learning
  graph that the MMO uses for NPC dialogue + quest generation)
- **Celtic language** — `tuatha/gaeilge.md` (Irish) + `tuatha/anam.md`
  (soul/spirit) are the Irish-language content surfaces
- **4 ADK agents** — Canonical implementations live at
  `oideachais/agents/adk/` (Phase 5 refactor). The
  `tuatha/agents/adk/*.py` files are thin re-exports:
  - `celtic_tutor.py` → `celtic_tutor_agent` (Celtic Tutor)
  - `mythology_narrator.py` → `mythology_narrator_agent` (Mythology Narrator)
  - `quest_guide.py` → `quest_guide_agent` (Quest Guide)
  - `research_assistant.py` → `research_assistant_agent` (Research Assistant)
  - `root_agent.py` → `root_agent` (Tuath root + 4 specialists + app + classify_query)

**Phase 6 of the 6-phase refactor plan (2026-06-24):** The
tuatha focus is now **British Isles formative assessment** (not
"Celtic broadly"). The crypto is now **educational
achievements** (skill-tree badges, not a financial token).
The pedagogical framework (5 curriculum frameworks, 4
formative feedback channels, 3 quest types, 4 graduated hint
levels, achievement-ledger schema) is documented in
`.agents/skills/british-isles-formative-assessment/`.

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
| Add a new educational-achievement badge | `tuatha/crypteolas/achievements/` |
| Wire x402 micropayments for a gated game feature | `tuatha/crypteolas/x402.py` (paid features only — never for educational content) |
| Add a new UI component | `tuatha/ui/` (TanStack Start) |
| Add a new BAML extraction for Celtic content | `baml_src/ui_components.baml` or `baml_src/image_generation.baml` |
| Add a new NPC or quest | `tuatha/knowledge_graph/` + `baml_src/ui_components.baml` |
| Add a new Dagster asset for the tuatha code-location | `tuatha/dagster_assets/` |
| Add a new Irish-language content surface | `tuatha/gaeilge.md` + `tuatha/anam.md` |
| Integrate the MMO content with a croilar persona | `croilar/apps/web/` (the `game` subproject) |
| Add a new SpacetimeDB table | `tuatha/crates/game_server/src/tables/` |
| Add a new formative-assessment quest | `.agents/skills/british-isles-formative-assessment/` (pedagogical framework) |
| Modify a 4-agent feedback channel | `oideachais/agents/adk/{celtic_tutor,mythology_narrator,quest_guide,research_assistant,tuatha_root}_agent.py` (canonical; the tuatha files are thin re-exports) |

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

- `tuatha-mmo/SKILL.md` — the MMO tech stack (Babylon.js,
  SpacetimeDB, x402, SIWE, Pent-Elemental Cosmology)
- `british-isles-formative-assessment/SKILL.md` — the
  pedagogical framework (5 curriculum frameworks, 4
  feedback channels, 3 quest types, 4 graduated hint
  levels, achievement-ledger schema) — **NEW in Phase 6**
- `celtic-asset-generation/SKILL.md` — how curriculum
  content becomes in-game assets
- `dagger/SKILL.md` — Dagger CI/CD (the SpacetimeDB Rust build is in
  the Dagger pipeline)
- `devops-architect/SKILL.md` — infrastructure patterns
- `baml/SKILL.md` — BAML schema patterns
- `tanstack-start/SKILL.md` — TanStack Start patterns
- `copilotkit/SKILL.md` — CopilotKit + AG-UI patterns
- `hono/SKILL.md` — Hono API patterns
- `celtic-language-ai/SKILL.md` — Celtic-language model patterns
- `irish-edtech/SKILL.md` — Irish-language AI patterns

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
