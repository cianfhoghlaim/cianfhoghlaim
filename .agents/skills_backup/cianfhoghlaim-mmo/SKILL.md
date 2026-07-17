---
name: cianfhoghlaim-mmo
description: The Cianfhoghlaim Educational MMO — 8 NCCA Leaving Certificate subjects × per-subject ADK agents (math_agent / appm_agent / chem_agent / geog_agent / hist_agent / engl_agent / gael_agent / comp_agent) × BAML quest-pack generators × DLT + Dagster + CocoIndex v1 + Cognee pipelines × hybrid x402 educational credential (off-chain SkillTreeBadge in Convex + FalkorDB + LanceDB, daily Merkle anchor on Base L2) × TanStack Start 2D client at port 3080. Use when adding a new subject realm, wiring a per-subject quest pack, deploying the daily credential anchor, integrating with the root_agent keyword router, or asking "how does the Cianfhoghlaim educational MMO fit together?". **Supersedes the deprecated tuatha-mmo / tuatha-platform / tuatha-achievement-ledger / tuatha-mcp-server-tools skills + british-isles-formative-assessment.**
---

# Cianfhoghlaim Educational MMO

## When to use this skill

Use when you need to:

- "Add a new NCCA subject realm" (mathematics, applied_mathematics, chemistry, geography, history, english, gaeilge, computer_science)
- "Design a formative assessment quest pack" — see the
  `.agents/skills/ncca-formative-assessment/` skill (the new
  canonical, supersedes british-isles-formative-assessment)
- "Wire a per-subject BAML extraction" — see `cianfhoghlaim/baml/qpack_<subject>.baml`
- "Add a per-subject Dagster asset" — see `cianfhoghlaim/dagster/assets/<subject>_assets.py`
- "Add a per-subject CocoIndex v1 embedding flow" — see
  `cianfhoghlaim/cocoindex/<subject>_embedding.py`
- "Onboard a new subject specialist agent (math_agent / appm_agent /
  chem_agent / geog_agent / hist_agent / engl_agent / gael_agent /
  comp_agent)" — see `cianfhoghlaim/agents/meaisinfhoghlaim/educational/<subject>_agent.py`
- "Issue a SkillTreeBadge after quest completion" — see
  `cianfhoghlaim/badges/`
- "Run the daily Merkle anchor on Base L2" — see
  `cianfhoghlaim/dagster/assets/credential_assets.py`
- "Verify a badge against the on-chain anchor" — see the public
  `/anchor/<date>` page on the TanStack Start 2D client
- "Understand the 8 NCCA subjects + the per-subject pipeline pattern"

## Overview

**Cianfhoghlaim** is a **formative-assessment-driven educational MMO**
for the **Republic of Ireland's NCCA Junior Cycle + Leaving Certificate**
curriculum. It fuses 8 NCCA subject specialisations into a single
product:

- **8 per-subject pipelines** end-to-end (PDF → BAML → DLT → Dagster
  → CocoIndex v1 → marimo notebook)
- **8 ADK specialist agents + 1 root orchestrator** that routes
  keyword-level traffic to the right subject
- **Hybrid x402 educational credential** — off-chain `SkillTreeBadge`
  in Convex + FalkorDB + LanceDB, daily Merkle anchor on Base L2
  (verifiable by any third party: employers, universities)
- **TanStack Start 2D game client** at port 3080 (no Babylon.js 3D,
  no SpacetimeDB v2 — those are deferred to v2)

The 8 NCCA subjects are:

| # | Subject (EN) | Subject (GA) | Realm code | Levels |
|:--|:--|:--|:--|:--|
| 1 | Mathematics | Matamaitic | `MATH` | FL / OL / HL |
| 2 | Applied Mathematics | Matamaitic Fheidhmeach | `APPM` | HL only |
| 3 | Chemistry | Ceimic | `CHEM` | OL / HL |
| 4 | Geography | Tíreolaíocht | `GEOG` | OL / HL |
| 5 | History | Stair | `HIST` | OL / HL |
| 6 | English | Béarla | `ENGL` | OL / HL |
| 7 | Gaeilge | Gaeilge | `GAEL` | FL / OL / HL |
| 8 | Computer Science | Ríomheolaíocht | `COMP` | OL / HL |

