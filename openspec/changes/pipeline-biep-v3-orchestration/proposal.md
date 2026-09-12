## Why

The 3 BIEP v3 orchestration changes
(`2026-08-13-biep-v3-orchestration-activation-v1`,
`2026-08-13-biep-v3-jurisdiction-sensor-jobs-v1`,
`2026-08-10-england-biiep-pipeline-v1`) are sequenced and
interdependent: the jurisdiction-sensor jobs depend on the
orchestration activation, which depends on the England BIEP
ingestion landing rows. Bundling them under one topic-batch change
records that dependency and gives the milestone a single archive
target. Each individual change keeps its own spec deltas; this
change adds the cross-batch orchestration contract.

## What Changes

- Adds the cross-batch BIEP v3 orchestration contract: the
  orchestration activation, jurisdiction sensor jobs, and England
  BIEP ingestion SHALL ship as one milestone (none archive
  independently).
- Records the dependency graph in this change's `design.md` so
  future agents can resume execution against the explicit ordering.
- Does NOT modify any of the 3 bundled changes' proposals or tasks —
  each remains a self-contained unit.

## Capabilities

### New Capabilities
(none — pure bundling/tracking change)

### Modified Capabilities
(none)

## Impact

- **Affected changes**: 3 bundled
- **Affected code**: none — this change is metadata-only