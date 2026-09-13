# Tasks: CocoIndex Skill + Test Audit v1

> 3 sections, 6 tasks. All tasks MUST pass before
> `openspec archive 2026-09-13-cocoindex-skill-and-test-audit-v1 --yes`.

## Phase A — Skill version bump (5 min)

- [x] **A.1** Update `.agents/skills/cocoindex/SKILL.md` to v1.0.20

## Phase B — Health tests (10 min)

- [x] **B.1** Author `tests/cocoindex/__init__.py` + `tests/cocoindex/test_cocoindex.py`
- [x] **B.2** Add 6 health tests (lib version, flow inventory, imports, fallback, parity tests, v1 pattern)

## Phase C — Validation (5 min)

- [ ] **C.1** `uv run pytest tests/cocoindex/ -v` all 6 pass
- [ ] **C.2** `uv run openspec validate 2026-09-13-cocoindex-skill-and-test-audit-v1 --strict` exits 0
- [ ] **C.3** `uv run openspec archive 2026-09-13-cocoindex-skill-and-test-audit-v1 --yes`