The platform builds on the existing Cianfhoghlaim pipeline stack:
DLT (per-subject sources) + Dagster (per-subject asset groups) +
CocoIndex v1 (per-subject embedding) + BAML (per-subject extraction +
quest-pack generation) + FalkorDB + LanceDB + Cognee + Graphiti
(memory layer) + Letta (agent memory) + LiteLLM (unified LLM gateway) +
CopilotKit AG-UI (streaming chat) + Hono + Convex + TanStack Start
(2D game client) + BetterAuth + SIWE (auth).

The historic skills `.agents/skills_backup/tuatha-mmo/` and
`.agents/skills_backup/tuatha-platform/` are preserved as
**archaeology** — they document an earlier Babylon.js 3D + SpacetimeDB
v2 + Pent-Elemental Cosmology + Crypteolas financial token design that
did not land. The new build drops those themes but keeps the
technological choices.

## The 8-agent system

The educational backbone is **8 ADK specialist agents**, one per NCCA
subject, each backed by BAML + LiteLLM + Letta:

| Agent | Primary role | Default model |
|:--|:--|:--|
| `math_agent` | Mathematics specialist (concrete + worked-example feedback) | `litellm/anthropic/claude-sonnet-4` |
| `appm_agent` | Applied Mathematics specialist (mechanics + vectors) | `litellm/anthropic/claude-sonnet-4` |
| `chem_agent` | Chemistry specialist (reactions + equilibria) | `litellm/anthropic/claude-sonnet-4` |
| `geog_agent` | Geography specialist (physical + regional) | `litellm/anthropic/claude-sonnet-4` |
| `hist_agent` | History specialist (Ireland + Europe) | `litellm/anthropic/claude-sonnet-4` |
| `engl_agent` | English specialist (comparative + composition) | `litellm/anthropic/claude-sonnet-4` |
| `gael_agent` | Gaeilge specialist (gramadach + litríocht) | `litellm/anthropic/claude-sonnet-4` |
| `comp_agent` | Computer Science specialist (algorithms + data structures) | `litellm/anthropic/claude-sonnet-4` |

The agents are CopilotKit AG-UI components rendered in the TanStack
Start UI; their state lives in Convex (the `badges` table) and in
FalkorDB (the cross-realm mastery graph). A2UI streams UI events over
the AG-UI WebSocket.

The root orchestrator (`root_agent` in `cianfhoghlaim/agents/adk/`)
routes keyword-level traffic to the 8 subject agents. Routing keywords
per agent:

| Agent | First 6 routing keywords |
|:--|:--|
| `math_agent` | math, algebra, calculus, differentiation, integration, probability |
| `appm_agent` | mechanics, dynamics, applied, vectors, projectile, moment of inertia |
| `chem_agent` | chemistry, molecule, reaction, equilibrium, organic, periodic table |
| `geog_agent` | geography, map, climate, tectonic, population, economic |
| `hist_agent` | history, 1916, european, irish history, cold war, modern ireland |
| `engl_agent` | english, poetry, shakespeare, comparative, unseen, composition |
| `gael_agent` | gaeilge, irish, gramadach, litríocht, filíocht, béaloideas |
| `comp_agent` | computer science, algorithm, data structure, python, complexity, sorting |

## NCCA Subject Cosmology (8 realms)

The game world is divided into **8 NCCA subject realms**, each tied
to a Leaving Certificate subject and an NCCA learning outcome code:

