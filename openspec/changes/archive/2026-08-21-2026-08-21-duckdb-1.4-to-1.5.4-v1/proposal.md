# 2026-08-21-duckdb-1.4-to-1.5.4-v1

## Summary

Bump DuckDB from 1.4.x → 1.5.4 (the highest MotherDuck-supported line; skip 1.5.5 until MD catches up). This is Priority 1 in the upstream-version audit. The umbrella change `2026-08-21-upstream-version-alignment-and-pin-resolution-v1` already authorized it.

## Why

- DuckDB 1.5.0 "Variegata" release brings `VARIANT` type + `GEOMETRY` type + bloom-filter join pushdown + stats-only min/max + faster TopN with late materialization + lazy view binding.
- DuckDB 2.0 ships **September 2026**. Bumping to 1.5.4 buys time and avoids a 1.4 → 2.0 upgrade in one go.
- MotherDuck supports 1.5.4 (per the audited release notes) but NOT 1.5.5 yet — staying on 1.5.4 is MD-safe.

## What changes

- `pyproject.toml`: `duckdb>=1.4` → `duckdb>=1.5.4,<1.5.5`.
- `bonneagar/stacks/lakehouse/compose.yaml`: image tag `duckdb/duckdb:1.4.x` → `duckdb/duckdb:1.5.4` (if any DuckDB-only container).
- Re-test the 24 BIEP tables + `gov_circulars_archive` against `VARIANT` rejection (MotherDuck doesn't have `VARIANT` yet — any usage in the schema will fail).

## Test plan

1. `uv sync` resolves cleanly.
2. `uv pip show duckdb` prints `1.5.4`.
3. The BIEP v3 Ireland LC pipeline (now on DLT 1.30) still produces 80 rows.
4. The local DuckDB engine that the dagster `orchestration/defs/` uses for SQLite-backed assets accepts the 1.5.4 binary.
5. `openspec validate 2026-08-21-duckdb-1.4-to-1.5.4-v1 --strict` exits 0.

## Rollback

- Revert `pyproject.toml` pin to `duckdb>=1.4`.
- `uv sync` re-resolves.
- The local DuckDB uses separate file paths (`:memory:` for notebooks, `/tmp/lc5*.duckdb` for tests); no migration needed.
