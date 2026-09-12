# Tasks: DLT 1.28/1.29 Feature Adoption v1

> 4 sections, 8 tasks. All tasks MUST pass before
> `openspec archive 2026-09-12-dlt-1.29-feature-adoption-v1 --yes`.

## Phase A — Skill + version verification (5 min)

- [x] **A.1** Update `.agents/skills/dlt/SKILL.md` to dlt 1.29.1 (was 1.28.1)
- [x] **A.2** Add `dlt[hub]` + verified-source-first rules to the skill

## Phase B — Per-source smoke tests (10 min)

- [x] **B.1** Author `tests/dlt/__init__.py` + `tests/dlt/test_curated_sources.py`
- [x] **B.2** Add path-exists + import-smoke + count-match tests for the 25 curated sources

## Phase C — write_disposition migration (10 min)

- [x] **C.1** Identify all `write_disposition='replace'` usages (49 hits in 29 files)
- [x] **C.2** Migrate to `refresh='drop'` (all in safe-to-drop categories per skill guide)

## Phase D — dlt[hub] install (5 min)

- [x] **D.1** Update `pyproject.toml` to include `hub` extra
- [x] **D.2** Add `test_dlt_cli_available` + `test_dlthub_cli_available` smoke tests

## Phase E — Documentation (5 min)

- [x] **E.1** Update `dlt_sources/AGENTS.md` with dlt 1.29+ commands
- [x] **E.2** Add per-source migration guide table to AGENTS.md

## Phase F — Validation (5 min)

- [x] **F.1** `mise run lint:brand` exits 0
- [x] **F.2** `uv run pytest tests/dlt/test_curated_sources.py -v` all pass (37 skipped OK — those are from lost Phase 16-29 work)
- [x] **F.3** `uv run openspec validate 2026-09-12-dlt-1.29-feature-adoption-v1 --strict` exits 0
- [x] **F.4** `uv run openspec archive 2026-09-12-dlt-1.29-feature-adoption-v1 --yes`
