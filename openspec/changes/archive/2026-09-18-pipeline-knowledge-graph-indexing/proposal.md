## Why

The knowledge graph population
(`2026-08-13-knowledge-graph-population-activation-v1`,
`2026-08-10-knowledge-graph-population-v1`) and indexing cognition
cleanup (`2026-08-13-count-drift-rebase-and-indexing-cognition-cleanup-v1`)
changes share the same CCC + Cognee + OpenCode registry surface.
Bundling them records that knowledge-graph activation and the
drift-cleanup belong together — a populated graph with stale counts
is misleading.

## What Changes

- Cross-batch KG + indexing contract: count drift rebase ships
  before KG population to ensure the dashboard counts are honest.
- Records the dependency order in `design.md`.

## Capabilities

(none added; pure bundling)

## Impact

- **Affected changes**: 3 bundled
- **Affected code**: none — this change is metadata-only