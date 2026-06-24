# Change: tuatha-formative-assessment-v1

## Why

Phase 6 of the 6-phase refactor plan. Phases 1-5 brought the
*codebase* (phase 1), *infrastructure* (phase 2), *embedding*
(phase 3), and *agent* (phase 5) surfaces onto oideachais; phase
4 was removed (routes stay in tuatha).

Phase 6 reframes the tuatha quadrant's focus from
**"Celtic Educational MMO + crypto platform"** to
**"British Isles Formative Assessment MMO"**. Per the user's
plan: "tuatha = British Isles formative assessment MMO" and
"crypto = educational achievements (not finance)".

Two concrete changes:

1. **The crypto reframing**: the `tuatha/crypteolas/` data
   platform moves from "Bitcoin / Ethereum / Solana
   settlement layer for in-game transactions" to
   "educational-achievement ledger" (skill-tree badges, per
   curriculum framework × level, NOT a financial token).
   The x402 micropayments stay in the tech stack but are
   reserved for **gated game features only** (cosmetics,
   premium quests, paid DLC), never for educational content.
2. **The pedagogical reframing**: the MMO's curriculum
   scope is the **British Isles 5** (NCCA + CfE + CfW + CCEA
   + SQA), not "Celtic broadly". The 4 agents deliver
   **formative** feedback (continuous, low-stakes, retry-
   friendly) per the
   `.agents/skills/british-isles-formative-assessment/`
   framework, NOT summative feedback (end-of-term, high-
   stakes, one-shot). The Leaving Cert / GCSE / A-Level
   summative exams are out of scope.

The pedagogical framework is documented in a new skill
`.agents/skills/british-isles-formative-assessment/` (164
lines). The existing `tuatha-mmo` skill is updated with a
"British Isles formative assessment (Phase 6)" section that
cross-references the new skill.

## What Changes

### 1. `tuatha/README.md` (MODIFIED)

The header + the first paragraph are reframed from "Celtic
Educational MMO + Crypto Platform" to "British Isles
Formative Assessment MMO". Adds a Phase 6 callout.

### 2. `tuatha/AGENTS.md` (MODIFIED)

The overview is reframed. Adds a "Phase 6 of the 6-phase
refactor plan" callout. The Quick routing table gains 2
new rows: "Add a new educational-achievement badge" and
"Add a new formative-assessment quest". The Related
skills section gains 4 new entries: `tuatha-mmo`,
`british-isles-formative-assessment`, `celtic-asset-generation`,
`irish-edtech`.

### 3. `.agents/skills/british-isles-formative-assessment/SKILL.md` (NEW)

A new 164-line skill documenting:

- The formative-vs-summative matrix
- The 5 British Isles curriculum frameworks (NCCA / CfE /
  CfW / CCEA / SQA)
- The 4 formative feedback channels (the 4 tuatha agents)
- The 3 quest types (language / cultural / story)
- The 4 graduated hint levels (Level 1: nudge → Level 4:
  step-by-step)
- The achievement ledger schema (skill-tree badges, NOT a
  financial token)

### 4. `.agents/skills/tuatha-mmo/SKILL.md` (MODIFIED)

The description is updated to reflect the new focus.
The "British Isles formative assessment (Phase 6)"
section is added after the 4-agent system, cross-
referencing the new skill. Mentions that x402 is
reserved for gated game features only.

### 5. `openspec/specs/tuatha-platform/spec.md` (MODIFIED via 1 MODIFIED + 1 ADDED Requirement)

- 1 MODIFIED Requirement: "Crypteolas crypto data
  platform" → reframed to "Crypteolas educational-
  achievement ledger". The Scenario is reframed: no more
  "100 CELT" currency; instead, "1 skill-tree badge per
  NCCA Junior Cycle Gaeilge Vocabulary Level 3".
- 1 ADDED Requirement: "British Isles formative
  assessment focus" — the MMO SHALL implement the
  pedagogical framework documented in
  `.agents/skills/british-isles-formative-assessment/`
  with 4 formative feedback channels (the 4 agents), 3
  quest types, 4 graduated hint levels, and a
  curriculum-framework × level achievement ledger.

## Impact

- Affected specs: `tuatha-platform` (1 MODIFIED + 1 ADDED
  Requirement)
- Affected skills: 1 new
  (`british-isles-formative-assessment`), 1 updated
  (`tuatha-mmo`)
- Affected docs: 2 updated (`tuatha/README.md`,
  `tuatha/AGENTS.md`)
- No code refactor (Phase 6 is docs + skills + spec only;
  no `tuatha/crypteolas/` code changes — the code is
  inherited from the v0 implementation, with the
  reframing documented in the spec)
- The `Anam Cara NFT` and the `Crypteolas federated
  learning` round (from the v0 spec) are NOT removed —
  they remain in the spec as **optional premium content
  for gated game features**. The reframing is in the
  default focus, not the available tech stack.

## Success criteria

- `.agents/skills/british-isles-formative-assessment/SKILL.md`
  exists, has valid frontmatter, and is 150-180 lines
- `.agents/skills/tuatha-mmo/SKILL.md` has 4 cross-
  references to the new skill
- `tuatha/README.md` header reflects the new focus
- `tuatha/AGENTS.md` overview + routing table reflect the
  new focus
- `openspec validate tuatha-formative-assessment-v1
  --strict` passes
- The 1 MODIFIED Requirement on `tuatha-platform` reframes
  the crypteolas section to be about educational
  achievements, not a financial token
- The 1 ADDED Requirement documents the British Isles
  formative assessment focus
