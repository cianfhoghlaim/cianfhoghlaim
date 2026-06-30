# Tasks: cianfhoghlaim-educational-mmo-v1

## Phase 0: README §7 removal — COMPLETE

- [x] T0.1 Remove `README.md` lines 1919-2679 (§7 Tuath cultural-stewardship narrative, 760 lines)
- [x] T0.2 Verify README line count = 1950 (was 2711, removed 761 accounting for collapsed blank line)

## Phase 1: OpenSpec scaffolding — IN PROGRESS

- [x] T1.1 Create `openspec/changes/cianfhoghlaim-educational-mmo-v1/` directory
- [x] T1.2 Write `proposal.md` (the Why / What / Impact / Risks / Acceptance)
- [x] T1.3 Write `tasks.md` (this file)
- [ ] T1.4 Write spec delta at `openspec/changes/cianfhoghlaim-educational-mmo-v1/specs/cianfhoghlaim-educational-mmo/spec.md` with 8 Requirements × ≥1 Scenario
- [ ] T1.5 Write spec delta at `openspec/changes/cianfhoghlaim-educational-mmo-v1/specs/tuatha-platform/spec.md` with `## REMOVED Requirements` for all 4 historical Requirements
- [ ] T1.6 Run `bun run spec:validate cianfhoghlaim-educational-mmo-v1 --strict` — MUST pass before implementation
- [ ] T1.7 Create the new canonical spec at `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` (mirror of the delta for downstream reference)

## Phase 2: Theme rename (mechanical, no functional change)

- [ ] T2.1 Rename `.agents/skills/tuatha-mmo/` → `.agents/skills/cianfhoghlaim-mmo/`
  - Update `name:` frontmatter from `tuatha-mmo` to `cianfhoghlaim-mmo`
  - Update all internal references
- [ ] T2.2 Rename `.agents/skills/tuatha-platform/` → `.agents/skills/cianfhoghlaim-platform/`
- [ ] T2.3 Rename `.agents/skills/tuatha-achievement-ledger/` → `.agents/skills/cianfhoghlaim-achievement-ledger/`
- [ ] T2.4 Rename `.agents/skills/tuatha-mcp-server-tools/` → `.agents/skills/cianfhoghlaim-mcp-server-tools/`
- [ ] T2.5 Rename `.agents/skills/british-isles-formative-assessment/` → `.agents/skills/ncca-formative-assessment/`
  - Update content to drop CfE/CfW/CCEA/SQA references
  - Add the 8 NCCA subjects as the canonical framework
- [ ] T2.6 Rename `openspec/specs/tuatha-platform/spec.md` → add `## REMOVED Requirements` (do NOT delete the file; mark as deprecated alias)
- [ ] T2.7 Rename `cianfhoghlaim/agents/tuatha/` → `cianfhoghlaim/agents/meaisinfhoghlaim/educational/`
- [ ] T2.8 Rename `cianfhoghlaim/dlt/_croilar_pipelines/` → `cianfhoghlaim/dlt/_legacy_croilar_pipelines/`
- [ ] T2.9 Rename `cianfhoghlaim/dlt/destinations_tuatha.py` → `cianfhoghlaim/dlt/destinations_educational.py`
- [ ] T2.10 Rename `cianfhoghlaim/baml/tuatha_clients.baml` → `cianfhoghlaim/baml/educational_clients.baml`
- [ ] T2.11 Archive `cianfhoghlaim/dlt/british_isles/{sct,wls,ni,jey,iom,ggy}/` → `.archive/dlt/british_isles_other/`
- [ ] T2.12 Update all import paths in `cianfhoghlaim/dagster/`, `cianfhoghlaim/cocoindex/`, `cianfhoghlaim/agents/`, `cianfhoghlaim/web/`
- [ ] T2.13 Run `mise run lint:skills` — MUST report 123/123 → 127/127 (after rename + new skill)
- [ ] T2.14 Run `mise run turbo typecheck` — MUST pass

## Phase 3: Per-subject Mathematics template (1 of 8 fully built)

The remaining 7 subjects follow the same template (D3). Mathematics is built first because it has the richest corpus (7 PDFs in EN/GA) and the most NCCA learning outcomes.

- [ ] T3.1 Create `cianfhoghlaim/baml/qpack_mathematics.baml`
  - `class MathSyllabusTopic`, `class MathFormativeItem`, `class MathQuestPack`
  - `function GenerateMathQuestPack(syllabus, past_papers, marking_schemes, level) -> QuestPack`
  - `function ExtractMathLOStatement(paragraph) -> string[]`
  - `function GenerateMathFormativeItem(lo_code, difficulty) -> FormativeItem`
  - `function ScoreMathFormativeResponse(item, response) -> ScoreBreakdown`
  - Bilingual `text_en` + `text_ga` on every output field
