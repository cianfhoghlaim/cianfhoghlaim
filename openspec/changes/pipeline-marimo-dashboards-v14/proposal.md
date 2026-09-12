## Why

The 4 Marimo v14 dashboard consolidation changes
(`2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1`,
`2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1`,
`2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1`,
`2026-08-10-marimo-v14-cascading-effects-verification-v1`) all touch
the same marimo dashboard surface. Bundling them records that v14
dashboards ship as one milestone (the cascade-effects change
specifically verifies the others), avoiding the trap of
partial-archive states where some dashboards ship and others don't.

## What Changes

- Cross-batch Marimo v14 dashboard contract: the 4 changes ship as
  one milestone with cascading-effects verification last.
- Records the dependency order in `design.md`.

## Capabilities

(none added; pure bundling)

## Impact

- **Affected changes**: 4 bundled
- **Affected code**: none — this change is metadata-only