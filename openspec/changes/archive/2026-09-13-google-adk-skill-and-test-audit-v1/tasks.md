# Tasks: Google ADK Skill + Test Audit v1

> 3 sections, 6 tasks. All tasks MUST pass before
> `openspec archive 2026-09-13-google-adk-skill-and-test-audit-v1 --yes`.

## Phase A — Skill version correction (5 min)

- [x] **A.1** Update `.agents/skills/google-adk/SKILL.md` version >=2.1.0 → >=1.17.0

## Phase B — Health tests (10 min)

- [x] **B.1** Author `tests/google_adk/__init__.py` + `tests/google_adk/test_google_adk.py`
- [x] **B.2** Add 8 health tests (lib version, agent clusters, module count, imports, fallback pattern)

## Phase C — Validation (5 min)

- [x] **C.1** `uv run pytest tests/google_adk/ -v` all 8 pass
- [x] **C.2** `uv run openspec validate 2026-09-13-google-adk-skill-and-test-audit-v1 --strict` exits 0
- [x] **C.3** `uv run openspec archive 2026-09-13-google-adk-skill-and-test-audit-v1 --yes`
