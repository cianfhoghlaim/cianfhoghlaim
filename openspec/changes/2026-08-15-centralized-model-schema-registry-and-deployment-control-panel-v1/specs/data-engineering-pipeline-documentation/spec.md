# Spec delta: `data-engineering-pipeline-documentation`

This delta is part of the openspec change
`2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1`.
It updates `STATUS.md` and `REFACTORING.md` with entries for the 3
mega-change artifacts (`centralized-model-registry`,
`centralized-schema-registry`, `deployment-control-panel`).

## ADDED Requirements

### Requirement: STATUS.md + REFACTORING.md entries for the 3 mega-change artifacts

The system SHALL add 3 entries to `STATUS.md` + 3 entries to
`REFACTORING.md` documenting the new artifacts:

1. `centralized-model-registry` — `STATUS.md` entry:
   "70 models registered in `MODEL_REGISTRY` (was 22 OCR/VLM only);
   32 hardcoded `gemini-2.0-flash` sites replaced with
   `MODEL_REGISTRY.resolve(...)`; LiteLLM config regenerated from
   the registry; 96 Pydantic duplicates removed."

2. `centralized-schema-registry` — `STATUS.md` entry:
   "BAML TypeScript codegen activated (`baml_client_ts/`); 96
   hand-written Pydantic duplicates replaced with BAML-generated
   types; bi-ep.gen.ts rewritten from BAML TS (was 671 LOC of
   DuckDB-introspection-derived Zod); `notebooks/_shared/schema.py`
   exposes `schema_introspect()` for every BIEP table."

3. `deployment-control-panel` — `STATUS.md` entry:
   "Marimo notebook `notebooks/00_control_panel.py` + web UI
   `web/apps/cianfhoghlaim-web/control-panel/` + CLI
   `scripts/cianfhoghlaim-cli.ts` + `deployment-choice.yaml` (the
   single enablement file). 5 tabs × 5 routes × 8 subcommands."

#### Scenario: STATUS.md has 3 new entries

- **GIVEN** the 3 mega-change artifacts shipped
- **WHEN** the operator reads `STATUS.md`
- **THEN** the file contains 3 new entries documenting the artifacts