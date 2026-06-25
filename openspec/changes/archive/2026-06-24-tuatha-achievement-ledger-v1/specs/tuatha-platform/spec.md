## MODIFIED Requirements

### Requirement: Crypteolas crypto data platform

The system SHALL provide an **educational-achievement ledger**
at `sruth/tuatha/sruth/crypteolas/achievements/` (rebranded from the v0
"Crypteolas crypto data platform" per Phase 6 of the 6-phase
refactor plan). The ledger holds **skill-tree badges**, NOT
a financial token. The canonical home is
`sruth/tuatha/sruth/crypteolas/achievements/ledger.py`; the public
surface is the `AchievementLedger` class with the 4 methods:
`issue(badge)`, `list_badges(player_id, framework=...)`,
`verify_signature(badge_id)`,
`cross_quest_relevance(player_id, realm)`.

Per the user's plan: "crypto = educational achievements
(not finance)". The ledger metadata includes the 8 fields:

- The curriculum framework (NCCA / CfE / CfW / CCEA / SQA)
- The level (e.g. JC4 / CfE Third Level / Progression Step 3)
- The subject (e.g. "Gaeilge" / "Mathematics")
- The competency (e.g. "Vocabulary" / "Comprehension")
- The learning outcome code (e.g. "JC English OL — LO 2.4")
- The date earned + the agent that issued the badge
- The evidence (a 3-sentence reflection from the player)
- A cryptographic evidence signature (the agent's wallet signs
  the evidence via Sign-In With Ethereum)

x402 micropayments remain in the tech stack but are
**reserved for gated game features only** (cosmetics,
premium quests, paid DLC) — never for educational content.
The v0 financial-token flow (Bitcoin / Ethereum / Solana
settlement) is preserved for the optional paid-DLC path.

The 5 Pent-Elemental Cosmology realms (Spirit / Water / Fire
/ Earth / Air) are the 5 masteries the player can earn.
Each realm maps to 1 of the 5 curriculum frameworks
(NCCA → Earth, CfE → Water, CfW → Fire, CCEA → Air,
SQA → Spirit).

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
- **AND** the evidence is signed by the agent's wallet
  (the cryptographic evidence chain)
- **AND** the badge is stored in the
  `crypteolas_achievements` LanceDB table with a
  1024-dim BGE-M3 embedding of the
  `evidence + subject + competency` text

## ADDED Requirements

### Requirement: Achievement-ledger implementation

The system SHALL provide the canonical implementation of the
Crypteolas educational-achievement ledger at
`sruth/tuatha/sruth/crypteolas/achievements/` (6 files):

- `__init__.py` — the package marker + the 4 public surfaces
- `schema.py` — the 8-field `SkillTreeBadge` dataclass + the
  `CurriculumFramework` enum (NCCA / CfE / CfW / CCEA / SQA)
  + the `PentElementalRealm` enum (Spirit / Water / Fire /
  Earth / Air) + the `SkillTreeMastery` dataclass
- `storage.py` — the LanceDB-backed `AchievementStorage`
  with the `crypteolas_achievements` + `crypteolas_masteries`
  tables
- `ledger.py` — the `AchievementLedger` class with the 4
  public methods + the `_sign_evidence` + `_verify_evidence`
  helpers (the cryptographic evidence chain)
- `cli.py` — the 4 CLI commands (issue, list, verify, mastery)
- `sruth/tuatha/sruth/crypteolas/__init__.py` — the package marker

The 4 public methods of `AchievementLedger`:

1. `issue(badge: SkillTreeBadge) -> dict` — insert the badge
   into the `crypteolas_achievements` LanceDB table; sign the
   evidence with the agent's wallet; auto-issue a
   Cross-British-Isles Achiever mastery if the player has
   now earned 1+ badge in each of the 5 frameworks
2. `list_badges(player_id, framework=...)` — list a player's
   badges (optional framework filter)
3. `verify_signature(badge_id) -> dict` — verify the
   cryptographic evidence chain
