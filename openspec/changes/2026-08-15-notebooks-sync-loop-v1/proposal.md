# 2026-08-15-notebooks-sync-loop-v1

## Why

Layer 11 of the 11-layer pull-based sync architecture. Validates
the 119 notebook files at notebooks/.

## What changes

5 sub-layers + 1 orchestrator + 6 artifacts + 1 CCC guide + 1 Cognee
cluster + 1 Dagster asset + 1 notebook + 1 ingestor.

## Acceptance gates

All 3 smoke tests pass + openspec validate --strict.
