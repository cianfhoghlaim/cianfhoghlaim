# Tasks: Round 11 Phase 12 (croilar Phase 1) — Delete local fallback in `sruth/croilar/dlt_utils/destinations.py`

## Pre-flight

- [x] Confirmed `sruth/croilar/dlt_utils/destinations.py` has 126 lines with 88-line local fallback (lines 38-126)
- [x] Confirmed README Known issues row #2 explicitly says "should be deleted once the oideachais workspace dep is wired"
- [x] Confirmed croilar packaging fix (commit `e9e0fc7d2`) is the precondition — already in production
- [x] Confirmed canonical `sruth.oideachais.dlt_utils.destinations.with_namespace("croilar")` exports 4 names: `NAMESPACE`, `create_pipeline`, `get_dlt_destination`, `get_duckdb_fallback_destination`
- [x] Confirmed `dlt` import is needed only by the local fallback's body, NOT by the shim
- [x] Confirmed the local fallback's `DuckLakeConfig` has 0 active callers in the repo (only the file itself + its `__init__.py` re-export use it; the `__init__.py` is updated in Phase 12)
- [x] Confirmed `get_duckdb_fallback` (without `_destination` suffix) has only 1 caller — `tests/test_smoke.py:220` — which is a pre-existing test failure documented in Known issues #3
- [x] Confirmed `_get_local_config` is private to the local fallback (0 callers)

## Implementation

- [x] Create openspec change directory `openspec/changes/croilar-audit-phase-1-delete-dlt-utils-fallback/`
- [x] Write `proposal.md`
- [x] Write `tasks.md`
- [x] Write `specs/croilar-data-engineering/spec.md` delta with 1 ADDED Requirement (no-local-fallback-in-croilar-dlt-utils-destinations)
- [ ] Run `openspec validate croilar-audit-phase-1-delete-dlt-utils-fallback --strict` (must pass before commit)
- [ ] Rewrite `sruth/croilar/dlt_utils/destinations.py` to 13-line canonical-only shim
- [ ] Update `sruth/croilar/dlt_utils/__init__.py` to re-export canonical names (NAMESPACE, get_dlt_destination, create_pipeline, get_duckdb_fallback_destination)
- [ ] Update `sruth/croilar/README.md` "Known issues" row #2 → mark RESOLVED (Round 11 Phase 12)
- [ ] Verify post-state: `from dlt_utils.destinations import NAMESPACE, create_pipeline, get_dlt_destination, get_duckdb_fallback_destination` succeeds
- [ ] Verify post-state: `import dlt_utils; dlt_utils.NAMESPACE == "croilar"` returns True
- [ ] Verify post-state: `import dlt_utils; dlt_utils.get_duckdb_fallback_destination()` returns a dlt duckdb destination
- [ ] Verify post-state: `hasattr(dlt_utils, 'DuckLakeConfig') == False`
- [ ] Verify post-state: `hasattr(dlt_utils, 'get_duckdb_fallback') == False`
- [ ] Run `mise run lint:skills` (123/123 pass)

## Commit + push

- [ ] Stage only files for this phase: 2 modified Python files + 1 README.md update + 3 openspec files
- [ ] **Do NOT stage**: pre-existing in-flight work in `.agents/skills/`, `.infisical.env`, `infrastructure/AGENTS.md`, ROOT `pyproject.toml`, `sruth/oideachais/notebooks/dashboards/education/all_nations.py`, `sruth/oideachais/celtic/duchas.py`, `sruth/oideachais/subjects/subjects/*`, `spaces/data-engineering`, `infrastructure/komodo/*`, `infrastructure/stacks/monitoring/*`, `openspec/changes/add-open{chamber,claw}-*`, `infrastructure/stacks/open{chamber,claw}/`, `infrastructure/stacks/openclaw/`, meaisínfhoghlaim in-flight files
- [ ] Commit 1: `refactor(croilar): round 11 phase 12 (croilar phase 1) — delete local fallback in dlt_utils/destinations.py`
- [ ] Push to `q3-2026-oideachais-consolidation`
- [ ] Run `openspec archive croilar-audit-phase-1-delete-dlt-utils-fallback --yes`
- [ ] Commit 2: `docs(openspec): apply Phase 12 spec delta to croilar-data-engineering`
- [ ] Push to `q3-2026-oideachais-consolidation`
- [ ] Verify `git status` shows "up to date with origin"

## Post-archive

- [ ] Verify `openspec/changes/croilar-audit-phase-1-delete-dlt-utils-fallback/` is now in `archive/` subdirectory
- [ ] Confirm spec delta is now part of `openspec/specs/croilar-data-engineering/spec.md`
- [ ] Confirm 19 changes archived in Round 11 (10 oideachais + 5 meaisinfhoghlaim + 3 tuatha + 1 croilar)