4. `cross_quest_relevance(player_id, realm, query_text="")`
   — return the 3 most relevant badges for a new quest
   (LanceDB vector search by BGE-M3 embedding)

#### Scenario: A quest_guide_agent issues a badge via the CLI

- **WHEN** a developer runs
  `uv run python -m tuatha.crypteolas.achievements.cli issue --framework=NCCA --level=JC3 --subject=Gaeilge --competency=Vocabulary --lo=JC-Gaeilge-LO-2.4 --agent-issuer=quest_guide_agent --player=demo_user_001 --evidence="I learned 50 new Irish words across 3 quests."`
- **THEN** the CLI exits 0
- **AND** the JSON output contains the badge_id, the
  evidence_signature, and the mastery_issued (null or a
  Cross-British-Isles Achiever mastery if the player has
  1+ badge in each of the 5 frameworks)
- **AND** the badge is stored in the
  `crypteolas_achievements` LanceDB table

### Requirement: Cross-British-Isles Achiever mastery

The `AchievementLedger.issue` method SHALL auto-issue a
**Cross-British-Isles Achiever mastery** when a player has
earned at least 1 badge in each of the 5 British Isles
curriculum frameworks (NCCA + CfE + CfW + CCEA + SQA).
The 5 masteries are:

1. `Mastery of Spirit` (the Pent-Elemental `Spirit` realm)
2. `Mastery of Water` (the Pent-Elemental `Water` realm)
3. `Mastery of Fire` (the Pent-Elemental `Fire` realm)
4. `Mastery of Earth` (the Pent-Elemental `Earth` realm)
5. `Mastery of Air` (the Pent-Elemental `Air` realm)

The mastery is stored in the `crypteolas_masteries` LanceDB
table with the source_badge_ids (the 5 framework badges that
triggered the mastery).

#### Scenario: A player earns all 5 framework badges

- **GIVEN** a player has earned 1 badge in NCCA + 1 in CfE
  + 1 in CfW + 1 in CCEA + 1 in SQA
- **WHEN** the player earns the 5th framework badge via
  `AchievementLedger.issue`
- **THEN** the method auto-issues the 5
  Cross-British-Isles Achiever masteries (one per
  Pent-Elemental realm)
- **AND** each mastery is stored in the
  `crypteolas_masteries` LanceDB table with the 5
  source_badge_ids

### Requirement: MCP server tool shim

The `sruth/tuatha/agents/mcp_server/server.py` SHALL import the 5
canonical MCP tools (`search_curriculum`,
`get_learning_outcomes`, `search_mythology`,
`get_character_lore`, `get_location_lore`) via 3 thin
re-export shim files at `sruth/tuatha/agents/tools/`:

- `__init__.py` — the package marker
- `curriculum_search.py` — re-exports the canonical
  `search_curriculum` + `get_learning_outcomes` +
  `CurriculumSearchResults` + `OIDEACHAIS_LANCEDB_PATH` from
  `oideachais.agents.adk.tools.tuatha_curriculum_search`
- `mythology_query.py` — re-exports the canonical
  `search_mythology` + `get_character_lore` +
  `get_location_lore` from
  `oideachais.agents.adk.tools.tuatha_mythology_query`

The 3 shim files SHALL preserve the historical
`from ..tools.X import ...` import pattern used by the
`sruth/tuatha/agents/mcp_server/server.py` lines 23-33, while
delegating to the canonical home in `sruth/oideachais/` (the
oideachais quadrant is the authoritative source for Celtic
curriculum + mythology content).

#### Scenario: The MCP server boots without import errors

- **WHEN** a developer runs
  `uv run python -m tuatha.agents.mcp_server.server --transport=stdio`
- **THEN** the server boots without `ModuleNotFoundError`
- **AND** the 5 tools (`search_curriculum`,
  `get_learning_outcomes`, `search_mythology`,
  `get_character_lore`, `get_location_lore`) are listed
  via the MCP protocol
