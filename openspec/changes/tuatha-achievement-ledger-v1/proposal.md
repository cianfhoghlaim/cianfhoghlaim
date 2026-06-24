# tuatha-achievement-ledger-v1

## Why

The Phase 6 deliverable of the 6-phase refactor plan
(`tuatha-formative-assessment-v1`, archived 2026-06-24)
promised a canonical implementation of the
`tuatha/crypteolas/achievements/` skill-tree badge ledger.
The spec was written and archived, but the implementation
was never created. The 4 prerequisites for this change:

1. The canonical `oideachais/agents/adk/tools/tuatha_*.py`
   tools (the 5 tools: `search_curriculum`,
   `get_learning_outcomes`, `search_mythology`,
   `get_character_lore`, `get_location_lore`) are wired and
   ready to consume.
2. The `tuatha/agents/mcp_server/server.py` has a broken
   import at lines 23-33 (`from ..tools.curriculum_search
   import ...` fails because `tuatha/agents/tools/` does
   not exist).
3. The 8-field badge schema + the 5 Pent-Elemental realm
   masteries + the cryptographic evidence chain are
   documented in `.agents/skills/tuatha-achievement-ledger/`
   + `.agents/skills/pent-elemental-cosmology/`.
4. The British Isles formative assessment framework
   (5 curriculum frameworks, 4 feedback channels, 3 quest
   types, 4 graduated hint levels) is documented in
   `.agents/skills/british-isles-formative-assessment/`.

The change delivers 4 sub-tasks:

1. **Achievement-ledger implementation** — the 6 new files
   at `tuatha/crypteolas/achievements/`
   (`__init__.py`, `schema.py`, `storage.py`, `ledger.py`,
   `cli.py`) plus the `tuatha/crypteolas/__init__.py` package
   marker. The 8-field skill-tree badge schema + the 5
   Pent-Elemental realm masteries + the LanceDB storage +
   the BGE-M3 embeddings + the cryptographic evidence
   chain (Sign-In With Ethereum, the same wallet identity
   as the player's authentication).
2. **MCP server shim fix** — the 3 shim files at
   `tuatha/agents/tools/{__init__,curriculum_search,mythology_query}.py`
   that preserve the historical import pattern while
   pointing at the canonical home in `oideachais/`.
3. **3 new skills** —
   `.agents/skills/pent-elemental-cosmology/SKILL.md`,
   `.agents/skills/tuatha-achievement-ledger/SKILL.md`,
   `.agents/skills/tuatha-mcp-server-tools/SKILL.md` —
   to document the 5 Pent-Elemental realms, the 8-field
   badge schema, the 4 cross-framework masteries, the
   cryptographic evidence chain, and the 5 MCP tools
   + the broken-import bug + the shim pattern.
4. **OpenSpec spec delta** — MODIFIED Requirement
   "Crypteolas crypto data platform" → "Crypteolas
   educational-achievement ledger" (the spec body was
   already updated but the requirement header still
   says "crypto data platform"), plus the 3 new
   ADDED Requirements on `tuatha-platform`:
   `Achievement-ledger implementation`,
   `Cross-British-Isles Achiever mastery`,
   `MCP server tool shim`.

The change is the 10th round of the multi-quadrant refactor
plan (rounds 7-13). Rounds 7-9 have already landed
(infrastructure, meaisinfhoghlaim, oideachais).

## What changes

- `tuatha/crypteolas/__init__.py` (new)
- `tuatha/crypteolas/achievements/__init__.py` (new)
- `tuatha/crypteolas/achievements/schema.py` (new)
- `tuatha/crypteolas/achievements/storage.py` (new)
- `tuatha/crypteolas/achievements/ledger.py` (new)
- `tuatha/crypteolas/achievements/cli.py` (new)
- `tuatha/agents/tools/__init__.py` (new)
- `tuatha/agents/tools/curriculum_search.py` (new)
- `tuatha/agents/tools/mythology_query.py` (new)
- `.agents/skills/pent-elemental-cosmology/SKILL.md` (new)
- `.agents/skills/tuatha-achievement-ledger/SKILL.md` (new)
- `.agents/skills/tuatha-mcp-server-tools/SKILL.md` (new)
- `tuatha/AGENTS.md` (updated — added 3 new skill rows to
  the priority quick reference)
- `tuatha/README.md` (updated — new achievement-ledger
  section + the Phase 6 reference)
- `openspec/specs/tuatha-platform/spec.md` (MODIFIED
  requirement header + 3 ADDED requirements)

## Impact

- **Cross-quadrant**: the tuatha `mcp_server` can now
  boot (the broken import at lines 23-33 is fixed via
  the 3 shim files).
- **Celtic content**: the 8-field skill-tree badge
  ledger + the 5 Pent-Elemental realm masteries are
  fully implemented (the Phase 6 promise is delivered).
- **Documentation**: the 3 new skills document the
  Pent-Elemental Cosmology, the achievement-ledger
  schema, and the MCP server tools.
- **Spec consistency**: the `tuatha-platform` spec
  header is corrected from "Crypteolas crypto data
  platform" to "Crypteolas educational-achievement
  ledger" (the body was already updated in a prior
  change).
