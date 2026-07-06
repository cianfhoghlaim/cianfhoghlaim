---
name: ncca-formative-assessment
description: The NCCA formative assessment framework — the pedagogical engine of the Cianfhoghlaim Educational MMO. 8 NCCA Leaving Certificate subjects × 4 formative feedback channels × 3 quest types × 4 graduated hint levels + the SkillTreeBadge schema + the 8 ADK specialist agent roster. Supersedes the historic british-isles-formative-assessment skill (which covered NCCA / CfE / CfW / CCEA / SQA — narrowed to NCCA-only for v1).
---

# NCCA Formative Assessment Framework

## When to use this skill

Use when you need to:

- Design a new formative quest pack for any of the 8 NCCA LC subjects
- Onboard a new formative feedback agent (the 8 NCCA specialist agents)
- Wire a new quest type or graduated hint level
- Understand the SkillTreeBadge schema (the NCCA-aligned educational
  credential, distinct from the historic British-Isles 5-framework one)
- Ask "how does formative assessment work in the Cianfhoghlaim MMO?"
- Decide whether a feature is **formative** (in-scope) or **summative**
  (out-of-scope — the LC / GCSE / A-Level are summative and don't
  belong in the MMO)

## Overview

**Cianfhoghlaim** is a **formative-assessment-driven educational MMO**
for the **Republic of Ireland's NCCA Junior Cycle + Leaving Certificate**
curriculum. The framework is:

- **8 NCCA Leaving Certificate subjects** (mathematics, applied_mathematics,
  chemistry, geography, history, english, gaeilge, computer_science)
- **4 formative feedback channels** = 4 NCCA-aligned agent roles per
  subject (delivered by 8 ADK specialist agents + 1 root orchestrator)
- **3 quest types** = the 3 modes of formative engagement
- **4 graduated hint levels** = the 4 levels of scaffolded support
- **SkillTreeBadge schema** = the NCCA-aligned educational credential

**Key principle:** the MMO is **formative, not summative**. It gives
continuous feedback during learning, not a final grade. The Leaving
Certificate is out of scope as a graded product. The SkillTreeBadge is
the summative-severity record that a third party (employer, university)
can verify, but the MMO's pedagogical engine is per-quest,
per-response, per-misconception.

## The 8 NCCA LC subjects (the "realms")

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

The 8 ADK specialist agents are:

| Agent | Backing BAML | Default model | Language(s) |
|:--|:--|:--|:--|
| `math_agent` | `qpack_mathematics.baml` | `litellm/anthropic/claude-sonnet-4` | en + ga |
| `appm_agent` | `qpack_applied_mathematics.baml` | `litellm/anthropic/claude-sonnet-4` | en + ga |
| `chem_agent` | `qpack_chemistry.baml` | `litellm/anthropic/claude-sonnet-4` | en + ga |
| `geog_agent` | `qpack_geography.baml` | `litellm/anthropic/claude-sonnet-4` | en + ga |
| `hist_agent` | `qpack_history.baml` | `litellm/anthropic/claude-sonnet-4` | en + ga |
| `engl_agent` | `qpack_english.baml` | `litellm/anthropic/claude-sonnet-4` | en + ga |
| `gael_agent` | `qpack_gaeilge.baml` | `litellm/anthropic/claude-sonnet-4` | ga (text_en optional helper) |
| `comp_agent` | `qpack_computer_science.baml` | `litellm/anthropic/claude-sonnet-4` | en + ga |

## 4 formative feedback channels (per subject)

The 4 channels mirror the canonical Cianfhoghlaim feedback loop. Each
subject agent delivers feedback through the channel most appropriate
for the item type:

| Channel | Who delivers | What it does |
|:--|:--|:--|
| **Subject Tutor** | `<subject>_agent` | Concrete + worked-example feedback. The primary channel. |
| **Quest Guide** | `gael_tutor` (graduated hints) | 4 graduated hint levels (Level 1 nudge → Level 4 step-by-step). |
| **Curriculum Lookup** | `cianhoghlaim.baml` (`ExtractLeavingCertSyllabus`, `ExtractLeavingCertPastPaper`, `ExtractLeavingCertMarkingScheme`) | Direct NCCA LO citation + source page reference. |
| **Research Assistant** | `meaisinfhoghlaim.agents.adk.research_assistant_agent` | Cross-topic + cross-subject synthesis; bridges to Mathematics, History, etc. |

For Gaeilge specifically, the **Grammar Review** channel is the 5th
distinct channel — it provides conjugation tables + grammar rule
explanations in Irish.

## 3 quest types

| Type | Description | Example (Mathematics) |
|:--|:--|:--|
| **Skill quest** | Drill one LO with multiple contexts | "Differentiate f(x) = x² + 3x in 3 different ways" |
| **Conceptual quest** | Build deep understanding | "Explain why d/dx[xⁿ] = nxⁿ⁻¹" |
| **Application quest** | Real-world problem-solving | "A ball is thrown upward at 20 m/s. When does it reach 15 m?" |

