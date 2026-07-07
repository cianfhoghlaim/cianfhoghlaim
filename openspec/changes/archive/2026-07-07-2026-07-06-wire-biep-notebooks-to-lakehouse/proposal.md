# Change: 2026-07-06-wire-biep-notebooks-to-lakehouse

## Why

After Changes 1 + 2 bring up the Infisical-managed data plane
(Infisical + lakehouse + mlflow + litellm + unstract), the 6 BIEP
marimo notebooks (Mathematics, Chemistry, Geography, Gaeilge, English,
Computer Science) under `british-isles-education-pipeline-v1` AND the
canonical `bonneagar/stacks/lakehouse/notebooks/lakehouse_pipeline.py`
SHALL run against the live local data plane — not against a `*.duckdb`
file on disk.

This change implements the Cross-Sruth Lakehouse Wiring Contract from
`openspec/specs/infrastructure-stacks/spec.md` (the `ducklake_{namespace}`
DB + LANCEDB_URI = rest://lakehouse-lance-namespace:8182).

Per user decision 2026-07-06: **all 7 notebooks must prioritise DuckDB
through ibis** — the canonical KCG entrypoint per
`.agents/skills/ibis/SKILL.md` is `ibis.duckdb.connect(uri)`. Raw
`duckdb.connect(uri)` calls are forbidden.

## What changes

- **7 marimo notebooks rewritten to use ibis end-to-end** (1 x
  `bonneagar/stacks/lakehouse/notebooks/lakehouse_pipeline.py` + 6 x
  BIEP subjects under `cianfhoghlaim/notebooks/biep/`):
  every existing raw `duckdb.connect(...)` and `lancedb.connect(...)` call
  switches to `ibis.duckdb.connect(...)` and `ibis.lancedb.connect(...)`.
  Cloud-remote path uses `ibis.duckdb.connect("md:oideachais")`;
  local-dev path uses
  `ibis.duckdb.connect("ducklake:postgres:host=lakehouse-postgres …")`.
- 1 new runbook section "Phase 4 — Run the BIEP notebooks" appended to
  `bonneagar/deploy-runbooks/bunchloch-infisical-data-plane-2026-07.md`
- 1 new ops script `opencode/scripts/run-biep-notebooks.sh` that runs
  each marimo notebook and captures outputs to
  `.scratch/biep-2026-07/<subject>.log`

## Impact

- **Affected specs:** `oideachais-marimo-dashboards` +
  `british-isles-education-pipeline`
- **Affected hosts:** `bunchloch` only
- **Risk:** low (notebook-only change, no infrastructure mutations)
- **Disk:** negligible (notebook outputs are ~10 KB each)
- **RAM:** per-notebook peak ~1 GB (marimo browser tab + server)
- **Audit gates:** `openspec validate <id> --strict` + manual smoke
  that the notebook's output table reads 0 rows before any DLT data
  has been ingested (expected)

## Non-goals

- Not implementing the actual BAML extraction pipeline (the BIEP change
  `2026-07-06-british-isles-education-pipeline-v1` is the owner of that
  — verify it's archived before running the extraction-step of the
  notebooks)
- Not converting the 6 marimo notebooks from marimo 0.23.13 to a
  newer version (the existing pins work; `__generated_with` is
  metadata only)
- Not adding MotherDuck as a remote-write target (it's already
  available; this change just configures the local-mode default)

## Spec delta

See `specs/oideachais-marimo-dashboards/spec.md` for the ADDED
Requirement governing the 7 notebooks' ibis-first contract. See
`specs/british-isles-education-pipeline/spec.md` for the MODIFIED
Requirement governing the per-subject DuckDB-through-ibis wiring.