- Each realm is a **TanStack Start route** (`/realm/<subject>`)
- Inter-realm travel happens through **interdisciplinary quests**
  (e.g. the *An Ghaeilge sa Mhatamaitic* quest blends Gaeilge +
  Mathematics)
- The cosmology is encoded as data, not as hard-coded scenes: the
  `lc_subjects.json` manifest holds the subject metadata + the
  per-subject pipeline wiring

## Per-subject pipeline (the canonical pattern)

For each of the 8 subjects, the canonical 9-file template is:

```
cianfhoghlaim/
├── baml/
│   └── qpack_<subject>.baml                    # Quest-pack generator
├── dlt/
│   └── subjects/
│       └── <subject>/
│           ├── __init__.py
│           ├── sources.py                     # DLT PDF source
│           └── schema.py
├── dagster/
│   └── assets/
│       └── <subject>_assets.py                # 6 assets per subject
├── cocoindex/
│   └── <subject>_embedding.py                 # v1 CocoIndex App
├── agents/
│   └── meaisinfhoghlaim/
│       └── educational/
│           ├── <subject>_agent.py             # 1 ADK agent per subject
│           └── tools/                         # 5 tools per agent
├── web/
│   └── apps/
│       └── cianfhoghlaim-mmo/
│           └── src/
│               └── routes/
│                   └── realm/
│                       └── <subject>.tsx       # 1 TanStack Start route per realm
└── notebooks/
    └── leaving_cert/
        └── <subject>.py                       # 1 marimo notebook per subject
```

The Mathematics subject is built end-to-end as the template. The
remaining 7 subjects follow the same template (Phase 4 of the
`cianfhoghlaim-educational-mmo-v1` openspec change).

## Hybrid x402 educational credential

Per-subject quest completion emits a `SkillTreeBadge` via
`cianfhoghlaim/badges/issue_badge()`. Each badge is:

- **Off-chain**: stored in Convex (the `badges` table) + FalkorDB
  (cross-realm mastery graph) + LanceDB (BGE-M3 1024-dim embedding)
- **On-chain**: the daily Merkle root of new badges is published to
  **Base L2** via the `CredAnchor` smart contract
  (`cianfhoghlaim/badges/anchor.py` + `anchor_contract.py`)
- **Verifiable by any third party** (employer, university) via the
  public `/anchor/<date>` page on the TanStack Start 2D client

The credential is **educational, not financial** — students do not
buy anything with real money, and the educational credit tokens are
issued by the platform itself as quest-completion rewards. The gas
for the daily Merkle anchor is paid from the platform's treasury
(Base L2 ≈ $0.01/anchor; 1 anchor/day = $3.65/year).

The `daily_credential_anchor` Dagster asset runs at 02:00 UTC daily:

```python
@dg.asset(group_name="credentials")
def daily_credential_anchor(context):
    new_badges = fetch_badges_since(last_anchor_iso)
    batch = anchor_mod.publish_anchor(new_badges, today)
    # batch.tx_hash is written back into each badge row in Convex
```

## TanStack Start 2D game client

The v1 client is at `cianfhoghlaim/web/apps/cianfhoghlaim-mmo/` on
port 3080. Routes:

| Path | Purpose |
|:--|:--|
| `/` | Landing page (NCCA-corpus hero, subject chooser) |
| `/realm/<subject>` | Subject realm (2D quest list + CopilotKit chat + quest pack UI) |
| `/student/<id>/badges` | Badge wallet (off-chain badges + on-chain anchor lookup) |
| `/student/<id>/mastery` | Cross-subject mastery dashboard (FalkorDB-backed) |
| `/teacher/<class>/quests` | Teacher view (marimo-embedded quest designer) |
| `/anchor/<date>` | Public Merkle-root proof page (verifies against Base L2) |

**No Babylon.js, no SpacetimeDB v2** in v1 (those are deferred to v2).

