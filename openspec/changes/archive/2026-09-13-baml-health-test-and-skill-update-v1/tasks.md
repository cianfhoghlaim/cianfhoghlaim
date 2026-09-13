# Tasks: BAML Health Test + Skill Update v1

> 2 sections, 4 tasks. All tasks MUST pass before
> `openspec archive 2026-09-13-baml-health-test-and-skill-update-v1 --yes`.

## Phase A — Skill version bump (5 min)

- [x] **A.1** Update `.agents/skills/baml/SKILL.md` to v0.226.1
- [x] **A.2** Add "⚠️ CURRENT STATUS" section documenting broken stubs

## Phase B — BAML health tests (10 min)

- [x] **B.1** Author `tests/baml/__init__.py` + `tests/baml/test_baml_health.py`
- [x] **B.2** Add 4 health tests: CLI available, inventory, templates separated, generation status

## Phase C — Validation (5 min)

- [x] **C.1** `uv run pytest tests/baml/ -v` all 4 pass
- [x] **C.2** `uv run openspec validate 2026-09-13-baml-health-test-and-skill-update-v1 --strict` exits 0
- [x] **C.3** `uv run openspec archive 2026-09-13-baml-health-test-and-skill-update-v1 --yes`
