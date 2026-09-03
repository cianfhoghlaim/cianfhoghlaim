# P2-28 — dagster recheck (Phase 2, Drift Re-check)

**Date:** 2026-06-28
**Phase:** 2 (Drift Re-check)
**Budget:** ~60 credits
**Subagent:** data-platform

## TL;DR

This is a **drift re-check** of P1A-02 (Dagster). The purpose is to detect upstream breaking changes between the original P1A-02 research (2026-06-28) and the Phase 4 OpenSpec closure (~30 days later).

## Drift detected

| Component | P1A-02 baseline | Re-check 2026-07-28 | Action |
|:--|:--|:--|:--|
| Dagster version | 1.13.x | (pending Phase 4) | Run `pip show dagster` |
| dagster-dlt | 0.25.x | (pending) | Check compatibility |
| `@dlt_assets` API | stable | (pending) | None expected |
| `MultiPartitionsDefinition` | stable | (pending) | None expected |
| `@asset_check` | stable | (pending) | None expected |

## Check procedure

```bash
# Run in the worker's Python environment
python3 -c "
import dagster
print(f'Dagster version: {dagster.__version__}')
import dagster_dlt
print(f'dagster-dlt version: {dagster_dlt.__version__}')
"

# Check if any @dlt_assets patterns are deprecated
python3 -c "
from dagster_dlt import dlt_assets
print(dlt_assets.__doc__)
"

# Verify the asset check API hasn't changed
python3 -c "
from dagster import asset_check, AssetCheckResult, MetadataValue
print('All asset check imports OK')
"

# Check if MultiPartitionsDefinition still works as expected
python3 -c "
from dagster import MultiPartitionsDefinition, StaticPartitionsDefinition
p = MultiPartitionsDefinition({
    'subject': StaticPartitionsDefinition(['math', 'irish', 'english']),
    'material_type': StaticPartitionsDefinition(['exam_paper', 'marking_scheme']),
})
print(f'MultiPartitionsDefinition created: {len(p.get_partitions())} partitions')
"
```

## Expected outcome (if no drift)

All imports work; Dagster version is in the 1.13.x → 1.14.x range; no breaking API changes.

## Expected outcome (if drift detected)

If any check fails:
1. Document the API change in P2-28 / P1A-02 (whichever is more recent)
2. Add a `## Drift log` entry to P1A-02 with the new version
3. File an OpenSpec change to update the canonical Dagster skill + SPEC

## Files

- `oideachais/dagster_defs/definitions.py` (entry point)
- `docs/skills/dagster/SKILL.md` (canonical skill)
- `openspec/specs/oideachais-pipeline/spec.md` (cross-cutting Dagster requirement)

## Status

DEFERRED — runs in Phase 4 (30 days from now). For now, no action needed.
