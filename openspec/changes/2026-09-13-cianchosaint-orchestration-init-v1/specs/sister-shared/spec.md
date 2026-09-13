## ADDED Requirements

### Requirement: cianchosaint MUST mirror cianfhoghlaim 5-layer defs shape

The cianchosaint repo SHALL carry the same 5-layer Dagster defs
shape as cianfhoghlaim: `1_ingestion/` + `2_materials/` +
`3_model_lifecycle/` + `4_asset_generation/` + `5_agent_ops/`
plus the missing `__init__.py` in each.

#### Scenario: dg list defs returns the cianchosaint assets

- **WHEN** an operator runs `cd /Users/cianmacandeisigh/dev/cianchosaint && dg list defs --module orchestration.defs`
- **THEN** the output MUST include `licence_enforcement_sensor`
- **AND** MUST NOT report `Module orchestration.defs has no assets defined`
