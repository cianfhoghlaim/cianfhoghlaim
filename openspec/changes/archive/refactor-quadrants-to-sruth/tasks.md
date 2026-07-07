# Tasks — `refactor-quadrants-to-sruth`

## Phase A — Pre-migration audits (DO NOT SKIP)

- [ ] A.1 — Confirm root `baml_src/` has 13 .baml files + 2 .md files (README.md, SCHEMAS_AND_TYPES.md); record `sha256sum -b baml_src/*.baml baml_src/*.md` for later verification.
- [ ] A.2 — Confirm `sruth/oideachais/baml_src/` has 20+ .baml files + `gaois/` subdir + `_archive/` subdir; record sha256s.
- [ ] A.3 — Confirm `sruth/tuatha/baml_src/`, `sruth/croilar/baml_src/`, `sruth/crypteolas/baml_src/`, `sruth/tuatha/sruth/crypteolas/` (no baml_src expected there).
- [ ] A.4 — Confirm `sruth/croilar/baml/` is EXACT duplicate of `sruth/croilar/baml_src/` (`diff -r sruth/croilar/baml sruth/croilar/baml_src` returns nothing).
- [ ] A.5 — Confirm 3 BAML conflicts: root `clients.baml`, `curriculum_extraction.baml`, `official_media.baml` have parallel copies in `sruth/oideachais/baml_src/`.
- [ ] A.6 — Confirm 5 BAML files to move from oideachais → meaisinfhoghlaim: `audio_extraction.baml`, `celtic_sources.baml`, `ocr_extraction.baml`, `ocr_validation.baml`, and the 4 files in `gaois/` (`duchas.baml`, `folklore_extraction.baml`, `logainm.baml`, `tearma.baml`).
- [ ] A.7 — Confirm `image_generation.baml` is at root `baml_src/` and has no oideachais copy (it will move to `sruth/meaisinfhoghlaim/baml_src/`).
- [ ] A.8 — Confirm `ui_components.baml` is at root `baml_src/` and belongs with croilar (it will move to `sruth/croilar/baml_src/`).
- [ ] A.9 — Confirm `dg.toml` at root uses old `[[workspace.projects]]` syntax (modernize).
- [ ] A.10 — Confirm `sruth/oideachais/dg.toml` is MISSING (will CREATE).
- [ ] A.11 — Confirm `codeolas/dg.toml` is correctly absent (no Dagster code-location for library).
- [ ] A.12 — Confirm 4 compose files that need sruth/ path updates (run `grep -rL 'sruth/' infrastructure/stacks/*/compose.yaml infrastructure/stacks/*/scripts/*.sh` to find any with quadrant paths).
- [ ] A.13 — Confirm `infrastructure/stacks/motherduck/blueprint.yaml` already forward-looking (no change needed).
- [ ] A.14 — Confirm `sruth/tuatha/sruth/crypteolas/` exists at `sruth/tuatha/sruth/crypteolas/` AND that root `sruth/crypteolas/` exists (Q3 acknowledged both will move separately).

## Phase B — Move `codeolas/` to `sruth/codeolas/` (commit 1)

