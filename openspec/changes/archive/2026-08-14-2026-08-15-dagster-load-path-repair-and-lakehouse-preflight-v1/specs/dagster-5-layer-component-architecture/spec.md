## ADDED Requirements

### Requirement: Component YAML mount convention

The system MUST enforce that every directory in `orchestration/defs/`
that contains Component YAML children has an explicit mount point. The
mount point is EITHER:

1. A bare `defs.yaml` at the directory root (the directory IS a Component, via `dg.Component` + `build_defs()`), OR
2. An `_layer/defs.yaml` inside the directory (using `type: dagster.DefsFolderComponent` with `attributes: {}` to mount the children recursively)

A directory that has Component YAML children but NEITHER mount point
is silently unreachable by `dg.load_defs()` — the assets are dead code.

The system MUST additionally enforce that every loadable Component YAML
is named exactly `defs.yaml` (Dagster 1.13+ only walks files with that
magic filename; `mything.yaml` is silently skipped).

Per the 2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1
change: this invariant is enforced by the existing
`scripts/audit_defs_yaml.py` (CI gate) + the new
`scripts/dagster_load_smoke.py` companion.

#### Scenario: A new subdirectory with Component YAML children has a mount point

- **GIVEN** a developer adds `orchestration/defs/2_materials/foo/bar/defs.yaml`
- **WHEN** they run `dg check yaml`
- **THEN** Dagster reports the addition as a loadable Component
- **AND** `dg list defs` includes `2_materials/foo/bar`

#### Scenario: A directory missing the mount point is unreachable

- **WHEN** `python3 scripts/dagster_load_smoke.py` runs
- **THEN** it reports any directory with `defs.yaml` children but no mount point
- **AND** it exits 1 if any such directory is found

#### Scenario: A YAML file not named `defs.yaml` is unreachable

- **WHEN** `python3 scripts/dagster_load_smoke.py` runs
- **THEN** it reports any `*.yaml` file under `orchestration/defs/` whose name is not `defs.yaml` (and not `.planned`)
- **AND** it exits 1 if any such file is found

### Requirement: L3 cognify + federated_ocr assets default to manual automation

The system MUST emit the 3 L3 components that wrap the cognify +
federated_ocr stack (`KCGCognifyComponent`,
`CognifyIngestSensorsComponent`, `CelticFederatedOcrComponent`) with
the default `automation_condition: Manual()` -- i.e. they MUST NOT
trigger on cron or on upstream freshness signals. Operators launch
them by hand once the cognify stack (cognee + graphiti + falkordb +
lancedb + memgraph) is brought up.

The fail-loudly contract documented in `kcg_cognify_component.py` is
preserved: when the assets ARE materialised manually and the cognify
stack is not up, they raise informative errors.

#### Scenario: The L3 cognify assets are not auto-triggered in BIEP M1-M4

- **WHEN** `mise run biep:v3:m1` runs
- **THEN** the 3 cognify + federated_ocr assets are NOT in the materialisation set
- **AND** the asset graph shows them as "manual-only" badges
- **AND** the BIEP milestone exits 0 (no fail-loudly raise)

#### Scenario: An operator can manually materialise the L3 cognify assets

- **GIVEN** the cognify stack is up (cognee + graphiti + falkordb + lancedb + memgraph)
- **WHEN** the operator clicks "Materialize" on a `3_model_lifecycle/cognify/*` asset in the Dagster UI
- **THEN** the asset materialises successfully
- **OR** fails informatively with the fail-loudly contract error