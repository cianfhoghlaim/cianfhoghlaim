# 2026-07-25-nb-utils-ibis-first-v1

## Why

The current `notebooks/nb_utils.py` uses raw `duckdb.connect(...)` for all 5
call-sites (lines 48, 118, 150, 158, 170). The ibis-first spec at
`openspec/specs/oideachais-marimo-dashboards/spec.md` mandates
`ibis.duckdb.connect("md:oideachais")` — only 2 of 177 notebooks currently
comply (`data_platform/biep_motherduck/10_leabharlann_descriptive.py` +
`11_dpre_lag_analysis.py`).

Building the shared library + migrating `nb_utils.py` makes every downstream
refactor safe: it gives subagent 4 (notebook flatten) the canonical helper
it imports, and gives subagent 2 (CocoIndex dedup) the per-area `_shared.py`
shims that mirror `marimo_dashboards/_shared.py`.

The pattern is proven by `marimo_dashboards/06_per_subject_analytics.py:84-95`
which already uses `ibis.duckdb.connect("md:oideachais")` successfully.

## What changes

### 1. New `notebooks/_shared/` package

The single canonical connection helper:

- `notebooks/_shared/__init__.py` (NEW) — re-exports `connect_md`
- `notebooks/_shared/db.py` (NEW, ~100 LOC) — defines:
  - `def connect_md(*, read_only: bool = True) -> ibis.duckdb.connect`
  - `def connect_local() -> ibis.duckdb.connect` (for `:memory:` fallback)
  - Internal: `from ibis.duckdb import connect as _ibis_duckdb_connect`

### 2. Refactored `notebooks/nb_utils.py`

- Shrinks from 327 LOC to ≤80 LOC
- Replaces raw `duckdb.connect(...)` with `from _shared.db import connect_md`
- Preserves the existing public API (`connect_biep_lakehouse`,
  `BIEP_SUBJECTS`, `cl_argument_parser`, `run_as_script`) as thin
  re-exports / delegates

### 3. Five per-area `_shared.py` shims

Each re-exports `connect_md` + any area-specific constants:

- `notebooks/leabharlann/_shared.py`
- `notebooks/leaving_cert/_shared.py`
- `notebooks/celtic_language/_shared.py`
- `notebooks/marimo_dashboards/_shared.py`
- `notebooks/mmo/_shared.py`

(These shims already exist in some cases — keep the existing one;
otherwise create. `notebooks/academic_history/_common.py` already
exists and follows this pattern — keep as-is.)

### 4. Spec delta

`openspec/specs/oideachais-marimo-dashboards/spec.md` — add a
`### Requirement: nb_utils.py uses ibis-first connection` requirement
that mandates `ibis.duckdb.connect("md:oideachais")` and points at
the canonical helper at `notebooks/_shared/db.py:connect_md`.

## Dependencies

```yaml
Blocked by: none (root of DAG)
Blocked by (soft): 2026-07-25-cocoindex-per-subject-dedup-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-25-nb-utils-ibis-first-v1 --strict` passes
- `nb_utils.py` ≤ 80 LOC, contains zero raw `duckdb.connect(...)` calls
- `notebooks/_shared/db.py:connect_md()` is the canonical entry point
- The 5 existing ibis-first spec requirements (R1-R9 from `marimo_dashboards/06`)
  remain satisfied
- `mispo run nb-utils:test` (new test) passes for all 6 new modules
- No notebook regressions: every existing notebook that imports
  `nb_utils.connect_biep_lakehouse` continues to work
- Push target: `origin/main`

## Cross-references

- [`oideachais-marimo-dashboards`](../../specs/oideachais-marimo-dashboards/spec.md) —
  the parent marimo dashboard spec that this change conforms to
- `openspec/changes/2026-07-25-cocoindex-per-subject-dedup-v1/` — depends
  on the `_shared/db.py` helper for the per-area shims
- `openspec/changes/2026-07-25-flatten-notebooks-v1/` — depends on
  the `_shared/db.py` helper for the flat-notebook refactor
- `.agents/skills/ibis/SKILL.md` — the ibis-first contract documentation
- `.agents/skills/marimo/SKILL.md` — the marimo conventions