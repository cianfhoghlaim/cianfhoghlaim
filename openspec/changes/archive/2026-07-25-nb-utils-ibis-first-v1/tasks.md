# 2026-07-25-nb-utils-ibis-first-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify the BIEP v2 stack merged on `feat/iac-ify-arm1-oci-control-plane`
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`
- [ ] Read the existing `marimo_dashboards/06_per_subject_analytics.py:84-95`
  ibis-first pattern

## Stage 1 — Create the `_shared/db.py` helper

- [ ] Create `notebooks/_shared/__init__.py` (re-export)
- [ ] Create `notebooks/_shared/db.py` with the canonical `connect_md()` + `connect_local()`
- [ ] Verify: `uv run python -c "from notebooks._shared.db import connect_md; c = connect_md(); print(c)"`
  works and returns an `ibis.duckdb.connect` handle (not raw `duckdb`)

## Stage 2 — Refactor `notebooks/nb_utils.py`

- [ ] Read the current `notebooks/nb_utils.py` (327 LOC)
- [ ] Identify the 5 raw `duckdb.connect(...)` call-sites
- [ ] Replace each with `connect_md()` from `_shared/db`
- [ ] Shrink the file to ≤80 LOC while preserving the public API
  (`connect_biep_lakehouse`, `BIEP_SUBJECTS`, `cl_argument_parser`, `run_as_script`)
- [ ] Run `uv run python -c "import notebooks.nb_utils as u; print(u.BIEP_SUBJECTS)"`
  to verify the public API still works

## Stage 3 — Create per-area shims

- [ ] `notebooks/leabharlann/_shared.py` — re-export `connect_md`
- [ ] `notebooks/leaving_cert/_shared.py` — re-export `connect_md`
- [ ] `notebooks/celtic_language/_shared.py` — re-export `connect_md`
- [ ] `notebooks/marimo_dashboards/_shared.py` — already exists; verify it
  re-exports `connect_md` (if not, add the re-export)
- [ ] `notebooks/mmo/_shared.py` — re-export `connect_md`
- [ ] (Skip `notebooks/academic_history/_common.py` — already exists, keep as-is)

## Stage 4 — Add `## KCG patterns used` docstring block

- [ ] Add the block to `notebooks/_shared/db.py`
- [ ] Add the block to `notebooks/nb_utils.py` (top of file)
- [ ] Add the block to each of the 5 per-area shims

## Stage 5 — Tests

- [ ] Create `notebooks/_shared/test_db.py` with the unit test:
  - `test_connect_md_returns_ibis_duckdb`
  - `test_connect_local_uses_memory`
- [ ] Run `uv run pytest notebooks/_shared/test_db.py` — must pass
- [ ] Run the existing 2 ibis-first notebooks (`10_leabharlann_descriptive.py`,
  `11_dpre_lag_analysis.py`) to verify no regression

## Stage 6 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-07-25-nb-utils-ibis-first-v1/specs/oideachais-marimo-dashboards/spec.md`
  with the new `### Requirement: nb_utils.py uses ibis-first connection`
- [ ] Run `openspec validate 2026-07-25-nb-utils-ibis-first-v1 --strict`
- [ ] Commit the change on a dedicated branch `openspec/2026-07-25-nb-utils-ibis-first-v1`
- [ ] Open a PR on `origin/main` referencing this change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-07-25-nb-utils-ibis-first-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Update `docs/notebooks/ibis-first-migration.md` with the migration notes
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol