# Tasks — Phase 1.1 English lc5 wiring verification

## Pre-flight

- [x] **P.1** `git checkout pick-4-biep-v1` (already on branch)
- [x] **P.2** `git status -sb` shows `pick-4-biep-v1...origin/pick-4-biep-v1` (in sync)
- [x] **P.3** Acknowledge 3 pre-existing dirty paths in working tree
      (NOT in my scope; flagged for the parallel agents who own them):
      - `M .gitignore`
      - `D ocr/__init__.py`
      - `D ocr/models/__init__.py`
      - `D ocr/models/registry.py`
      - `M spaces/data-engineering`
      - `?? meaisinfhoghlaim/ocr/`

## Step 1 — Inspect current state (Step 1 of the build prompt)

- [x] **1.1** Inspect `leaving_cert_source.py:40-70` — `LC6_SUBJECTS`
      tuple (line 52) + `LC_PDF_KIND_REGISTRY` dict (line 64)
- [x] **1.2** Confirm `LC6_SUBJECTS` is the canonical name (no stale
      `LC5_SUBJECTS` references — `grep -n LC5_SUBJECTS` returns 0
      matches across the file)
- [x] **1.3** Confirm 2 English regex patterns in `LC_PDF_KIND_REGISTRY`:
      - `r"^LC002ALP\d{3}[EI]V\.pdf$"` → `qwen3-vl-8b` (line 67)
      - `r"^SC-English-Spec-ENG-INT.*\.pdf$"` → `gemma-4-26B-A4B` (line 73)
- [x] **1.4** Confirm `elif subject_dir.name == "english"` branch in
      `_scan_subject` (lines 137-145)
- [x] **1.5** Inspect `lc5_assets.py` — explicit `lc5_english_ingested`
      at line 121 + explicit `lc5_english_cognified` at line 226
- [x] **1.6** Confirm `english.yaml` exists at
      `orchestration/defs/1_ingestion/curriculum/lc5/english.yaml`
      (1492 bytes, dated 2026-07-10)

## Step 2 — Code work already done by prior change

> All 4 Phase 1.1 code edits were already shipped by
> `2026-07-10-wire-english-lc5-and-resolve-ie-duplicates-v1` (the
> T2 subagent at commit `ba234de61`). This change VERIFIES the
> state on disk rather than re-implementing it.

- [x] **2a.1** `leaving_cert_source.py:48` — `LC5_SUBJECTS` renamed to
      `LC6_SUBJECTS` (3 occurrences: tuple def, `for subject in LC6_SUBJECTS`,
      log message `{len(LC6_SUBJECTS)}`)
- [x] **2a.2** `leaving_cert_source.py` — `"english"` added as the 3rd
      element of `LC6_SUBJECTS` (alphabetical order)
- [x] **2a.3** `leaving_cert_source.py:_scan_subject` — `elif
      subject_dir.name == "english"` branch added (en-only at root,
      mirrors the gaeilge asymmetry)
- [x] **2a.4** `leaving_cert_source.py:LC_PDF_KIND_REGISTRY` — 2 new
      regex patterns added (line 67 + line 73)
- [x] **2a.5** `leaving_cert_source.py` — module docstring updated
      5-subject → 6-subject + `english/` listed
- [x] **2b.1** `lc5_assets.py` — `LC5_SUBJECTS` renamed to `LC6_SUBJECTS`
      (3 occurrences: tuple def, `for _subject in LC6_SUBJECTS`,
      `len(LC6_SUBJECTS)` in cross-subject payload)
- [x] **2b.2** `lc5_assets.py` — `"english"` added as 3rd element of
      `LC6_SUBJECTS` (mirrors source-side tuple)
- [x] **2b.3** `lc5_assets.py:121` — explicit `lc5_english_ingested`
      `@asset` (Layer 1, group_name `1_ingestion/curriculum/lc5`)
- [x] **2b.4** `lc5_assets.py:199-201` — factory loop bound to
      `LC6_SUBJECTS`, generates 4 English extraction assets
- [x] **2b.5** `lc5_assets.py:226` — explicit `lc5_english_cognified`
      `@asset` (Layer 3, group_name `3_model_lifecycle/lc_cognify/lc5/english`)
- [x] **2c.1** `english.yaml` — `CelticIngestionComponent` cron asset
      created (source_id `cianfhoghlaim.filesystem.leaving_cert.english`,
      cron `"0 5 * * *"`)

## Step 3 — Verification gates

- [x] **3.1** `grep -A 7 "^LC6_SUBJECTS" dlt/filesystem/leaving_cert_source.py`
      returns the 6-element tuple (chemistry, computer_science,
      **english**, gaeilge, geography, mathematics)
