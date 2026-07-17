---
name: british-isles-formative-assessment
description: The KCG pedagogical framework for the Tuatha MMO — British Isles formative assessment (not summative) mapped to the NCCA Primary + Junior Cycle + Senior Cycle / CfE Early Level through Senior Phase / Curriculum for Wales Foundation Phase through KS5 / CCEA Foundation Stage through KS5 / SQA National 3 through Advanced Higher. Use when designing a quest, designing a feedback rubric, mapping a learning outcome to a formative assessment event, or asking "how do the 4 tuatha agents (Celtic Tutor / Mythology Narrator / Quest Guide / Research Assistant) deliver formative feedback during a quest?".
---

# British Isles Formative Assessment

## Purpose

The Tuatha MMO is **not** a summative-assessment product. It is a
**formative-assessment** product that gives learners continuous
feedback during learning, not a final grade at the end of a
term. This skill captures the pedagogical framework that the 4
tuatha agents (Celtic Tutor, Mythology Narrator, Quest Guide,
Research Assistant) + the quest system + the achievement ledger
implement.

**Formative vs. summative:**

| | **Formative** (this MMO) | **Summative** (the Leaving Cert / GCSE / A-Level) |
|:--|:--|:--|
| When | During learning | End of course |
| Purpose | Adjust teaching + learning | Certify achievement |
| Granularity | Per-quest, per-response, per-misconception | Per-paper, per-grade boundary |
| Stakes | Low (retry-friendly) | High (one-shot) |
| Feedback channel | 4 ADK agents in real time | Marker reports after grading |
| Achievement type | Skill tree badges (this skill) | Certificate / grade |

## The 5 curriculum frameworks

The British Isles has 5 distinct curriculum frameworks. The MMO
implements all 5 via the same quest + agent + achievement pattern.

### 1. Ireland (NCCA Primary + JC + SC)

- **NCCA Primary Curriculum (2015 framework)** — 7 curriculum
  areas: Language (Gaeilge + English), Mathematics, Social,
  Environmental and Scientific Education (SESE), Arts
  Education, Physical Education, Social Personal and Health
  Education (SPHE)
- **Junior Cycle (2015 framework)** — 21 subjects. Each subject
  has a specification + CBA (Classroom-Based Assessment) +
  assessment task. The MMO maps CBAs to formative quests.
- **Senior Cycle (Leaving Certificate)** — Established + LCVP
  + LCA. The MMO covers the formative phase; the summative
  exam is out of scope.
- **Source**: `sruth/cianfhoghlaim/dlt_sources/domains/education/ie/`
  + `baml_src/curriculum_*.baml`

### 2. Scotland (CfE Early → Senior Phase)

- **Curriculum for Excellence (CfE)** — 3 levels (Early,
  First/Second, Third/Fourth) + Senior Phase. The MMO maps
  each CfE level to a "realm" in the Pent-Elemental Cosmology.
- **Experiences and Outcomes (EsOs)** — each CfE subject has
  EsOs at each level. The MMO quest system maps EsOs to
  formative quests.
- **Source**: `sruth/cianfhoghlaim/dlt_sources/domains/education/uk/scotland/`

### 3. Wales (Curriculum for Wales Foundation → KS5)

- **Curriculum for Wales (2015 framework)** — Foundation Phase
  + KS3 + KS4 + KS5. The 4 purposes of the curriculum drive
  the MMO's formative philosophy: ambitious, capable learners;
  enterprising, creative contributors; ethical, informed
  citizens; healthy, confident individuals.
- **Progression Steps** — each Area maps to Progression Steps
  at the 4 phases.
- **Source**: `sruth/cianfhoghlaim/dlt_sources/domains/education/uk/wales/`

### 4. Northern Ireland (CCEA Foundation → KS5)

- **CCEA Foundation Stage** (P1-P3)
- **CCEA Key Stage 1-4** (P4-Y12)
- **CCEA Post-16** (A-Levels, BTEC, Occupational Studies)
- **Source**: `sruth/cianfhoghlaim/dlt_sources/domains/education/uk/northern_ireland/`

### 5. SQA (National 3 → Advanced Higher)

- **National 3, 4, 5** (broad general education)
- **Higher + Advanced Higher** (post-16)
- **Source**: `sruth/cianfhoghlaim/dlt_sources/domains/education/uk/scotland/gov_scot_statistics.py`

