# Change: Fix 3 broken `import dlt_sources` regressions in cianfhoghlaim

## Why

Per `cianchosaint-handoff-v1/proposal.md` §4 (drift #3), 3
files under `orchestration/defs/` still import the OLD pre-v7
`dlt_sources` module path instead of `dlt`:

```
orchestration/defs/2_materials/eu_multilingual/english_coverage_monitor.py
orchestration/defs/2_materials/eu_multilingual/irish_coverage_monitor.py
orchestration/defs/2_materials/eu_multilingual/language_alignment_mapper.py
```

These were supposed to be fixed by
`2026-08-24-wave-1-dlt-sources-domain-restructure-v1` but the
trust-gap memory `kcg-fabricated-openspec-archive-biep-v3`
claims the wave did not fully land. Verification confirms:
the 3 broken files still exist with `import dlt_sources`.

Fixing this is a 3-line patch per file (1 import statement).

## What changes

- `orchestration/defs/2_materials/eu_multilingual/english_coverage_monitor.py`: replace `import dlt_sources` with the correct dlt path
- Same for `irish_coverage_monitor.py`
- Same for `language_alignment_mapper.py`

## Impact

- **Affected code**: 3 lines across 3 files
- **Affected specs**: `orchestration-architecture` (Dagster 5-layer + the import convention)
