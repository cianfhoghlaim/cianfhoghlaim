## Why

`spaces/data-engineering/` is the only non-Gradio HuggingFace
Space. It runs a Dagster + dbt + Evidence dashboard that queries
the public PyPI Packages dataset on Google BigQuery.

The Space is **functional but disconnected from the KCG
monorepo**:

- Uses BigQuery as a source (not the KCG pattern of
  `stedding/ingest_queue/`)
- Uses local DuckDB (not MotherDuck)
- Has its own dbt project name `pypi_analytics` (orthogonal
  to sruth/oideachais/sruth/croilar/tuatha)
- No 2026-06 features (no LanceDB, no CocoIndex, no Cognee,
  no Graphiti, no BAML extraction)
- Has no openspec spec governing it (no `data-engineering-space`
  capability)
- Has its own .git/ (a standalone repo, not a submodule)

This change adds a new `data-engineering-space` capability
spec to the `infrastructure-stacks` umbrella. The spec
captures the 4 key rules:

1. The Space MUST use `stedding/ingest_queue/pypi/` as the
   source (the KCG pattern), not BigQuery
2. The Space MUST use MotherDuck as the destination (not local
   DuckDB), via the canonical `motherduck-data-modeling` skill
3. The Space MUST use dbt-duckdb (not raw dbt)
4. The Space MUST add Cognee + Graphiti for the curriculum KG
   (the canonical knowledge-graph stack)

The actual modernization (replacing the BigQuery source +
local DuckDB) is captured in the `modernize-data-engineering-space`
openspec change (E2).

## What changes

- New `openspec/specs/data-engineering-space/spec.md`
- 1 ADDED Requirement to the `infrastructure-stacks` spec
  (the data-engineering-space pointer)

## Out of scope

- The actual modernization (E2) — separate change
- The data-engineering README (it stays as-is until E2)
