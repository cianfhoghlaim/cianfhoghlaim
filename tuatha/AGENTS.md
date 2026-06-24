# Tuatha Quadrant — Agent Instructions

> **The British Isles Formative Assessment MMO.** *An
> educational MMO that delivers continuous formative feedback
> (not summative) during quests, mapped to the NCCA / CfE / CfW /
> CCEA / SQA curriculum frameworks. Babylon.js 3D game front-end,
> Rust + SpacetimeDB game engine, TanStack Start web app, and the
> Crypteolas educational-achievement ledger (skill-tree badges,
> not a financial token) — all consolidated into the `tuath` uv
> workspace member.*

## Priority quick reference

The 8 priority skills, the 4 priority commands, and the 1
priority openspec spec at a glance. **Read this first**; the
rest of the file is the full 4-stream routing.

### Priority skills (11 of 120)

| Skill | When to load |
|:--|:--|
| [`babylonjs`](../.agents/skills/babylonjs/SKILL.md) | Babylon.js 7 + WebGPU (the MMO client renderer) |
| [`tuatha-mmo`](../.agents/skills/tuatha-mmo/SKILL.md) | The Tuatha Celtic MMO + Crypteolas achievement-ledger (4 sub-modules) |
| [`pent-elemental-cosmology`](../.agents/skills/pent-elemental-cosmology/SKILL.md) | The 5 Pent-Elemental realms (Spirit / Water / Fire / Earth / Air) + Anam Cara + Geasa |
| [`tuatha-achievement-ledger`](../.agents/skills/tuatha-achievement-ledger/SKILL.md) | The 8-field skill-tree badge schema + the 5 masteries + the cryptographic evidence chain |
| [`tuatha-mcp-server-tools`](../.agents/skills/tuatha-mcp-server-tools/SKILL.md) | The 5 MCP tools + the canonical home + the broken-import bug + the shim pattern |
| [`dagger`](../.agents/skills/dagger/SKILL.md) | Dagger CI/CD (the SpacetimeDB Rust build is in the Dagger pipeline) |
| [`baml`](../.agents/skills/baml/SKILL.md) | BAML extraction for Celtic content (image_generation, ui_components) |
| [`tanstack-start`](../.agents/skills/tanstack-start/SKILL.md) | TanStack Start (the educational game front-end) |
| [`copilotkit`](../.agents/skills/copilotkit/SKILL.md) | CopilotKit + AG-UI (the agent UI for the MMO) |
| [`hono`](../.agents/skills/hono/SKILL.md) | Hono API (the unified API surface) |
| [`celtic-language-ai`](../.agents/skills/celtic-language-ai/SKILL.md) | Celtic-language model catalog (GaBERT, Helsinki OPUS-MT, NLLB-200) |

### ccc + openspec commands

```bash
bun run ccc:search "SpacetimeDB table migration"      # semantic code search
openspec list --specs                                 # 32 specs total
openspec validate <change-id> --strict                # MUST pass before commit
openspec archive <change-id> --yes                    # after deploy
```

### Priority openspec spec for tuatha

| Spec | One-liner |
|:--|:--|
| `tuatha-platform` | The 4 sub-modules + the BAML Celtic content extraction + the croilar consumer integration |

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
- `pent-elemental-cosmology/SKILL.md` — the 5 Pent-Elemental
  realms (Spirit / Water / Fire / Earth / Air) + Anam Cara +
  Geasa + 5 SpacetimeDB tables + 5 quest tracks +
  Babylon.js scene graph — **NEW in round 10**
- `tuatha-achievement-ledger/SKILL.md` — the 8-field
  skill-tree badge schema + the 5 Pent-Elemental realm
  masteries + the cryptographic evidence chain +
  the cross-quest retrieval — **NEW in round 10**
- `tuatha-mcp-server-tools/SKILL.md` — the 5 MCP tools +
  the canonical home in oideachais + the broken-import
  bug + the shim pattern + the 4 transports —
  **NEW in round 10**
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
