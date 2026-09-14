# Tasks: Firecrawl Skill + Test Audit v1

> 3 sections, 6 tasks. All tasks MUST pass before
> `openspec archive 2026-09-13-firecrawl-skill-and-test-audit-v1 --yes`.

## Phase A — Skill update (5 min)

- [x] **A.1** Update `.agents/skills/firecrawl/SKILL.md` with CURRENT STATUS + monitor pipeline note

## Phase B — Health tests (10 min)

- [x] **B.1** Author `tests/firecrawl/__init__.py` + `tests/firecrawl/test_firecrawl.py`
- [x] **B.2** Add 8 health tests (MCP config, monitor configs, imports, skills, bunx, CLI subcommands)

## Phase C — Validation (5 min)

- [ ] **C.1** `uv run pytest tests/firecrawl/ -v` all 8 pass
- [ ] **C.2** `uv run openspec validate 2026-09-13-firecrawl-skill-and-test-audit-v1 --strict` exits 0
- [ ] **C.3** `uv run openspec archive 2026-09-13-firecrawl-skill-and-test-audit-v1 --yes`
