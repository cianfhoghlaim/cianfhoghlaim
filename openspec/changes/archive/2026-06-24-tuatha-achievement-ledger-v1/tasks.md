# Tasks for tuatha-achievement-ledger-v1

## 1. Achievement-ledger implementation

- [x] 1.1 Create `sruth/tuatha/sruth/crypteolas/__init__.py` (the package marker)
- [x] 1.2 Create `sruth/tuatha/sruth/crypteolas/achievements/__init__.py` (the 4 public surfaces)
- [x] 1.3 Create `sruth/tuatha/sruth/crypteolas/achievements/schema.py` (the 8-field badge + the 5 realm types + the mastery dataclass)
- [x] 1.4 Create `sruth/tuatha/sruth/crypteolas/achievements/storage.py` (the LanceDB-backed storage with `crypteolas_achievements` + `crypteolas_masteries` tables)
- [x] 1.5 Create `sruth/tuatha/sruth/crypteolas/achievements/ledger.py` (the 4 public methods: issue, list_badges, verify_signature, cross_quest_relevance)
- [x] 1.6 Create `sruth/tuatha/sruth/crypteolas/achievements/cli.py` (the 4 CLI commands: issue, list, verify, mastery)

## 2. MCP server shim fix

- [x] 2.1 Create `sruth/tuatha/agents/tools/__init__.py` (the thin re-export shim)
- [x] 2.2 Create `sruth/tuatha/agents/tools/curriculum_search.py` (re-exports the canonical `search_curriculum` + `get_learning_outcomes`)
- [x] 2.3 Create `sruth/tuatha/agents/tools/mythology_query.py` (re-exports the canonical `search_mythology` + `get_character_lore` + `get_location_lore`)
- [x] 2.4 Verify `sruth/tuatha/agents/mcp_server/server.py` lines 23-33 import correctly via the shim

## 3. Three new skills

- [x] 3.1 Create `.agents/skills/pent-elemental-cosmology/SKILL.md` (the 5 realms, 5 SpacetimeDB tables, Anam Cara, Geasa, 5 quest tracks, Babylon.js scene graph)
- [x] 3.2 Create `.agents/skills/tuatha-achievement-ledger/SKILL.md` (the 8-field badge schema, 5 masteries, cryptographic evidence chain, cross-quest retrieval, add-a-new-badge workflow)
- [x] 3.3 Create `.agents/skills/tuatha-mcp-server-tools/SKILL.md` (the 5 MCP tools, the canonical home, the broken-import bug, the shim pattern, the 4 transports)

## 4. Spec delta

- [x] 4.1 MODIFIED Requirement "Crypteolas crypto data platform" → "Crypteolas educational-achievement ledger" (correct the header to match the body that was already updated)
- [x] 4.2 ADDED Requirement "Achievement-ledger implementation" (the 6 new files + the 4 public methods)
- [x] 4.3 ADDED Requirement "Cross-British-Isles Achiever mastery" (the 5 masteries, one per Pent-Elemental realm)
- [x] 4.4 ADDED Requirement "MCP server tool shim" (the 3 shim files + the canonical home in oideachais)

## 5. Documentation

- [x] 5.1 Update `sruth/tuatha/AGENTS.md` (add 3 new skill rows to the priority quick reference)
- [x] 5.2 Update `sruth/tuatha/README.md` (new achievement-ledger section + the Phase 6 reference)

## 6. Validation + commit + push + archive

- [ ] 6.1 Run `openspec validate tuatha-achievement-ledger-v1 --strict`
- [ ] 6.2 Run `mise run lint:skills` to verify the 3 new skills
- [ ] 6.3 Commit + push
- [ ] 6.4 Run `openspec archive tuatha-achievement-ledger-v1 --yes`