- [ ] T3.2 Create `cianfhoghlaim/dlt/subjects/mathematics/__init__.py`
- [ ] T3.3 Create `cianfhoghlaim/dlt/subjects/mathematics/sources.py` (yielding 6 resources: syllabus, structure, past_papers, marking_schemes, alp_items, glp_items)
- [ ] T3.4 Create `cianfhoghlaim/dlt/subjects/mathematics/schema.py`
- [ ] T3.5 Create `cianfhoghlaim/dagster/assets/mathematics_assets.py` (6 `@asset`s: math_syllabus_raw, math_syllabus_structured, math_quest_pack, math_embedding, math_cognify, math_dashboard)
- [ ] T3.6 Create `cianfhoghlaim/cocoindex/mathematics_embedding.py` (v1 App, BGE-M3 1024-dim, LanceDB table `oideachais.lc.mathematics.embeddings`)
- [ ] T3.7 Create `cianfhoghlaim/agents/meaisinfhoghlaim/educational/math_agent.py` (ADK LlmAgent with 5 tools: `math_syllabus_lookup`, `math_past_paper_lookup`, `math_marking_scheme_lookup`, `math_formative_item_generate`, `math_response_score`)
- [ ] T3.8 Create `cianfhoghlaim/web/apps/cianfhoghlaim-mmo/src/routes/realm/mathematics.tsx` (TanStack Start route, 2D UI, bilingual, CopilotKit chat with math_agent)
- [ ] T3.9 Create `cianfhoghlaim/notebooks/leaving_cert/mathematics.py` (marimo notebook, teacher view, all NCCA LOs visible, BGE-M3 semantic search over quest packs)
- [ ] T3.10 Smoke test: run `mise run dagster:oideachais`, materialise the math assets, confirm the QuestPack row count > 0
- [ ] T3.11 Open the math notebook: `marimo edit cianfhoghlaim/notebooks/leaving_cert/mathematics.py`

## Phase 4: Per-subject scaffold for the remaining 7 subjects (template applied)

Same 9 files per subject, copied from the Mathematics template with subject-specific BAML functions + ADK tool names:

- [ ] T4.1 Applied Mathematics: T4.1.1 baml/qpack_applied_mathematics.baml ... T4.1.9 notebooks/leaving_cert/applied_mathematics.py
- [ ] T4.2 Chemistry: T4.2.1 baml/qpack_chemistry.baml ... T4.2.9 notebooks/leaving_cert/chemistry.py
- [ ] T4.3 Geography: T4.3.1 baml/qpack_geography.baml ... T4.3.9 notebooks/leaving_cert/geography.py
- [ ] T4.4 History: T4.4.1 baml/qpack_history.baml ... T4.4.9 notebooks/leaving_cert/history.py
- [ ] T4.5 English: T4.5.1 baml/qpack_english.baml ... T4.5.9 notebooks/leaving_cert/english.py
- [ ] T4.6 Gaeilge: T4.6.1 baml/qpack_gaeilge.baml ... T4.6.9 notebooks/leaving_cert/gaeilge.py
- [ ] T4.7 Computer Science: T4.7.1 baml/qpack_computer_science.baml ... T4.7.9 notebooks/leaving_cert/computer_science.py
- [ ] T4.8 Update `cianfhoghlaim/agents/adk/root_agent.py` to route keyword-level traffic to all 8 subject agents (using `ROUTING_KEYWORDS` map)

## Phase 5: Hybrid x402 educational credential

- [ ] T5.1 Create `cianfhoghlaim/badges/__init__.py`
- [ ] T5.2 Create `cianfhoghlaim/badges/schema.py` — Pydantic models: `SkillTreeBadge`, `EvidenceLink`, `CredentialAnchor`, `MerkleBatch`
- [ ] T5.3 Create `cianfhoghlaim/badges/ledger.py` — Convex wrapper (read/write badge)
- [ ] T5.4 Create `cianfhoghlaim/badges/graph.py` — FalkorDB writer (cross-realm mastery edges)
- [ ] T5.5 Create `cianfhoghlaim/badges/vector.py` — LanceDB writer (BGE-M3 1024-dim embedding of `evidence + subject + competency`)
- [ ] T5.6 Create `cianfhoghlaim/badges/anchor.py` — Hono endpoint `/api/cred/anchor` that publishes daily Merkle root to Base L2
- [ ] T5.7 Create `cianfhoghlaim/badges/anchor_contract.py` — `CredAnchor.sol` ABI + helper
- [ ] T5.8 Author `CredAnchor.sol` (Solidity) and deploy to Base L2 testnet
- [ ] T5.9 Create `cianfhoghlaim/badges/README.md` — design doc + Merkle path verification example
- [ ] T5.10 Add a Dagster asset `daily_credential_anchor` to `cianfhoghlaim/dagster/assets/credential_assets.py`
  - Cron: `0 2 * * *` (02:00 UTC daily)
  - Reads new badges from Convex since last anchor
  - Computes Merkle root, calls `CredAnchor.publish(root, batchId)` via Hono
  - Writes the on-chain `tx_hash` back into each badge row

