# 2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify the BIEP v3 batch (Phases 0-5) merged on the current branch
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — Add `LAKEHOUSE_DUCKDB` constant

- [ ] Edit `dlt/common/destinations_cianfhoghlaim.py`
- [ ] Add the module-level constant after `LAKEHOUSE_URI_DEFAULT` (around line 47):
  ```python
  LAKEHOUSE_DUCKDB: str = "md:cianfhoghlaim"
  """The canonical MotherDuck + DuckLake lakehouse alias for the cianfhoghlaim platform."""
  ```

## Stage 2 — Drop the dead imports

- [ ] Edit `dlt/british_isles/ireland/education/ireland_jurisdiction_pipeline.py:48`
  - Remove `LAKEHOUSE_DUCKDB,` and `with_namespace,` from the import line
  - Verify the import shrinks from `from dlt.common.destinations_cianfhoghlaim import (with_namespace, get_dlt_destination, LAKEHOUSE_DUCKDB)` to `from dlt.common.destinations_cianfhoghlaim import get_dlt_destination`
- [ ] Repeat for `dlt/british_isles/england/education/england_jurisdiction_pipeline.py:40`
- [ ] Repeat for `dlt/british_isles/sct_wls_ni/education/sct_wls_ni_jurisdiction_pipeline.py:38`
- [ ] Repeat for `dlt/british_isles/crown_dependencies/education/crown_dependencies_jurisdiction_pipeline.py:39`

## Stage 3 — Fix the tuatha shim

- [ ] Edit `dlt/common/destinations_tuatha.py:33`
- [ ] Rename `from cianfhoghlaim.dlt.destinations_oideachais import with_namespace`
  → `from cianfhoghlaim.dlt.destinations_cianfhoghlaim import with_namespace`
  (drop the extra `h` typo)

## Stage 4 — Validation

- [ ] `python3 -c "from dlt.british_isles.ireland.education.ireland_jurisdiction_pipeline import ireland_jurisdiction_pipeline; print(ireland_jurisdiction_pipeline())"`
  must return the DLT pipeline (no `ImportError`)
- [ ] Same for `england_jurisdiction_pipeline`, `sct_wls_ni_jurisdiction_pipeline`, `crown_dependencies_jurisdiction_pipeline`
- [ ] `python3 -c "from dlt.common.destinations_tuatha import with_namespace; print(with_namespace('oideachais'))"`
  must return a result (no `ImportError`)

## Stage 5 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1/specs/cross-region-pipeline/spec.md`
  with a new `### Requirement: dlt.common.destinations_cianfhoghlaim exports LAKEHOUSE_DUCKDB`
- [ ] Run `openspec validate 2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1 --strict`
- [ ] Commit the change on a dedicated branch
- [ ] Open a PR on `origin/main` referencing this change
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Run `./scripts/sync_agent_docs.sh` per the global agent protocol