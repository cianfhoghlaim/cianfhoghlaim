# Delta: tuatha-platform

## ADDED Requirements

### Requirement: tuatha Python asset module

The `tuatha` asset group SHALL be declared as a Python asset module at
`cianfhoghlaim/assets/_oideachais_dagster_defs/defs/tuatha/assets.py`,
mounted via a `defs.yaml` at the same directory.

The module SHALL export exactly 6 assets, one per Tuatha game-state
function: mythology_cognify, celtic_tutor_agent, crypteolas_defi,
tuatha_mmo_state, tuatha_embedding, tuatha_audio.

All 6 assets SHALL be tagged with `group_name: tuatha`.

#### Scenario: a Dagster user runs the Tuatha pipeline

- **GIVEN** the Tuatha code-location is registered with the Dagster UI
- **WHEN** the user materialises the `tuatha` group
- **THEN** all 6 Tuatha game-state functions materialise
