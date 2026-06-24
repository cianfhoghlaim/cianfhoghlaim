# Spec Delta: tuatha-platform

## MODIFIED Requirements

### Requirement: Crypteolas crypto data platform

The system SHALL provide an **educational-achievement ledger**
at `tuatha/crypteolas/achievements/` (rebranded from the v0
"Crypteolas crypto data platform" per Phase 6 of the 6-phase
refactor plan). The ledger holds **skill-tree badges**, NOT
a financial token.

Per the user's plan: "crypto = educational achievements
(not finance)". The ledger metadata includes:

- The curriculum framework (NCCA / CfE / CfW / CCEA / SQA)
- The level (e.g. JC4 / CfE Third Level / Progression Step 3)
- The learning outcome code (e.g. "JC English OL — LO 2.4")
- The date earned + the agent that issued the badge
- The evidence (a 3-sentence reflection from the player)

x402 micropayments remain in the tech stack but are
**reserved for gated game features only** (cosmetics,
premium quests, paid DLC) — never for educational content.
The v0 financial-token flow (Bitcoin / Ethereum / Solana
settlement) is preserved for the optional paid-DLC path.

#### Scenario: A player earns a skill-tree badge

- **GIVEN** a player completes a NCCA Junior Cycle Gaeilge
  Vocabulary Level 3 quest
- **WHEN** the `quest_guide_agent` validates the completion
- **THEN** the crypteolas ledger records a badge with:
  - `framework: "NCCA"`
  - `level: "JC3"`
  - `subject: "Gaeilge"`
  - `competency: "Vocabulary"`
  - `learning_outcome_code: "JC-Gaeilge-LO-2.4"`
  - `date_earned: <today>`
  - `agent_issuer: "quest_guide_agent"`
  - `evidence: <3-sentence player reflection>`

## ADDED Requirements

### Requirement: British Isles formative assessment focus

The system SHALL implement the British Isles formative
assessment pedagogical framework documented in
`.agents/skills/british-isles-formative-assessment/`. The
framework has 4 components:

1. **5 British Isles curriculum frameworks** (NCCA IE / CfE
   SCT / CfW WLS / CCEA NI / SQA SCT post-16) — each
   framework is a "realm" in the Pent-Elemental Cosmology
   (Spirit / Water / Fire / Earth / Air + Anam Cara).
2. **4 formative feedback channels** (the 4 tuatha ADK
   agents at `oideachais/agents/adk/`: Celtic Tutor,
   Mythology Narrator, Quest Guide, Research Assistant).
   Each agent delivers per-quest, per-response,
   per-misconception feedback. The player always leaves
   with progress + feedback, never a binary right/wrong.
3. **3 quest types** — language quests, cultural quests,
   story quests. Each has a completion criterion that
   maps to a learning outcome from the relevant national
   curriculum.
4. **4 graduated hint levels** — Level 1: subtle nudge →
   Level 2: specific guidance → Level 3: direct but
   incomplete → Level 4: step-by-step. The Quest Guide
   agent starts at Level 1 and escalates as the player
   makes unsuccessful attempts.

The framework is **formative, not summative**. The
Leaving Cert / GCSE / A-Level summative exams are out
of scope. The MMO gives continuous feedback during
learning, not a final grade at the end of a term.

#### Scenario: A player completes a formative language quest

- **GIVEN** a player is on a JC Gaeilge vocabulary
  collection quest
- **WHEN** the player attempts the quest
- **THEN** the `celtic_tutor_agent` delivers per-response
  formative feedback (live pronunciation + grammar)
- **AND** the `quest_guide_agent` provides graduated
  hints (Level 1: subtle nudge if stuck; escalates to
  Level 4: step-by-step after 3 unsuccessful attempts)
- **AND** upon completion, the `quest_guide_agent`
  validates the transfer test (reproduce the answer in 3
  different contexts) and issues a skill-tree badge via
  the crypteolas ledger
- **AND** the player always leaves with progress +
  feedback, never a binary right/wrong

#### Scenario: A player works across all 5 British Isles frameworks

- **GIVEN** a player has earned at least 1 badge in each
  of the 5 frameworks (NCCA / CfE / CfW / CCEA / SQA)
- **WHEN** the player revisits the MMO dashboard
- **THEN** the player sees a "Cross-British-Isles
  Achiever" badge (1 per Pent-Elemental Cosmology
  realm: Spirit / Water / Fire / Earth / Air)
- **AND** the badge records the 5 source-framework
  badges + the date the cross-framework achievement
  was earned
