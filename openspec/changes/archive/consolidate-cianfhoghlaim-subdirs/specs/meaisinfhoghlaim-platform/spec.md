## MODIFIED Requirements

### Requirement: Dagster asset grouping by domain

The system SHALL organise dagster assets in `cianfhoghlaim/dagster/assets/`
by domain. The legacy `law/{nation}/` and `medicine/{nation}/`
single-asset directories SHALL be replaced by
`by_domain/{law,medicine}.py` files containing the consolidated
nation-specific assets.

The 9 British Isles nations SHALL each have 1 law asset
(`{nation}_legislation`) and 1 medicine asset (per the source
function exposed by the dlt domain). The 7 non-IE nations SHALL
have these assets wired to the canonical
`dlt/domains/{nation}/{domain}/{source}.py` paths (per the
`oideachais-pipeline` spec).

#### Scenario: A developer adds a new nation's law asset

- **WHEN** a new nation (e.g. `ci` for Channel Islands) is added to
  the British Isles coverage
- **THEN** the developer adds a new `{nation}_legislation` `@asset`
  to `dagster/assets/by_domain/law.py`
- **AND** wires it to the corresponding
  `dlt/domains/ci/law/legislation.py` source
- **AND** the asset appears in the `by_domain.law` group in the
  Dagster UI