# Tasks: Marimo Skill + Test Audit v1

> 3 sections, 6 tasks. All tasks MUST pass before
> `openspec archive 2026-09-13-marimo-skill-and-test-audit-v1 --yes`.

## Phase A — Skill correction (5 min)

- [x] **A.1** Update `.agents/skills/marimo/SKILL.md` description (6→66 notebooks)

## Phase B — Health tests (10 min)

- [x] **B.1** Author `tests/marimo/__init__.py` + `tests/marimo/test_marimo.py`
- [x] **B.2** Add 10 health tests (lib, count, patterns, template, control panel, BIEP lakehouse, official media, LC panel status, shared db, CLI)

## Phase C — Validation (5 min)

- [x] **C.1** `uv run pytest tests/marimo/ -v` all 10 pass
- [x] **C.2** `uv run openspec validate 2026-09-13-marimo-skill-and-test-audit-v1 --strict` exits 0
- [x] **C.3** `uv run openspec archive 2026-09-13-marimo-skill-and-test-audit-v1 --yes`
