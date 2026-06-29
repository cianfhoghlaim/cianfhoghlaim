# Delta: croilar-portfolio

## ADDED Requirements

### Requirement: croilar Python asset module

The `croilar` asset group SHALL be declared as a Python asset module at
`cianfhoghlaim/assets/_oideachais_dagster_defs/defs/croilar/assets.py`,
mounted via a `defs.yaml` at the same directory.

The module SHALL export exactly 4 assets, one per Croilar portfolio
function: croilar_cv_extraction, croilar_data_engineering,
croilar_portfolio, croilar_devtools_hub.

All 4 assets SHALL be tagged with `group_name: croilar`.

#### Scenario: a Dagster user runs the Croilar pipeline

- **GIVEN** the Croilar code-location is registered with the Dagster UI
- **WHEN** the user materialises the `croilar` group
- **THEN** all 4 Croilar portfolio functions materialise