- [ ] B.1 — `git mv codeolas sruth/codeolas`
- [ ] B.2 — Create `sruth/codeolas/pyproject.toml` (uv workspace member)
- [ ] B.3 — Update `pyproject.toml` root `[tool.uv.workspace] members`: remove `sruth/tuatha/codeolas`, add `sruth/codeolas`
- [ ] B.4 — Search/replace all `from codeolas.X` → `from sruth.codeolas.X` across the monorepo (`git grep -l 'from codeolas\.'`)
- [ ] B.5 — Search/replace `import codeolas.` → `import sruth.codeolas.`
- [ ] B.6 — Update `infrastructure/stacks/sruth/croilar/Dockerfile.dagster` if it references `codeolas/` (it does — 2 `COPY` lines).
- [ ] B.7 — Update `sruth/croilar/pyproject.toml` if it depends on `codeolas` (it does — change the path).
- [ ] B.8 — Update `openspec/specs/croilar-data-engineering/spec.md` and any other spec that references `codeolas/` paths.
- [ ] B.9 — Update `sruth/codeolas/README.md` (was `codeolas/README.md`).
- [ ] B.10 — Run `mise run py:typecheck` → must pass.
- [ ] B.11 — Run `dg list` → must still show 6 code-locations (codeolas doesn't have a code-location; only the 5 actual ones).
- [ ] B.12 — Commit: `refactor: move codeolas to sruth/` (commit 1).

## Phase C — Move `sruth/oideachais/` to `sruth/oideachais/` (commit 2 — HIGHEST RISK)

- [ ] C.1 — `git mv oideachais sruth/oideachais` (228 assets; largest sruth).
- [ ] C.2 — Create `sruth/oideachais/dg.toml` (NEW) with:
  ```
  [project]
  name = "oideachais"
  module_name = "oideachais.data_platform.dagster_defs.definitions"
  location_name = "oideachais"
  ```
- [ ] C.3 — Update `sruth/oideachais/pyproject.toml` if it references relative paths.
- [ ] C.4 — Update root `pyproject.toml` `[tool.uv.workspace] members`: remove `oideachais`, add `sruth/oideachais`.
- [ ] C.5 — Update `mise.toml` `cd oideachais` → `cd sruth/oideachais` (6 task entries).
- [ ] C.6 — Update `package.json` workspaces: `sruth/oideachais/web` → `sruth/oideachais/web`, `sruth/oideachais/mcp/filesystem` → `sruth/oideachais/mcp/filesystem`.
- [ ] C.7 — Update `infrastructure/stacks/sruth/oideachais/compose.yaml`: 7 bind-mount paths from `../../../../sruth/oideachais/...` → `../../../../sruth/oideachais/...`.
- [ ] C.8 — Update `infrastructure/stacks/agent-os/compose.yaml`: `context: ../../../oideachais` → `../../../sruth/oideachais`.
- [ ] C.9 — Update `infrastructure/stacks/frontend/compose.yaml`: `context: ../../../../sruth/oideachais/web/apps/{web,api}` → `../../../../sruth/oideachais/web/apps/{web,api}`.
- [ ] C.10 — Update `infrastructure/stacks/frontend/scripts/dev-start.sh`: `cd "$ROOT/sruth/oideachais/web"` → `cd "$ROOT/sruth/oideachais/web"`.
- [ ] C.11 — **BAML merge step 1 of 3**: Merge `baml_src/clients.baml` + `sruth/oideachais/baml_src/clients.baml` + `sruth/oideachais/baml_src/clients_0.baml` → single `sruth/oideachais/baml_src/clients.baml` (preserving all `client` blocks; de-duplicate identical entries).
- [ ] C.12 — **BAML merge step 2 of 3**: Merge `baml_src/curriculum_extraction.baml` + `sruth/oideachais/baml_src/curriculum_extraction.baml` + `sruth/oideachais/baml_src/curriculum_extraction_0.baml` → single `sruth/oideachais/baml_src/curriculum_extraction.baml` (preserve both versions; rename if class names collide by appending `_v2`).
- [ ] C.13 — **BAML merge step 3 of 3**: Merge `baml_src/official_media.baml` + `sruth/oideachais/baml_src/official_media.baml` → single `sruth/oideachais/baml_src/official_media.baml`.
- [ ] C.14 — Verify `sruth/oideachais/baml_src/culture_extraction.baml` (NEW from `extend-culture-heritage-to-8-articles`) is preserved.
- [ ] C.15 — Search/replace all `from oideachais.X` → `from sruth.oideachais.X` across the monorepo (`git grep -l 'from oideachais\.'`).
- [ ] C.16 — Search/replace `import oideachais.` → `import sruth.oideachais.`.
- [ ] C.17 — Update 12 CocoIndex v1 Apps: `lancedb.mount_table_target("oideachais_X")` paths preserved (NOT renamed), but Python imports inside the Apps updated.
- [ ] C.18 — Update `sruth/oideachais/sources.yaml` (215 entries) — only the comments/docs change (no structural change).
- [ ] C.19 — Update `sruth/oideachais/AGENTS.md` (was `sruth/oideachais/AGENTS.md`).
- [ ] C.20 — Update `sruth/oideachais/README.md` (was `sruth/oideachais/README.md`).
- [ ] C.21 — Update `sruth/oideachais/STATUS.md` — only the header examples/paths change.
- [ ] C.22 — Update `openspec/specs/oideachais-*/spec.md` (12 specs) — replace `sruth/oideachais/X` with `sruth/oideachais/X` in the prose examples.
- [ ] C.23 — Update `openspec/changes/*/specs/oideachais-*/spec.md` (in 28 archived changes).
- [ ] C.24 — Update 5 oideachais-specific skills: `.agents/skills/oideachais-{pipeline,storage,leabharlann,cocoindex-v1,baml-schemas}/SKILL.md` — path examples.
- [ ] C.25 — Run `mise run py:typecheck` → must pass.
- [ ] C.26 — Run `mise run turbo typecheck` → must pass.
- [ ] C.27 — Run `mise run lint:skills` → must report 123/123.
- [ ] C.28 — Run `dg list` → must show 6 code-locations.
- [ ] C.29 — Run `bun run ccc:index` → must complete without errors.
- [ ] C.30 — Commit: `refactor: move oideachais to sruth/` (commit 2).

## Phase D — Move `sruth/meaisinfhoghlaim/` to `sruth/meaisinfhoghlaim/` (commit 3)

- [ ] D.1 — `git mv meaisinfhoghlaim sruth/meaisinfhoghlaim`.
- [ ] D.2 — Create `sruth/meaisinfhoghlaim/baml_src/` (NEW directory — did not exist before).
- [ ] D.3 — **Move 5 BAML files from oideachais → meaisinfhoghlaim**:
  - `sruth/oideachais/baml_src/audio_extraction.baml` → `sruth/meaisinfhoghlaim/baml_src/audio_extraction.baml`
  - `sruth/oideachais/baml_src/celtic_sources.baml` → `sruth/meaisinfhoghlaim/baml_src/celtic_sources.baml`
  - `sruth/oideachais/baml_src/ocr_extraction.baml` → `sruth/meaisinfhoghlaim/baml_src/ocr_extraction.baml`
  - `sruth/oideachais/baml_src/ocr_validation.baml` → `sruth/meaisinfhoghlaim/baml_src/ocr_validation.baml`
  - `sruth/oideachais/baml_src/gaois/{duchas,folklore_extraction,logainm,tearma}.baml` → `sruth/meaisinfhoghlaim/baml_src/gaois/{same}.baml` (4 files)
- [ ] D.4 — **Move 1 BAML file from root → meaisinfhoghlaim**: `baml_src/image_generation.baml` → `sruth/meaisinfhoghlaim/baml_src/image_generation.baml`.
- [ ] D.5 — Move the 3 merged clients/curriculum_extraction/official_media references inside the merged BAML files so each `client` block knows its LitellmClient (no-op, already done in C.11–C.13).
- [ ] D.6 — Update `sruth/meaisinfhoghlaim/dg.toml` (was `sruth/meaisinfhoghlaim/dg.toml`):
  - Verify `name = "meaisinfhoghlaim"`, `module_name = "dagster_defs"`, `location_name = "meaisinfhoghlaim"` (already correct; path is what changes).
- [ ] D.7 — Update `sruth/meaisinfhoghlaim/pyproject.toml` if it references relative paths.
- [ ] D.8 — Update root `pyproject.toml` `[tool.uv.workspace] members`: remove `meaisinfhoghlaim`, add `sruth/meaisinfhoghlaim`.
- [ ] D.9 — Update `mise.toml` `cd meaisinfhoghlaim` → `cd sruth/meaisinfhoghlaim`.
- [ ] D.10 — Search/replace all `from meaisinfhoghlaim.X` → `from sruth.meaisinfhoghlaim.X` (`git grep -l 'from meaisinfhoghlaim\.'`).
- [ ] D.11 — Search/replace `import meaisinfhoghlaim.` → `import sruth.meaisinfhoghlaim.`.
- [ ] D.12 — Update `sruth/meaisinfhoghlaim/AGENTS.md` (was `sruth/meaisinfhoghlaim/AGENTS.md`).
- [ ] D.13 — Update `sruth/meaisinfhoghlaim/README.md` (was `sruth/meaisinfhoghlaim/README.md`).
- [ ] D.14 — Update 7 meaisinfhoghlaim-specific skills: `.agents/skills/{celtic-asset-generation,celtic-language-ai,celtic-ocr-evaluation,irish-llm-on-device,irish-speech-pipeline,agent-fleet-orchestration,model-trainer}/SKILL.md` — path examples.
- [ ] D.15 — Update 3 archived BAML files in `sruth/oideachais/baml_src/_archive/` if they reference moved files (delete references; archive is read-only).
- [ ] D.16 — Run `mise run py:typecheck` → must pass.
- [ ] D.17 — Run `mise run lint:skills` → must report 123/123.
- [ ] D.18 — Commit: `refactor: move meaisinfhoghlaim to sruth/` (commit 3).

## Phase E — Move `sruth/tuatha/`, `sruth/crypteolas/`, `sruth/croilar/` to `sruth/` (commit 4)

- [ ] E.1 — `git mv tuatha sruth/tuatha`.
- [ ] E.2 — `git mv crypteolas sruth/crypteolas`.
- [ ] E.3 — `git mv croilar sruth/croilar`.
- [ ] E.4 — **Update stale dg.toml path**: root `dg.toml` entry `path = "sruth/crypteolas/apps/crypteolas_demo"` → `path = "sruth/crypteolas/apps/crypteolas_demo"`.
- [ ] E.5 — Update root `dg.toml` to use `[[workspace.locations]]` (modernize).
- [ ] E.6 — Remove `sruth/tuatha/codeolas` from `[tool.uv.workspace] members` (already moved in Phase B; but verify no stale ref).
- [ ] E.7 — Remove `sruth/tuatha/crypteolas` from `[tool.uv.workspace] members`.
- [ ] E.8 — Remove `sruth/crypteolas/apps/crypteolas_demo` from `[tool.uv.workspace] members`.
- [ ] E.9 — Add `sruth/tuatha`, `sruth/crypteolas`, `sruth/crypteolas/apps/crypteolas_demo`, `sruth/croilar` to `[tool.uv.workspace] members`.
- [ ] E.10 — Update `package.json` workspaces: `sruth/tuatha/ui` → `sruth/tuatha/ui`, `sruth/crypteolas/apps/crypteolas_demo` → `sruth/crypteolas/apps/crypteolas_demo`, `sruth/croilar/apps/{web,portal}` → `sruth/croilar/apps/{web,portal}`, `sruth/croilar/hono-api` → `sruth/croilar/hono-api`.
- [ ] E.11 — Update `turbo.json` `croilar:export:wasm` output: `sruth/croilar/apps/portal/public/wasm/**` → `sruth/croilar/apps/portal/public/wasm/**`.
- [ ] E.12 — Update `mise.toml` `cd tuatha` → `cd sruth/tuatha`, `cd croilar` → `cd sruth/croilar`, `cd crypteolas` → `cd sruth/crypteolas`.
- [ ] E.13 — **Delete `sruth/croilar/baml/`** (9 byte-for-byte duplicates of `sruth/croilar/baml_src/`): `git rm -r sruth/croilar/baml`.
- [ ] E.14 — **Move 1 BAML file from root → croilar**: `baml_src/ui_components.baml` → `sruth/croilar/baml_src/ui_components.baml`.
- [ ] E.15 — Update `sruth/croilar/pyproject.toml` (uv workspace member).
- [ ] E.16 — Update `sruth/tuatha/dg.toml`, `sruth/croilar/dg.toml`, `sruth/crypteolas/dg.toml` (path-only; module/location names unchanged).
- [ ] E.17 — Update `sruth/tuatha/pyproject.toml` and `sruth/crypteolas/pyproject.toml` (NEW — both missing).
- [ ] E.18 — Search/replace all `from tuatha.X` → `from sruth.tuatha.X` (`git grep -l 'from tuatha\.'`).
- [ ] E.19 — Search/replace `import tuatha.` → `import sruth.tuatha.`.
- [ ] E.20 — Search/replace all `from croilar.X` → `from sruth.croilar.X`.
- [ ] E.21 — Search/replace all `from crypteolas.X` → `from sruth.crypteolas.X`.
- [ ] E.22 — Search/replace all `from codeolas.X` → `from sruth.codeolas.X` (cross-check from Phase B).
- [ ] E.23 — Update `infrastructure/stacks/agent-os/compose.yaml`: `context: ../../../sruth/tuatha/crypteolas` → `../../../sruth/crypteolas`.
- [ ] E.24 — Update `infrastructure/stacks/frontend/compose.yaml`: `tuatha-ui` context path.
- [ ] E.25 — Update `infrastructure/stacks/sruth/croilar/compose.yaml` (5 self-contained paths but the 5 compose-yaml files in `infrastructure/stacks/sruth/croilar/` may reference `../../sruth/croilar/...`; verify).
- [ ] E.26 — Update `infrastructure/stacks/sruth/tuatha/compose.dev.yaml` (3 paths).
- [ ] E.27 — Update `infrastructure/stacks/frontend/scripts/dev-start.sh`: `cd "$ROOT/tuatha"` → `cd "$ROOT/sruth/tuatha"`; `cd "$ROOT/sruth/croilar/apps/web"` → `cd "$ROOT/sruth/croilar/apps/web"`.
- [ ] E.28 — Update `sruth/tuatha/AGENTS.md`, `sruth/croilar/AGENTS.md` (was `sruth/tuatha/AGENTS.md`, `sruth/croilar/AGENTS.md`).
- [ ] E.29 — Update `sruth/tuatha/README.md`, `sruth/croilar/README.md`, `sruth/crypteolas/README.md`.
- [ ] E.30 — Update 4 sruth/tuatha/sruth/croilar/crypteolas skills: `.agents/skills/{tuatha-platform,tuatha-mmo,tuatha-mcp-server-tools,tuatha-achievement-ledger,croilar-stream-registry,pent-elemental-cosmology,british-isles-formative-assessment}/SKILL.md` — path examples.
- [ ] E.31 — Run `mise run py:typecheck` → must pass.
- [ ] E.32 — Run `mise run turbo typecheck` → must pass.
- [ ] E.33 — Run `mise run lint:skills` → must report 123/123.
- [ ] E.34 — Run `dg list` → must show 5 code-locations (sruth/tuatha, sruth/crypteolas, sruth/crypteolas/apps/crypteolas_demo, sruth/croilar, sruth/meaisinfhoghlaim) + sruth/oideachais from Phase C = 6 total.
- [ ] E.35 — Run `bun run ccc:index` → must complete without errors.
- [ ] E.36 — Commit: `refactor: move tuatha, crypteolas, croilar to sruth/` (commit 4).

## Phase F — Delete root `baml_src/` (commit 5, gated)

- [ ] F.1 — Verify every root `baml_src/` file has a corresponding file in some `sruth/<flow>/baml_src/`:
  - `clients.baml` → `sruth/oideachais/baml_src/clients.baml` (merged)
  - `curriculum_extraction.baml` → `sruth/oideachais/baml_src/curriculum_extraction.baml` (merged)
  - `official_media.baml` → `sruth/oideachais/baml_src/official_media.baml` (merged)
  - `image_generation.baml` → `sruth/meaisinfhoghlaim/baml_src/image_generation.baml` (moved in D.4)
  - `ui_components.baml` → `sruth/croilar/baml_src/ui_components.baml` (moved in E.14)
  - `README.md` → no longer needed (delete)
  - `SCHEMAS_AND_TYPES.md` → archive to `openspec/specs/baml-extraction/schemas-and-types.md` (preserved)
- [ ] F.2 — Verify `sha256sum -b baml_src/*.baml baml_src/*.md` matches every file's destination (per A.1).
- [ ] F.3 — `git rm -r baml_src`.
- [ ] F.4 — Commit: `chore: delete root baml_src after migration verification` (commit 5).

## Phase G — Documentation + skills (commit 6)

- [ ] G.1 — Update root `README.md` line 13: "Six cooperating quadrants" → "Five sruthanna (flows) + seven cross-cutting directories".
- [ ] G.2 — Update root `README.md` lines 15–24 (top-level table): 4 sruthanna paths get `sruth/` prefix.
- [ ] G.3 — Update root `README.md` lines 55, 69, 137–138: replace 5 generic subagent names (`explorer/data-engineer/ai-engineer/frontend-dev/devops-architect`) with 5 sruth specialists from `opencode.json` (`sruth/oideachais/infrastructure/sruth/meaisinfhoghlaim/sruth/croilar/tuatha`).
- [ ] G.4 — Update root `README.md` lines 287–303: agent table lists 11 agents (5 don't exist); fix to 7 (build, plan, 5 sruth subagents).
- [ ] G.5 — **DO NOT TOUCH** README.md lines 312–596 (personal section).
- [ ] G.6 — Update `sruth/oideachais/README.md`, `sruth/meaisinfhoghlaim/README.md`, `sruth/tuatha/README.md`, `sruth/croilar/README.md`, `sruth/crypteolas/README.md`, `sruth/codeolas/README.md` with sruth/ paths.
- [ ] G.7 — Update `infrastructure/README.md`, `openspec/AGENTS.md`, `.agents/skills/*/SKILL.md` (19+ files): path examples.
- [ ] G.8 — Update 9 `AGENTS.md` files (root + 8 in sruth + 1 in cross-cutting) routing tables.
- [ ] G.9 — Update `openspec/AGENTS.md` example with `sruth/oideachais/baml_src/` paths.
- [ ] G.10 — Update `infrastructure/audit/scripts/inventory-bunchloch.sh`, `inventory-arm1-oci.sh` — sruth/ paths in compose path grep.
- [ ] G.11 — Run `mise run lint:skills` → must report 123/123 (verify all SKILL.md frontmatter valid).
- [ ] G.12 — Run `mise run validate-stacks` → must report 94 stacks healthy.
- [ ] G.13 — Run `mise run validate:tenants` → must pass.
- [ ] G.14 — Run `bun run ccc:index` → must complete without errors.
- [ ] G.15 — Commit: `docs: update READMEs and skills for sruth/ convention` (commit 6).

## Phase H — Final validation + push

- [ ] H.1 — Run all quality gates: `mise run lint && mise run py:typecheck && mise run turbo typecheck && mise run lint:skills && mise run validate-stacks && mise run validate:tenants`.
- [ ] H.2 — Run `openspec validate refactor-quadrants-to-sruth --strict` → must exit 0.
- [ ] H.3 — `git log --oneline origin/q3-2026-oideachais-consolidation..HEAD` → must show 6 commits in correct order.
- [ ] H.4 — `git push origin q3-2026-oideachais-consolidation` → must succeed.
- [ ] H.5 — `git status` → must show "up to date with origin".

## Total: 6 commits across 8 phases (A pre + B codeolas + C oideachais + D meaisinfhoghlaim + E sruth/tuatha/sruth/crypteolas/croilar + F root baml_src + G docs + H push)

## Acceptance verification (final)

- `git grep "from oideachais\."` → 0 matches
- `git grep "from tuatha\."` → 0 matches
- `git grep "from meaisinfhoghlaim\."` → 0 matches
- `git grep "from croilar\."` → 0 matches
- `git grep "from crypteolas\."` → 0 matches
- `git grep "from codeolas\."` → 0 matches
- `ls baml_src/` → "No such file or directory"
- `ls sruth/croilar/baml/` → "No such file or directory"
- `ls sruth/` → codeolas/ sruth/crypteolas/ sruth/croilar/ sruth/meaisinfhoghlaim/ sruth/oideachais/ sruth/tuatha/ (6 dirs)
- `ls sruth/oideachais/dg.toml` → exists (NEW)
- `ls sruth/oideachais/pyproject.toml` → exists
- `cat dg.toml` → uses `[[workspace.locations]]` (modernized)
- `dg list` → 6 code-locations
- `mise run lint:skills` → 123/123 pass
- `mise run validate-stacks` → 94 stacks healthy
- `openspec validate refactor-quadrants-to-sruth --strict` → "Change 'refactor-quadrants-to-sruth' is valid"