## The 4 formative feedback channels

The 4 tuatha ADK agents (now at `sruth/cianfhoghlaim/agents/adk/`)
each deliver one channel of formative feedback:

| Agent | Formative role | When it fires |
|:--|:--|:--|
| **Celtic Tutor** | "How do I say / mean / pronounce this?" | During language quests; live pronunciation + grammar feedback |
| **Mythology Narrator** | "Tell me about / who is / what is the story of..." | During lore quests; live cultural context + fact-checking |
| **Quest Guide** | "How do I complete / what should I do next / hint..." | Per-quest; graduated hints (Level 1: nudge → Level 4: step-by-step) |
| **Research Assistant** | "Research / what is the history of / compare..." | After quest completion; comparative + cross-nation analysis |

## The 3 quest types

| Type | Formative event | Completion criteria |
|:--|:--|:--|
| **Language quest** | Vocabulary collection / grammar puzzle / translation challenge / conversation practice | Reproduce the answer in 3 different contexts (transfer test) |
| **Cultural quest** | Visit mythological location / learn about festival / discover historical event / explore traditional craft | Connect the cultural artefact to a learning outcome from the relevant national curriculum |
| **Story quest** | Follow mythological narrative / make choices affecting story / interact with legendary characters / uncover ancient mystery | Justify the player's choice in terms of a learning outcome (3-sentence reflection) |

## The 4 graduated hint levels

Per `sruth/cianfhoghlaim/agents/adk/quest_guide_agent:quest_guide_agent`:

- **Level 1**: Subtle nudge in the right direction
- **Level 2**: More specific guidance
- **Level 3**: Direct but not complete answer
- **Level 4**: Clear step-by-step help

The agent starts at Level 1 and escalates as the player makes
unsuccessful attempts. **All 4 levels are formative**: the
player always leaves with progress + feedback, never a binary
right/wrong.

## The achievement ledger (NOT a financial token)

Per the user's plan: "crypto = educational achievements (not
finance)". The MMO's crypto is a **badging system**, not a
cryptocurrency. The implementation lives in
`sruth/tuatha/sruth/crypteolas/achievements/`:

- **Skill tree badges** — 1 per curriculum framework × level
  (e.g. "NCCA Junior Cycle — Gaeilge — Vocabulary Level 3")
- **Quest completion badges** — 1 per quest family
- **Cross-quest masteries** — 1 per Pent-Elemental Cosmology
  realm (Spirit / Water / Fire / Earth / Air + Anam Cara)
- **Agent collaboration badges** — 1 per combination of
  agents the player has worked with (e.g. "Tutor + Narrator
  duo")

The badge metadata includes:

- The curriculum framework (NCCA / CfE / CfW / CCEA / SQA)
- The level (e.g. JC4 / CfE Third Level / Progression Step 3)
- The learning outcome code (e.g. "JC English OL — LO 2.4")
- The date earned + the agent that issued the badge
- The evidence (a 3-sentence reflection from the player)

## Cross-references

- `.agents/skills/tuatha-mmo/SKILL.md` — the MMO tech stack
  (Babylon.js, SpacetimeDB, x402, SIWE)
- `.agents/skills/celtic-asset-generation/SKILL.md` — how
  curriculum content becomes in-game assets
- `.agents/skills/cross-domain-registry/SKILL.md` — the
  `{nation}.{domain}.{entity}` asset-key contract
- `.agents/skills/irish-edtech/SKILL.md` — Irish-language
  AI patterns (UCCIX, GaBERT, BGE-M3)
- `sruth/cianfhoghlaim/agents/adk/{celtic_tutor_agent,mythology_narrator_agent,quest_guide_agent,research_assistant_agent,tuatha_root_agent}.py`
  — the 4 agents + the root orchestrator
- `openspec/specs/tuatha-platform/spec.md` — the canonical
  spec
- `openspec/changes/archive/2026-06-24-tuatha-formative-assessment-v1/`
  — the Phase 6 openspec change that records the
  British Isles formative assessment focus

## Reference

This skill was created during **Phase 6 of the 6-phase
tuatha refactor plan** (2026-06-24). Phase 6 = tuatha formative
assessment focus + skills + openspec.