- [x] **3.2** AST scan of `lc5_assets.py` confirms 2 explicit
      `lc5_english_*` `@asset` decorators + the factory pattern
      `globals()[f'lc5_{_subject}_{_kind}_extracted']` iterates over
      `LC6_SUBJECTS` × 4 kinds = 24 extraction assets including the
      4 English ones
- [x] **3.3** `ls -la orchestration/defs/1_ingestion/curriculum/lc5/english.yaml`
      confirms 1492-byte file exists
- [x] **3.4** `cat english.yaml` shows `automation_cron: "0 5 * * *"`
      + `source_id: cianfhoghlaim.filesystem.leaving_cert.english`

## Step 4 — `mise run baml:generate`

- [x] **4.1** `cd cianfhoghlaim && mise run baml:generate`
      exits 0 with `[BAML INFO] Wrote 14 files to
      baml/baml_client` (verified 2026-07-10 14:03)
- [x] **4.2** The 50 `field: type` errors fixed by commit `54c21dd52`
      remain resolved (no regression from this change — no BAML files
      touched)

## Step 5 — Dagster asset list

- [ ] **5.1** `dagster asset list --select lc5_english*` —
      **BLOCKED** by the pre-existing `2026-07-11-fix-dagster-asset-group-name-regex-v1`
      bug. All `1_ingestion/curriculum/lc5` group_names fail the
      `^[A-Za-z0-9_]+$` regex in Dagster 1.13.1, so the defs can't
      load until that fix lands. NOT in scope for Phase 1.1 — affects
      all 36 lc5 assets, not just the 6 English ones.
- [x] **5.2** AST-equivalent verification: confirmed via static
      analysis that the 6 English assets are materialised by the
      module-level factory loop (Step 3.2)

## Step 6 — OpenSpec change artefacts

- [x] **6.1** `openspec/changes/2026-07-13-biep-v1-phase-1-1-english-wiring-v1/proposal.md`
- [x] **6.2** `openspec/changes/2026-07-13-biep-v1-phase-1-1-english-wiring-v1/tasks.md` (this file)
- [x] **6.3** `openspec/changes/2026-07-13-biep-v1-phase-1-1-english-wiring-v1/specs/british-isles-education-pipeline/spec.md`
      — 1 ADDED Requirement "Phase 1.1 English lc5 wiring verified complete"
- [ ] **6.4** `openspec validate 2026-07-13-biep-v1-phase-1-1-english-wiring-v1 --strict`
      must pass before commit

## Step 7 — Flagship tasks.md tick step (DEFERRED)

> **DEFERRED**: per the hard rule "Do NOT touch the 50+ archived
> openspec changes under `openspec/changes/archive/*`", I do NOT
> modify the flagship archived tasks.md at
> `openspec/changes/archive/2026-07-09-2026-07-06-british-isles-education-v1/tasks.md`.
> The flagship is frozen; its Phase 1.1 boxes remain `[ ]` in the
> archive as a historical snapshot of "boxes unchecked at archive-time".

- [x] **7.1** Documented the deferral rationale in the proposal.md
      "Hard rule respected" section
- [x] **7.2** The verification status lives in this change's own
      `tasks.md` (Steps 1-6 above) instead

## Step 8 — Commit + push

- [ ] **8.1** `git add -A` (3 new files: proposal.md, tasks.md, spec.md)
- [ ] **8.2** `git -c user.email="build-agent@cianfhoghlaim" -c user.name="Build Agent" commit -m "feat(biep): Phase 1.1 English wiring verification + spec delta"`
- [ ] **8.3** `git push --set-upstream origin pick-4-biep-v1` (NOT `main`)

## Final report deliverables

- [ ] **R.1** Commit hash
- [ ] **R.2** `openspec validate --strict` result
- [ ] **R.3** `LC6_SUBJECTS` contents (6 subjects)
- [ ] **R.4** 6 `lc5_english_*` asset names (2 explicit + 4 factory-generated)
- [ ] **R.5** `english.yaml` summary (CelticIngestionComponent + cron `0 5 * * *`)
- [ ] **R.6** 1 ADDED spec delta summary on `british-isles-education-pipeline`
- [ ] **R.7** Phase 1.1 task-tick status in the BIEP v1 flagship archive
      (DEFERRED per Step 7 — not modifying the archived tasks.md)
- [ ] **R.8** Blockers / open questions (the 3 pre-existing dirty paths
      from parallel agents; the dagster group_name regex bug tracked
      in `2026-07-11-fix-dagster-asset-group-name-regex-v1`)