State: Convex for real-time (`player_progress`, `quest_attempts`,
`badges`); TanStack Query for read caches; Hono for write APIs.
Auth: BetterAuth (email/password + SIWE wallet).
i18n: Bilingual EN + GA UI strings + bilingual quest content.

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new NCCA subject realm | `cianfhoghlaim/web/apps/cianfhoghlaim-mmo/src/routes/realm/<subject>.tsx` |
| Add a new BAML extraction for a subject | `cianfhoghlaim/baml/qpack_<subject>.baml` |
| Add a new DLT source for a subject | `cianfhoghlaim/dlt/subjects/<subject>/sources.py` |
| Add a new Dagster asset for a subject | `cianfhoghlaim/dagster/assets/<subject>_assets.py` |
| Add a new CocoIndex v1 embedding flow | `cianfhoghlaim/cocoindex/<subject>_embedding.py` |
| Onboard a new subject agent | `cianfhoghlaim/agents/meaisinfhoghlaim/educational/<subject>_agent.py` + `tools/<subject>_*.py` |
| Issue a SkillTreeBadge | `cianfhoghlaim/badges/issue_badge()` |
| Run the daily credential anchor | `cianfhoghlaim/dagster/assets/credential_assets.py` |
| Verify a badge | `/anchor/<date>` page on the 2D client |
| Design a new formative quest pack | `.agents/skills/ncca-formative-assessment/SKILL.md` |

## Cross-references

- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — the
  canonical spec (8 Requirements)
- `openspec/changes/cianfhoghlaim-educational-mmo-v1/` — the active
  change (proposal + tasks + spec deltas)
- `.agents/skills/agent-fleet-orchestration/SKILL.md` — the 12-agent
  fleet pattern (this skill extends it with 8 subject agents)
- `.agents/skills/agent-observability/SKILL.md` — Langfuse + MLflow +
  RAGAS + Logfire observability
- `.agents/skills/agent-memory-systems/SKILL.md` — Letta + Graphiti +
  Cognee + LanceDB + FalkorDB memory layer
- `.agents/skills/agentic-frontend-frameworks/SKILL.md` — TanStack
  Start + CopilotKit + Hono + Convex pattern
- `.agents/skills/ncca-formative-assessment/SKILL.md` — the new
  canonical formative assessment pedagogy (replaces
  british-isles-formative-assessment)
- `.agents/skills/cianfhoghlaim-cocoindex-v1/SKILL.md` — the v1
  CocoIndex App pattern (used for per-subject embedding flows)

## Migration from historic skills

The historic skills `.agents/skills_backup/tuatha-mmo/`,
`.agents/skills_backup/tuatha-platform/`,
`.agents/skills_backup/tuatha-achievement-ledger/`, and
`.agents/skills_backup/tuatha-mcp-server-tools/` document an earlier
**Tuath British Isles MMO** design with Babylon.js 3D + SpacetimeDB
v2 + Pent-Elemental Cosmology + Crypteolas financial token. Those
products did not land. The new build drops the themes but keeps the
technological choices:

| Historic skill | New canonical skill | Renamed code path |
|:--|:--|:--|
| `tuatha-mmo` | `cianfhoghlaim-mmo` | `agents/tuatha/` → `agents/meaisinfhoghlaim/educational/` |
| `tuatha-platform` | `cianfhoghlaim-platform` (TBD) | `openspec/specs/tuatha-platform/` → `openspec/specs/cianfhoghlaim-educational-mmo/` |
| `tuatha-achievement-ledger` | `cianfhoghlaim-achievement-ledger` (TBD) | `badges/anchor.py` is the new home |
| `tuatha-mcp-server-tools` | `cianfhoghlaim-mcp-server-tools` (TBD) | (no change yet) |
| `british-isles-formative-assessment` | `ncca-formative-assessment` | (TBD — content rewrite to NCCA-only) |

The historic skills remain in `.agents/skills_backup/` for
archaeology but are excluded from `mise run lint:skills`.