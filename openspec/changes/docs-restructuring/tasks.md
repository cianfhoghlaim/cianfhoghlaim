# Tasks: docs-restructuring

## Phase 0: Discovery

- [x] Run 4 parallel discovery agents (inventory, Cognee readiness, ccc
  readiness, agent-skill consumability) to characterise the 1,038 source
  files and current state. Reports at `docs/audit/discovery_inventory.md`,
  `cognee_readiness_audit.md`, `cocoindex_readiness_audit.md`,
  `agent_skill_consumability.md`.
- [x] Identify the 116-file nested `docs/tuatha/tuatha/` mirror as a true
  byte-for-byte copy of `docs/tuatha/` (no unique content).

## Phase 1: Design

- [x] Cluster all 1,038 files into 12 super-clusters; map to 7 numbered
  domain directories.
- [x] Define the frontmatter schema (title, domain, status, description,
  supersedes, entities, related_skills, ccc_query_hints, last_reviewed).
- [x] Define the `00_index.md` routing table structure.
- [x] Choose per-cluster Cognee cognify (one dataset per domain) with
  per-domain graph_model_file pattern (deferred to follow-up change).

## Phase 2: Migration

- [x] Move `docs/tuatha/tuatha/` mirror to `docs/archive/tuatha-mirror/`.
- [x] Create the 7 target directories + 8 archive subdirectories.
- [x] Migrate `docs/agents/` (39 files → 5 canonical) into
  `docs/03-agents/`. Archive originals in
  `docs/archive/2026-06-06-agents/`.
- [x] Migrate `docs/bonneagar/` (163 files → 8 canonical) into
  `docs/01-platform-architecture/`. Archive originals in
  `docs/archive/2026-06-06-bonneagar/`.
- [x] Migrate `docs/data_engineering/` + `docs/context/` (136 files →
  6 canonical) into `docs/02-data-platform/` (4 files) and
  `docs/07-standards/` (2 files). Archive originals in
  `docs/archive/2026-06-06-data-engineering/` and
  `docs/archive/2026-06-06-context/`.
- [x] Migrate `docs/meaisínfhoghlaim/` + `docs/teanga/` (394 files →
  8 canonical) into `docs/04-ai-ml/`. Archive originals in
  `docs/archive/2026-06-06-meaisinfhoghlaim/` and
  `docs/archive/2026-06-06-teanga/`.
- [x] Migrate `docs/web/` (68 files → 4 canonical) into `docs/05-web/`.
  Archive originals in `docs/archive/2026-06-06-web/`.
- [x] Migrate `docs/tuatha/` (116 files → 5 canonical) into
  `docs/06-product/`. Archive originals in
  `docs/archive/2026-06-06-tuatha/`.
- [x] Remove the 8 empty old subtree directories.

## Phase 3: Indexes & Scripts

- [x] Write `docs/00_index.md` — master routing table with 31 "I want
  to..." routes, 25 skill-to-doc mappings, and the consolidation
  methodology summary.
- [x] Write `docs/audit/consolidation_plan.md` — 840-line retrospective
  plan document.
- [x] Write `infrastructure/scripts/cognee-ingest-docs.py` — two-phase
  ingestion script (add + cognify per domain) with --dry-run,
  --no-cognify, --domain, --all, --summary flags.
- [x] Fix `opencode.json` — replace the unresolved `infisical://` template
  string in the Cognee MCP server's `LLM_API_KEY` with
  `${DEEPSEEK_API_KEY}` so the mise-hydrated key is picked up at
  subprocess launch.

## Phase 4: Validation

- [x] Run `bun run ccc:index` to refresh the semantic search index over
  the new file paths.
- [x] Verify ccc search returns canonical docs:
  `ccc search "secrets management infisical locket three-way contract"`
  → `docs/01-platform-architecture/secrets-management.md` (score 0.824).
- [x] Verify all 8 old subtrees removed; 36 canonical files + 00_index.md
  + 5 audit files in target structure.
- [x] Verify 946 archived originals preserved (zero content loss).
- [ ] Run `openspec validate docs-restructuring --strict` (deferred — the
  openspec binary lives outside this worktree).
- [ ] Trigger per-domain Cognee cognify() on next session restart (when
  the LLM_API_KEY fix takes effect):
  - `docs-standards` — already stored, cognify pending
  - `docs-data-platform` — pending
  - `docs-agents` — pending
  - `docs-ai-ml` — pending
  - `docs-web` — pending
  - `docs-product` — pending
  - `docs-architecture` — pending

## Phase 5: Commit & Push

- [x] Stage all changes: new canonical files, archive, audit reports,
  00_index.md, cognee-ingest-docs.py, opencode.json fix.
- [x] Commit: `docs: consolidate 1,038 files into 36 canonical documents
  across 7 domains`.
- [x] Push to origin.
- [x] Stage and commit the opencode.json fix:
  `fix(cognee): resolve LLM_API_KEY via env var reference`.
- [x] Push to origin.
