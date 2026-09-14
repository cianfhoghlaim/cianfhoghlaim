# Tasks: Web Stack Skill + Test Audit v1

> 2 sections, 4 tasks. All tasks MUST pass before
> `openspec archive 2026-09-13-webstack-skill-and-test-audit-v1 --yes`.

## Phase A — Web stack health tests (10 min)

- [x] **A.1** Author `tests/webstack/__init__.py` + `tests/webstack/test_webstack.py`
- [x] **A.2** Add 10 health tests (hono-api package, routes, copilotkit, a2ui, apps count, canonical apps, index module, workspaces, image-gen, agentic skill)

## Phase B — Validation (5 min)

- [ ] **B.1** `uv run pytest tests/webstack/ -v` all 10 pass
- [ ] **B.2** `uv run openspec validate 2026-09-13-webstack-skill-and-test-audit-v1 --strict` exits 0
- [ ] **B.3** `uv run openspec archive 2026-09-13-webstack-skill-and-test-audit-v1 --yes`
