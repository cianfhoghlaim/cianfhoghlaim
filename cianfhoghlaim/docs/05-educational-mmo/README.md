# Cianfhoghlaim Educational MMO

> The 8-subject formative-assessment MMO for the Republic of
> Ireland's NCCA Junior Cycle + Leaving Certificate curriculum.

## What is it?

The Cianfhoghlaim Educational MMO is a TanStack Start 2D game client
+ Google ADK agent fleet + hybrid x402 educational credential
backed by 8 per-subject NCCA pipelines.

It delivers **continuous formative feedback** to students
completing formative quest packs mapped to the NCCA learning
outcomes for each LC subject.

The 8 NCCA Leaving Certificate subjects:

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

## Quick links

- [Source code README](../README.md)
- [OpenSpec change `cianfhoghlaim-educational-mmo-v1`](../../../openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md)
- [OpenSpec spec `cianfhoghlaim-educational-mmo`](../../../openspec/specs/cianfhoghlaim-educational-mmo/spec.md)
- [Skill `.agents/skills/cianfhoghlaim-mmo/`](../../../.agents/skills/cianfhoghlaim-mmo/SKILL.md)
- [Skill `.agents/skills/ncca-formative-assessment/`](../../../.agents/skills/ncca-formative-assessment/SKILL.md)
- [Solidity contract `infrastructure/contracts/CredAnchor.sol`](../../../infrastructure/contracts/CredAnchor.sol)
- [2D game client `web/apps/cianfhoghlaim-mmo/`](../../../web/apps/cianfhoghlaim-mmo/README.md)
- [Hybrid x402 credential `badges/`](../badges/README.md)

## Architecture

```
                          Cianfhoghlaim Educational MMO v1
                                       │
   ┌───────────────────────────────────┼───────────────────────────────────┐
   │                                   │                                   │
   ▼                                   ▼                                   ▼
┌──────────────┐                ┌──────────────┐                   ┌──────────────────┐
│  8 NCCA      │                │  8 ADK       │                   │  TanStack Start  │
│  Subject     │ ──── feeds ──▶│  Specialist  │ ──── streams ───▶│  2D Game Client  │
│  Pipelines   │                │  Agents      │                   │  (port 3080)     │
└──────────────┘                └──────────────┘                   └──────────────────┘
       │                                  │                                 │
       │                                  │ routes via                      │
       │                                  ▼                                 │
       │                         ┌──────────────────┐                        │
       │                         │  Root Orchestrator│                       │
       │                         │  (cianfhoghlaim.   │                       │
       │                         │   agents.adk.      │                       │
       │                         │   root_agent)     │                       │
       │                         └──────────────────┘                        │
       │                                                                   │
       │                                                                   │
       │  ┌─────────────────────────┐                                     │
       └─▶│  BAML QPack Generation   │                                     │
          │  qpack_<subject>.baml   │                                     │
          │  per-subject enums +     │                                     │
          │  classes + 5 functions   │                                     │
          └─────────────────────────┘                                     │
                     │                                                       │
                     ▼                                                       │
       ┌─────────────────────────────────────────────────────┐             │
       │  Hybrid x402 Educational Credential                  │             │
       │  cianfhoghlaim/badges/                              │             │
       │   - Off-chain SkillTreeBadge in Convex +             │             │
       │     FalkorDB + LanceDB (BGE-M3 1024-dim)            │             │
       │   - Daily Merkle anchor on Base L2 via               │             │
       │     CredAnchor.sol (≤ $0.01/anchor)                  │             │
       │   - Public /anchor/<date> verifier on the 2D client │             │
       └─────────────────────────────────────────────────────┘             │
                                                                            │
       ┌─────────────────────────────────────────────────────┐             │
       │  Per-subject marimo notebooks (teacher view)          │◀────────────┘
       │  cianfhoghlaim/notebooks/leaving_cert/<subject>.py  │  badge wallet,
       └─────────────────────────────────────────────────────┘  cross-subject mastery
```

## Per-subject pipeline (the canonical 9-file template)

For each of the 8 NCCA subjects:

