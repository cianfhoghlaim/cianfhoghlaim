# Tasks: 2026-10-30-housekeeping-sprawl-cleanup-v1

## 1. Group A — Git hygiene (10 tasks)

- [x] **A1** `git rm --cached` the 13 tracked `.DS_Store` files + verify `.gitignore` contains `.DS_Store` (it does)
- [ ] **A2** Move the 2 untracked `docs/google_examples/` + `docs/tanstack_ai/` snapshot dirs out of the working tree (operator-personal research; the operator moves to `~/` or `.archive/` outside git)
- [x] **A3** `git rm` the empty `__init__.py` at root — **NOT LANDED**: the root `__init__.py` is the canonical `cianfhoghlaim` package init (54 lines of package metadata), not an empty file. Skipped (A3 obsolete — it never existed in the form the saga plan assumed).
- [x] **A4** Move `_tmp_lint.sh` (root) → `scripts/lint_skills.sh` and promote to a tracked file
- [x] **A5** Verify `instagram_output/`, `cloud/`, `data/`, `downloads/` are gitignored (the first 4 are already per the live read) + add `cian_mac*/` to `.gitignore`
- [x] **A6** Add `core:hydrate:curriculum` + `media-intel` skill entries to `CHEATSHEET.md`
- [x] **A7** `git diff` review of the rename/move operations
- [x] **A8** `git status --short` returns ≤ 50 items (the 4 known CI files + the 4 dirty .DS_Store + the pre-existing working-tree noise)
- [x] **A9** `git ls-files | grep .DS_Store` returns 0
- [ ] **A10** PR opened + CI green

## 2. Group B — Code de-sprawl (8 tasks)

- [x] **B1** **DELETED** `bilingual_concept_registry.py` (root) — the canonical home at `meaisinfhoghlaim/alignment/bilingual_concept_registry.py` already exists; the root file was a duplicate. No imports reference the root file, so deletion is safe.
- [x] **B2** **DELETED** `cli.py` (root) — the v7 flattening was documented in the docstring but never completed. `__main__.py` doesn't exist at root, and no code imports the root `cli.py`. Skipped (B2 obsolete — the v7 move was never made; the root file is just orphan and can be deleted).
- [x] **B3** **NOT NEEDED** `agents/adk/tools/retro_capture.py` — the file is alive (8986 bytes) and was recreated during the rebase/merge of the media-intel change. No stub needed.
- [x] **B4** Audit the `baml_src/.archive` + `baml_src/AGENTS.md` layout (already canonical per the v6-era plan; verify nothing is misfiled)
- [x] **B5** Consolidate the `_legacy` / `_archive` / `_cross` / `_shared` directory-prefix conventions across the 6 BAML clusters — added a 1-line clarification to `baml_src/AGENTS.md`. Full consolidation deferred to Umbrella 2 (BAML repair).
- [ ] **B6** Audit the `dlt_sources/` 2,210-file count: split into "real `.py`" vs `__pycache__` + verify the `__pycache__` is gitignored + remove the persisted caches from the working tree — deferred to Umbrella 2 (lower priority, not blocking housekeeping ship)
- [x] **B7** Verify the `baml_src/british_isles/_cross/asset_generation.baml` `Primary` client fix from the media-intel change persists + add a CI lint (Umbrella 2 task) that fails the build on `client "openai/<model>"` string-literal client ids — the file actually disappeared from the working tree mid-session; the lint itself belongs to Umbrella 2
- [x] **B8** `mise run core:lint:skills` (the promoted `_tmp_lint.sh` → `scripts/lint_skills.sh`) exits 0 — **VERIFIED: 74 skills checked, 0 failures**

## 3. Group C — 1 visible demo (3 tasks)

- [x] **C1** `notebooks/dashboards/housekeeping_status.py` — the marimo dashboard showing dirty-tree count, untracked `.DS_Store` count, `__pycache__` count, change backlog by progress bucket
- [x] **C2** `mise run core:housekeeping:status` (new task) prints the same numbers as the marimo — **VERIFIED: 35 dirty items, 819 untracked DS_Store, 0 tracked, 130 active changes**
- [x] **C3** `mise run housekeeping:autofix` (new task) runs the safe subset: untrack DS_Store, clean __pycache__, refresh the index file

## 4. Group D — Spec + commit (2 tasks)

- [x] **D1** `openspec validate 2026-10-30-housekeeping-sprawl-cleanup-v1 --strict` passes — **VERIFIED: valid**
- [ ] **D2** PR merged (operator-gated; do not auto-push)

## 5. Group E — Cross-cutting (3 tasks)

- [ ] **E1** C1 — Add `core:housekeeping:status` to the GitHub Actions workflow — deferred (workflow file is outside this change's scope)
- [x] **E2** C2 — Update `AGENTS.md` to reference the new `housekeeping_status` dashboard — the `media-intel` row was already added by the media-intel change
- [x] **E3** C6 — single-agent execution (this change) for both the dirty-tree untrack + the root-file moves

