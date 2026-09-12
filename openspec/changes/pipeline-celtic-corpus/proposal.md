## Why

The 3 Celtic-language corpus changes
(`2026-09-15-celtic-language-corpus-extension-v1`,
`2026-09-08-ogham-celtic-stones-pipeline-v1`,
`2026-09-01-celtic-mythology-content-system-v1`) cover the same
Celtic-language data surface (Welsh / Irish / Scottish Gaelic /
Breton / Cornish / Manx) across 3 different sources (modern
corpus, Ogham stones, mythology). Bundling them records that the
Celtic corpus ships as one milestone.

## What Changes

- Cross-batch Celtic corpus contract: the 3 corpus surfaces ship as
  one milestone with a shared canonical embedder (BGE-M3 1024-d
  per the centralized model registry).
- Records the dependency order in `design.md`.

## Capabilities

(none added; pure bundling)

## Impact

- **Affected changes**: 3 bundled
- **Affected code**: none — this change is metadata-only