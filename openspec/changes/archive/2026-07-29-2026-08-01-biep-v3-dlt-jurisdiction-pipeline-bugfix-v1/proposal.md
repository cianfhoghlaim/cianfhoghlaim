## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

# 2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1

## Why

The 4 BIEP v3 jurisdiction pipelines (`ireland_jurisdiction_pipeline.py`,
`england_jurisdiction_pipeline.py`, `sct_wls_ni_jurisdiction_pipeline.py`,
`crown_dependencies_jurisdiction_pipeline.py`) all import
`LAKEHOUSE_DUCKDB` from `dlt.common.destinations_cianfhoghlaim`, but that
module does **NOT** export `LAKEHOUSE_DUCKDB`. This causes
`ImportError` at module load and breaks the BIEP v3 stack end-to-end.

Additionally, `dlt/common/destinations_tuatha.py:33` still imports from
the non-existent `destinations_oideachais` module (the post-Phase 0
rename didn't catch this sibling-quadrant shim).

This change is the **A1 blocker** that must land before the rest of
the BIEP v3 wave can deploy.

## What changes

### 1. Add `LAKEHOUSE_DUCKDB` constant to destinations_cianfhoghlaim.py

`dlt/common/destinations_cianfhoghlaim.py` — add a module-level
constant `LAKEHOUSE_DUCKDB = "md:cianfhoghlaim"` next to the existing
`LAKEHOUSE_URI_DEFAULT` (already in `notebooks/_shared/db.py:24`, but
the DLT module didn't carry it).

### 2. Drop the dead `LAKEHOUSE_DUCKDB` imports from the 4 pipelines

- `dlt/british_isles/ireland/education/ireland_jurisdiction_pipeline.py:48`
- `dlt/british_isles/england/education/england_jurisdiction_pipeline.py:40`
- `dlt/british_isles/sct_wls_ni/education/sct_wls_ni_jurisdiction_pipeline.py:38`
- `dlt/british_isles/crown_dependencies/education/crown_dependencies_jurisdiction_pipeline.py:39`

(The `with_namespace` import is also dead — same fix.)

### 3. Fix the tuatha shim import

`dlt/common/destinations_tuatha.py:33` — rename import from
`destinations_oideachais` → `destinations_cianfhoghlaim`.

## Dependencies

```yaml
Blocked by: 2026-07-31-biep-v3-crown-dependencies-v1
Blocked by (soft): 2026-07-26-biep-v3-root-namespace-rename-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `python3 -c "from dlt.british_isles.ireland.education.ireland_jurisdiction_pipeline import ireland_jurisdiction_pipeline; print(ireland_jurisdiction_pipeline())"`
  returns the DLT pipeline object (no `ImportError`)
- Same for `england_jurisdiction_pipeline`, `sct_wls_ni_jurisdiction_pipeline`, `crown_dependencies_jurisdiction_pipeline`
- `python3 -c "from dlt.common.destinations_tuatha import with_namespace; print(with_namespace('oideachais'))"`
  returns a non-`ImportError` result
- `openspec validate 2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1 --strict` passes

## Cross-references

- `dlt/common/destinations_cianfhoghlaim.py` — the canonical destination factory
- `dlt/british_isles/ireland/education/ireland_jurisdiction_pipeline.py` + 3 sibling files
- `dlt/common/destinations_tuatha.py`
- `.agents/skills/dlt/SKILL.md` — the DLT conventions