## Phase 6: TanStack Start 2D game client

- [ ] T6.1 Create `cianfhoghlaim/web/apps/cianfhoghlaim-mmo/` (TanStack Start app)
- [ ] T6.2 Wire to existing Hono API (`cianfhoghlaim/web/hono-api/`)
- [ ] T6.3 Wire to existing Convex deployment
- [ ] T6.4 Wire to existing CopilotKit runtime (AG-UI consumer)
- [ ] T6.5 Add 8 subject realm routes (`/realm/{subject}`) — 1 per Phase 4
- [ ] T6.6 Add `/student/<id>/badges` route (badge wallet, off-chain + on-chain anchor lookup)
- [ ] T6.7 Add `/student/<id>/mastery` route (cross-subject mastery dashboard, reads FalkorDB)
- [ ] T6.8 Add `/teacher/<class>/quests` route (teacher view, marimo-embedded quest designer)
- [ ] T6.9 Add `/anchor/<date>` route (public Merkle-root proof page, verifies against Base L2)
- [ ] T6.10 Add `package.json` workspace entry to root `package.json`
- [ ] T6.11 Add turbo pipeline entry to root `turbo.json`
- [ ] T6.12 Wire BetterAuth (email/password + SIWE wallet) using existing `agent-fleet-orchestration` skill
- [ ] T6.13 Add bilingual EN + GA UI strings using existing i18n pattern
- [ ] T6.14 Smoke test: `bun run dev` in `cianfhoghlaim-mmo/`, navigate to all 8 realm pages, confirm quest packs load

## Phase 7: NCCA-only narrowing (mechanical refactor)

- [ ] T7.1 Move `cianfhoghlaim/dlt/british_isles/{sct,wls,ni,jey,iom,ggy}/` → `.archive/dlt/british_isles_other/`
- [ ] T7.2 Add a CHANGELOG entry noting the narrowing
- [ ] T7.3 Update any `.agents/skills/` references to `british_isles_*` to point at `ncca_*`
- [ ] T7.4 Run `mise run turbo typecheck` to confirm nothing broke
- [ ] T7.5 Run `mise run lint:skills` to confirm nothing broke

## Phase 8: Documentation + cross-references

- [ ] T8.1 Update `openspec/AGENTS.md` quadrant map (drop tuatha line, add cianfhoghlaim-mmo)
- [ ] T8.2 Update `openspec/project.md` capability list (add `cianfhoghlaim-educational-mmo`)
- [ ] T8.3 Update `AGENTS.md` (root) skill references
- [ ] T8.4 Add `cianfhoghlaim/badges/README.md` (cross-referenced from all 5 priority skills)
- [ ] T8.5 Add `cianfhoghlaim/web/apps/cianfhoghlaim-mmo/README.md` (product spec)
- [ ] T8.6 Add `openspec/changes/cianfhoghlaim-educational-mmo-v1/README.md` (the human-readable summary, mirrors the proposal)
- [ ] T8.7 Add 1-paragraph note to `cianfhoghlaim/README.md` under "Per-subject pipelines" mentioning the 8 subjects
- [ ] T8.8 Update `docs/openspec/changelog.md` with the new change
- [ ] T8.9 Add a `.agents/skills/cianfhoghlaim-educational-mmo/SKILL.md` (canonical skill for the new spec)
- [ ] T8.10 Update `mise.toml` aliases (add `mise run dagster:educational-mmo`, `mise run marimo:educational`)

## Phase 9: Quality gates

- [ ] T9.1 `mise run lint:skills` — 127/127 pass
- [ ] T9.2 `mise run turbo typecheck` — all packages pass
- [ ] T9.3 `mise run py:typecheck` — Python packages pass
- [ ] T9.4 `mise run dagster:oideachais` — Dagster UI launches, all 8 subject asset groups visible
- [ ] T9.5 Manual smoke test: complete 1 formative quest in each of the 8 subject realms, confirm a `SkillTreeBadge` row is created in Convex + a FalkorDB node
- [ ] T9.6 Manual smoke test: trigger `daily_credential_anchor` asset, confirm the Merkle root lands on Base L2 testnet within 5 minutes
- [ ] T9.7 `openspec validate cianfhoghlaim-educational-mmo-v1 --strict` — final pass
- [ ] T9.8 `bun run ccc:search "qpack_mathematics"` — returns the new file

## Phase 10: Commit + push (DO NOT COMMIT UNTIL EXPLICITLY ASKED)

- [ ] T10.1 Stage the changes (per the user's "Landing the Plane" protocol in AGENTS.md)
- [ ] T10.2 `git pull --rebase`
- [ ] T10.3 Hand off to user for explicit commit + push authorisation