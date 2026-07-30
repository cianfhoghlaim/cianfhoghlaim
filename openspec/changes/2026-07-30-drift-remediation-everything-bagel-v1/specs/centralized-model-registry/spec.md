# Spec delta: `centralized-model-registry`

This change adds 1 requirement to the existing `centralized-model-registry`
spec: the audit-pattern gate MUST cover `meaisinfhoghlaim/` (the
process + model sub-package that was previously out of scope).

## ADDED Requirements

### Requirement: Audit covers all model-using surfaces

The `mise run lint:registry` task SHALL audit every Python file
under `agents/`, `baml_src/`, `notebooks/`, `web/`, `orchestration/`,
`spaces/`, **and** `meaisinfhoghlaim/`. Any hardcoded model string
in any of these directories (not routed through `MODEL_REGISTRY`)
SHALL fail the gate.

#### Scenario: A hardcoded model is added to meaisinfhoghlaim/process/

- **GIVEN** a developer adds `default_model="gpt-4.5-turbo"` to a
  new function in `meaisinfhoghlaim/process/llm_router.py`
- **WHEN** `mise run lint:registry` runs
- **THEN** the audit MUST detect the new hardcoded string
- **AND** the gate MUST exit 1 with a finding like
  `meaisinfhoghlaim/process/llm_router.py:<line>: 'gpt-4.5-turbo'`

#### Scenario: The audit is run against the post-change state

- **GIVEN** the `drift-remediation` change has migrated the 6
  hardcoded models in `meaisinfhoghlaim/` to `model_for(...)` lookups
- **WHEN** `mise run lint:registry` runs
- **THEN** the audit MUST exit 0 with `Found 0 hardcoded model strings in audited files`
- **AND** the `_AUDIT_DIRS` list in `scripts/registry_audit.py`
  MUST include `meaisinfhoghlaim/`

## Cross-references

- `scripts/registry_audit.py` — the audit-pattern script
- `scripts/lint_drift_docs.py` — the parallel `lint:drift-docs` gate
- `meaisinfhoghlaim/models/model_registry.py` — the canonical registry
- `openspec/changes/2026-07-30-drift-remediation-everything-bagel-v1/specs/drift-remediation/spec.md` —
  the new spec that mandates the audit gap be closed
