# Tasks: Dagster Skill + Test Audit v1

> 3 sections, 6 tasks. All tasks MUST pass before
> `openspec archive 2026-09-13-dagster-skill-and-test-audit-v1 --yes`.

## Phase A — Skill update (5 min)

- [x] **A.1** Update `.agents/skills/dagster/SKILL.md` description (42→150+ assets)
- [x] **A.2** Add "⚠️ CURRENT STATUS" section with jurisdiction_assets_base ABC + lost factory note

## Phase B — Health tests (10 min)

- [x] **B.1** Author `tests/dagster/__init__.py` + `tests/dagster/test_dagster.py`
- [x] **B.2** Add 8 health tests (lib version, asset/asset_check counts, base, shims, dg CLI, imports, factory placeholder)

## Phase C — Validation (5 min)

- [ ] **C.1** `uv run pytest tests/dagster/ -v` all 8 pass
- [ ] **C.2** `uv run openspec validate 2026-09-13-dagster-skill-and-test-audit-v1 --strict` exits 0
- [ ] **C.3** `uv run openspec archive 2026-09-13-dagster-skill-and-test-audit-v1 --yes`
