# Change: Bootstrap ciandlithe orchestration skeleton

## Why

Per `cianchosaint-handoff-v1/proposal.md` §4 (drift #4),
`ciandlithe/orchestration/`, `ciandlithe/motherduck/`, and
`ciandlithe/notebooks/` are all empty directories. ciandlithe
is the visual/digital-art sister with 7 web apps + a legal
registry — none of which currently feed an orchestration layer.

This change bootstraps the 5-layer defs shape in ciandlithe
so future sister-specific Dagster assets (legal_registry
materialisation, court-record ingestion, etc.) can land
without a separate orchestration-init change.

## What changes

- New file: `ciandlithe/orchestration/defs/__init__.py`
- New directories: `ciandlithe/orchestration/defs/{1_ingestion,2_materials,3_model_lifecycle,4_asset_generation,5_agent_ops}/`
- Mirror of cianfhoghlaim's orchestration scaffold pattern

## Impact

- **Affected code**: `ciandlithe/orchestration/` (new files only)
- **Affected specs**: `sister-shared` (Shared-4 + orchestration parity)
