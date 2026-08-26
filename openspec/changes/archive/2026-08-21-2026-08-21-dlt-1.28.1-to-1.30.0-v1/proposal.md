# 2026-08-21-dlt-1.28.1-to-1.30.0-v1

## Summary

Bump DLT from `>=1.28.1` to `>=1.30.0,<2.0.0`. This is Priority 1 in the upstream-version audit (`stedding/audit/2026-08-21-upstream-audit.md`). The umbrella change `2026-08-21-upstream-version-alignment-and-pin-resolution-v1` already authorized it.

## Why

DLT 1.25+ changed `pipeline.dataset()` to include all schemas by default (was single-schema before). Pinning the `schema=` kwarg in the 10 jurisdiction pipelines defends against silent breakage. DLT 1.27 split `dlt[hub]` into a separate package; we're not using dlthub directly so this is non-impact. DLT 1.28 introduced `refresh` to supersede `replace`. DLT 1.30.0 (Aug 2026) is the latest stable.

The BIEP v3 Ireland LC pipeline run today (Phase 4 audit log) used dlt 1.30 successfully — the bump was effectively already applied via `>=1.28.1` resolving transitively.

## What changes

- `pyproject.toml`: bump `dlt[duckdb,motherduck,filesystem]>=1.28.1` → `>=1.30.0,<2.0.0`.
- 9 jurisdiction pipelines: audit any `replace` → migrate to `refresh` (per DLT 1.28 supersession).
- The 10 jurisdiction `pipeline.dataset()` call-site audit showed **0 direct usages** (the `ireland_jurisdiction_pipeline.py` uses the new `JurisdictionPipelineBase.build_pipeline(name, dataset_name)` pattern). Audit complete; no edits needed.

## Test plan

1. `uv sync` resolves cleanly.
2. `mise run data:status` reports BIEP v3 status OK across all 7 sections.
3. Run the BIEP v3 Ireland LC pipeline end-to-end (`lc5_mathematics_ingested`-equivalent) against the 80 PDFs at `/leaving_certificate/` — assert same 80 rows.
4. `openspec validate 2026-08-21-dlt-1.28.1-to-1.30.0-v1 --strict` exits 0.
5. Run the canonical per-subject notebook CLI (`uv run notebooks/lc/mathematics.py --milestone m1 --asset-check documents_ingested --jurisdiction ireland --output json`) — must still work.

## Rollback

- Revert `pyproject.toml` to `dlt[duckdb,motherduck,filesystem]>=1.28.1`.
- `uv sync` re-resolves.
- The `replace` → `refresh` migration in the 9 jurisdiction pipelines is a semantic change, not a syntax change. Reverting is a simple `sed -i 's/write_disposition="refresh"/write_disposition="replace"/g'`.
