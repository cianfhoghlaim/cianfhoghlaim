## ADDED Requirements

### Requirement: ciandlithe MUST carry the 5-layer defs scaffold

The ciandlithe repo SHALL carry the same 5-layer Dagster defs
shape as cianfhoghlaim + cianchosaint: `1_ingestion/` +
`2_materials/` + `3_model_lifecycle/` + `4_asset_generation/` +
`5_agent_ops/` plus the missing `__init__.py` in each.

#### Scenario: dg list defs does not error

- **WHEN** an operator runs `cd /Users/cianmacandeisigh/dev/ciandlithe && dg list defs --module orchestration.defs`
- **THEN** the output MUST NOT be a ModuleNotFoundError
- **AND** MUST report zero assets (scaffold only — future sister-specific work fills it)
