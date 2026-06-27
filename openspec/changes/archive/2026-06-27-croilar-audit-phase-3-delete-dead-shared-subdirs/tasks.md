# Tasks: Delete dead `_shared/{observability,agents,mcp,embeddings}` subdirs

## 1. Validate change

- [x] 1.1 Run `openspec validate croilar-audit-phase-3-delete-dead-shared-subdirs --strict`

## 2. Delete dead subdirs

- [x] 2.1 Delete `sruth/croilar/_shared/observability/` (2 files, 481 lines)
- [x] 2.2 Delete `sruth/croilar/_shared/agents/` (2 files, 372 lines)
- [x] 2.3 Delete `sruth/croilar/_shared/mcp/` (2 files, 419 lines)
- [x] 2.4 Delete `sruth/croilar/_shared/embeddings/` (2 files, 124 lines)

## 3. Update parent `__init__.py`

- [x] 3.1 Patch `sruth/croilar/_shared/__init__.py` docstring (lines 1-15) — remove the "embeddings, MCP gateway, agent orchestration, and observability" clause
- [x] 3.2 Patch `sruth/croilar/_shared/__init__.py` (lines 42-44) — remove the 3 commented-out sibling imports

## 4. Verify

- [x] 4.1 `python -c "import _shared; print('PASS')"` (canonical, no fallback)
- [x] 4.2 `python -c "import _shared.database; print('PASS')"` (kept)
- [x] 4.3 `python -c "import _shared.config; print('PASS')"` (kept)
- [x] 4.4 `python -c "from _shared.streams import Stream; print('PASS')"` (kept)
- [x] 4.5 Confirm `tests/test_database.py` (the only consumer of `_shared.database`) still imports cleanly
- [x] 4.6 Run `mise run lint:skills` (must remain 123/123)

## 5. Spec delta + audit trail

- [x] 5.1 Add 1 ADDED Requirement to `openspec/specs/croilar-data-engineering/spec.md`: no-dead-croilar-shared-subdirs
- [x] 5.2 Add Known issues row to `sruth/croilar/README.md`: row #5 RESOLVED

## 6. Commit + push + archive

- [x] 6.1 `git add` only the deleted files + the patched `__init__.py` + the spec delta + the README Known issues row
- [x] 6.2 Commit (refactor)
- [x] 6.3 Push
- [x] 6.4 `openspec archive croilar-audit-phase-3-delete-dead-shared-subdirs --yes`
- [x] 6.5 Commit (spec delta + archive)
- [x] 6.6 Push