```
baml/qpack_<subject>.baml                    # BAML quest-pack generator (5 functions)
dlt/subjects/<subject>/{__init__,sources,schema}.py
dagster/assets/<subject>_assets.py            # 6 Dagster assets per subject
cocoindex/<subject>_embedding.py              # v1 CocoIndex App (BGE-M3 1024-dim)
agents/meaisinfhoghlaim/educational/<subject>_agent.py + tools/
notebooks/leaving_cert/<subject>.py           # marimo teacher dashboard
```

The Mathematics subject is fully built; the other 7 subjects apply
the same template.

## Hybrid x402 educational credential

**Educational, not financial.** Students do not buy anything with
real money.

- **Off-chain `SkillTreeBadge`** stored in Convex + FalkorDB + LanceDB.
- **Daily Merkle anchor** on Base L2 via `CredAnchor.sol` (the
  32-byte Merkle root + YYYY-MM-DD batch ID).
- **Verifiable by any third party** (employer, university, parent)
  via the public `/anchor/<date>` page on the 2D client.
- **Educational credit tokens** are issued by the platform itself as
  quest-completion rewards; not a financial instrument.
- **Annual cost** ≈ $3.65/year (Base L2 ≈ $0.01/anchor × 365 days).

## Cross-subject agent routing

The root orchestrator (`cianfhoghlaim.agents.adk.root_agent`) routes
keyword-level traffic to the 8 NCCA subject specialists:

| Keyword bucket | Subject agent |
|:--|:--|
| math, algebra, calculus, differentiation, integration, probability, geometry, statistics, trigonometry | `math_agent` |
| mechanics, dynamics, applied, vectors, projectile, moment of inertia | `appm_agent` |
| chemistry, molecule, reaction, equilibrium, organic, periodic table | `chem_agent` |
| geography, map, climate, tectonic, population, economic | `geog_agent` |
| history, 1916, european, irish history, cold war, modern ireland | `hist_agent` |
| english, poetry, shakespeare, comparative, unseen, composition | `engl_agent` |
| gaeilge, irish, gramadach, litríocht, filíocht, béaloideas | `gael_agent` |
| computer science, algorithm, data structure, python, complexity, sorting | `comp_agent` |

## Formative feedback philosophy

The MMO is **formative, not summative**. It gives continuous feedback
during learning, not a final grade. The Leaving Certificate as a
graded product is **out of scope**.

- **4 graduated hint levels** per item (Level 1 nudge → Level 4
  step-by-step)
- **SkillTreeBadge** issued when partial_credit_pct >= 80%
- **Bilingual EN + GA** on every user-facing string; Gaeilge taught in
  Irish (text_ga canonical, text_en optional helper)
- **8 specialist agents** mirror the 4 formative feedback channels
  (subject tutor + quest guide + curriculum lookup + research
  assistant) + the 5th Gaeilge-specific channel (grammar review)

## NCCA-only scope (narrowed from the historic 5-framework design)

The historic `.agents/skills_backup/british-isles-formative-assessment/`
skill covered NCCA (IE) + CfE (SCT) + CfW (WLS) + CCEA (NI) +
SQA (SCT-post-16). The v1 of Cianfhoghlaim narrows to **NCCA only**
(per the user's explicit decision on 2026-06-30).

## Quality gates

| Gate | Status |
|:--|:--|
| `openspec validate cianfhoghlaim-educational-mmo-v1 --strict` | ✅ PASS |
| Skill lint | ✅ 62/62 pass |
| TypeScript typecheck (`cianfhoghlaim-mmo`) | ✅ Exit 0 |
| `tests/_badges/` (18 tests) | ✅ 18/18 pass |
| `tests/_educational_mmo/` (52 tests) | ✅ 52/52 pass |
| Total MMO test suite | ✅ 70/70 pass |

## Reference

- `openspec/changes/cianfhoghlaim-educational-mmo-v1/` (the active change)
- `openspec/specs/cianfhoghlaim-educational-mmo/` (the canonical spec)
- `.agents/skills/cianfhoghlaim-mmo/SKILL.md` (the canonical skill)
- `.agents/skills/ncca-formative-assessment/SKILL.md`
- `infrastructure/contracts/CredAnchor.sol`
- `infrastructure/contracts/README.md`
- `web/apps/cianfhoghlaim-mmo/README.md`
- `badges/README.md`