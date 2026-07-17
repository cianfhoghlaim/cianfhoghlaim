## ADDED Requirements

### Requirement: Canonical cross-region path contract for the oideachais pipeline

The cianfhoghlaim-pipeline capability MUST route every new DLT source
through the canonical cross-region path contract declared by the
[`cross-region-pipeline`](../../../specs/cross-region-pipeline/spec.md)
umbrella spec.

The existing British Isles files (`dlt/british_isles/<nation>/<domain>/<source>.py`)
are forward-compatible — they were the seed of the contract — and are
NOT renamed. The new regions (`european_union`, `european_nations`,
`commonwealth`, `americas`, `global_official`) MUST obey the contract
on every new file.

#### Scenario: A new file in the EU nations expansion obeys the contract

- **WHEN** a developer adds a new French statute-book DLT source
- **THEN** it MUST be created at
  `dlt/european_nations/fra/law/legifrance.py`
- **AND** it MUST NOT be created at any of the legacy paths
  (`dlt/eu/`, `dlt/european_union/fra/`,
   `dlt/british_isles/fra/`, etc.)
