# Delta: oideachais-cognify-knowledge-graph

## ADDED Requirements

### Requirement: cognify Python asset module

The `cognify` asset group SHALL be declared as a Python asset module at
`cianfhoghlaim/assets/_oideachais_dagster_defs/defs/cognify/assets.py`,
mounted via a `defs.yaml` at the same directory.

The module SHALL export exactly 10 assets, one per cognify function:
- 7 cognee_integration functions (author_archive, cross_stage, culture,
  leabharlann, leabharlann_inbox, official_media, site_analysis)
- 3 cross-archive rules (author_archive_cross_corpus,
  leabharlann_cross_archive, leabharlann_inbox_cross_archive)

All 10 assets SHALL be tagged with `group_name: cognify` and
`compute_kind: cognee`.

#### Scenario: a Dagster user runs the cognify pipeline

- **GIVEN** the `dagster dev` webserver is running on port 3335
- **WHEN** the user materialises the `cognify` group
- **THEN** all 10 cognify functions materialise (each one calls the
  underlying Cognee + cross-archive edge function)
