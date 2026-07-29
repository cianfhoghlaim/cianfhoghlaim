# Spec delta: `cianfhoghlaim-baml-schemas`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It activates BAML TypeScript codegen (`baml_client_ts/`) and removes
the 96 hand-written Pydantic duplicates in
`dlt_sources/.../subjects/<subject>/schema.py`.

## ADDED Requirements

### Requirement: BAML TypeScript codegen is activated

The system SHALL run BAML TypeScript codegen on every
`mise run baml:generate`, populating `baml_client_ts/` at the repo
root. The TypeScript codegen output SHALL be consumed by web apps via
`import { z } from "@baml/..."` (or path-relative).

#### Scenario: baml_client_ts/ is populated on mise run baml:generate

- **GIVEN** `baml_src/baml.toml` declares
  `[generators.lang_ts] output_type = "typescript" output_dir = "../baml_client_ts"`
- **WHEN** the operator runs `mise run baml:generate`
- **THEN** `baml_client_ts/` is populated with `index.ts`, `types.ts`,
  `async_client.ts` (~3 MB total)
- **AND** `baml_client/` is also populated (Python Pydantic)

### Requirement: 96 hand-written Pydantic duplicates are removed

The system SHALL replace the 8
`dlt_sources/.../subjects/<subject>/schema.py` files with
`from cianfhoghlaim.baml_client.types import ...` imports. The 96
hand-written Pydantic classes (8 subjects × 12 classes) SHALL be
removed.

#### Scenario: schema.py files are replaced with BAML imports

- **GIVEN** the 8
  `dlt_sources/.../subjects/<subject>/schema.py` files
- **WHEN** the operator reads any of the 8 files
- **THEN** the file is either deleted OR contains only re-export
  statements (`from cianfhoghlaim.baml_client.types import ...`)
- **AND** the file does NOT contain any `class X(BaseModel):`
  declarations for the 12 mirrored BAML classes