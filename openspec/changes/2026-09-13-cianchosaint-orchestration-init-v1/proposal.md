# Change: Mirror cianfhoghlaim 5-layer defs shape to cianchosaint

## Why

Per `cianchosaint-handoff-v1/proposal.md` §4 (drift #2),
`cianchosaint/orchestration/defs/__init__.py` does not exist —
the sister fork only has `licence_enforcement_sensor.py` in
that directory. This means `dg list defs` (Dagster 1.13+)
returns an empty set for cianchosaint, even though the
`licence_enforcement_sensor.py` should be loaded.

Mirroring the cianfhoghlaim 5-layer defs shape
(`1_ingestion/` + `2_materials/` + `3_model_lifecycle/` +
`4_asset_generation/` + `5_agent_ops/` + the missing
`__init__.py`) brings cianchosaint into parity and unlocks
the standard Dagster CLI workflow.

## What changes

- New file: `cianchosaint/orchestration/defs/__init__.py` —
  mirror of the cianfhoghlaim `orchestration/defs/__init__.py`
  pattern (Dagster Definitions loader).
- New directories: `cianchosaint/orchestration/defs/{1_ingestion,2_materials,3_model_lifecycle,4_asset_generation,5_agent_ops}/`
  (empty for now; populated by future sister-specific work).

## Impact

- **Affected code**: `cianchosaint/orchestration/defs/`
- **Affected specs**: `sister-shared` (Shared-4: openspec workflow
  + the orchestration shape)