## 4 graduated hint levels

Every formative item has exactly 4 hints, indexed 0-3, in order from
least to most scaffolding:

| Level | Type | Example |
|:--|:--|:--|
| **Level 1 (nudge)** | A conceptual pointer, no answer | "Think about the power rule" |
| **Level 2 (specific)** | Names the operation needed | "Use d/dx[xⁿ] = nxⁿ⁻¹" |
| **Level 3 (direct but incomplete)** | Most of the work shown, last step missing | "f'(x) = 2x + ? for the second term" |
| **Level 4 (step-by-step)** | Full worked solution with marking-scheme alignment | Full working, including the answer |

Each hint used reduces the **partial_credit_pct** by ~15-20% but
preserves the **SkillTreeBadge** if the final attempt scores ≥80%.

## SkillTreeBadge schema (the educational credential)

When a student's attempt scores ≥80% on a formative item, a
`SkillTreeBadge` is issued:

```python
class SkillTreeBadge:
    id: str                        # UUID
    student_id: str                # Hash(student_pseudonym + salt)
    framework: str                 # 'ncca-lc' or 'ncaa-jc'
    level: str                     # 'hl', 'ol', 'fl', 'jc'
    subject: str                   # 'mathematics', 'gaeilge', etc.
    competency_code: str           # NCCA LO code, e.g. 'LC-MATHS-LO-2.4'
    competency_text: BilingualText
    date_earned: datetime
    agent_issuer: str              # 'math_agent', 'gael_agent', etc.
    evidence: EvidenceLink         # Pointer to the formative item + response
    evidence_hash: str             # SHA-256, used as Merkle leaf
    signature: str                 # ETH-signed by the issuing agent's wallet
    on_chain_anchor: Optional[str] # Base L2 tx_hash (daily Merkle anchor)
    anchor_date: Optional[str]     # YYYY-MM-DD of the daily anchor batch
```

**Daily Merkle anchor:** the `daily_credential_anchor` Dagster asset
runs at 02:00 UTC daily, computes the Merkle root of all new badges,
and publishes to Base L2 via the `CredAnchor` smart contract
(`cianfhoghlaim/badges/anchor.py` + `anchor_contract.py`). The
on-chain record is verifiable by any third party via the public
`/anchor/<date>` page on the TanStack Start 2D client.

## NCCA-only scope (narrowed from historic 5-framework design)

The historic `british-isles-formative-assessment` skill covered the
5 frameworks:

- **NCCA** (Republic of Ireland) — Primary, JC, SC
- **CfE** (Scotland) — Early → Senior Phase
- **CfW** (Wales) — Foundation → KS5
- **CCEA** (Northern Ireland) — Foundation → Post-16
- **SQA** (Scotland) — National 3 → Advanced Higher

The v1 of the Cianfhoghlaim MMO narrows to **NCCA only** (per the
user's explicit decision on 2026-06-30). The CfE / CfW / CCEA / SQA
frameworks are out of scope for v1. The historic skill remains in
`.agents/skills_backup/british-isles-formative-assessment/SKILL.md`
for archaeology but is excluded from `mise run lint:skills`.

## What is NOT in scope

- **Leaving Certificate as a graded product** — the MMO is formative,
  not summative. The LC is out of scope as a test-prep product.
- **British Isles 5-framework scope** — narrowed to NCCA only for v1.
- **Babylon.js 3D client** — deferred to v2 (TanStack Start 2D for v1).
- **SpacetimeDB v2** — deferred to v2.
- **Pent-Elemental Cosmology** — replaced by NCCA Subject Cosmology.
- **Crypteolas financial token** — replaced by SkillTreeBadge.

## Per-quest scoring algorithm

```python
async def score_response(item, attempt):
    score = baml.ScoreFormativeResponse(item, attempt)
    # Per-step mark breakdown
    # Bilingual feedback (EN + GA where applicable)
    # next_recommended_lo based on the attempt
    # badge_earned iff partial_credit_pct >= 80
    if score.badge_earned:
        await issue_badge(...)  # Convex + FalkorDB + LanceDB
    return score
```

## Cross-references

- `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` — canonical spec
- `openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md` — design rationale
- `openspec/changes/cianfhoghlaim-educational-mmo-v1/tasks.md` — 92 tasks
- `.agents/skills/cianfhoghlaim-mmo/SKILL.md` — the canonical MMO skill
- `cianfhoghlaim/baml/qpack_<subject>.baml` — per-subject BAML contracts
- `cianfhoghlaim/agents/meaisinfhoghlaim/educational/<subject>_agent.py` — 8 ADK agents
- `cianfhoghlaim/badges/` — the hybrid x402 educational credential
- `.agents/skills/british-isles-formative-assessment/SKILL.md` (in
  `.agents/skills_backup/`) — the historic predecessor skill