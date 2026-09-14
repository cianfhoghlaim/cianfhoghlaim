# Tasks: Lakehouse Skill + Test Audit v1

> 3 sections, 6 tasks. All tasks MUST pass before
> `openspec archive 2026-09-13-lakehouse-skill-and-test-audit-v1 --yes`.

## Phase A — Skill updates (5 min)

- [x] **A.1** Update `.agents/skills/motherduck/SKILL.md` with 99-stack breakdown + destination code location
- [x] **A.2** Update `.agents/skills/ducklake/SKILL.md` + `.agents/skills/lancedb/SKILL.md` with brief CURRENT STATUS notes

## Phase B — Health tests (10 min)

- [x] **B.1** Author `tests/lakehouse/__init__.py` + `tests/lakehouse/test_lakehouse.py`
- [x] **B.2** Add 9 health tests (bonneagar stacks, dlt extra, common modules, lakehouse stack, env var, 3 skills, 3-tier dispatch)

## Phase C — Validation (5 min)

- [x] **C.1** `uv run pytest tests/lakehouse/ -v` all 9 pass
- [x] **C.2** `uv run openspec validate 2026-09-13-lakehouse-skill-and-test-audit-v1 --strict` exits 0
- [x] **C.3** `uv run openspec archive 2026-09-13-lakehouse-skill-and-test-audit-v1 --yes`
