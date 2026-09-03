# deployment-control-panel Specification

## Purpose
TBD - created by archiving change 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1. Update Purpose after archive.
## Requirements
### Requirement: One marimo control-panel notebook with 5 tabs

The system SHALL provide a marimo notebook at
`notebooks/00_control_panel.py` with 5 tabs:

1. **Tab 1: Models** — `mo.ui.multiselect` listing every
   `MODEL_REGISTRY` entry by family. Toggle on/off. Writes the
   choice to `deployment-choice.yaml`.
2. **Tab 2: Pipelines** — `mo.ui.multiselect` listing every DLT
   source + every CocoIndex App. Toggle on/off.
3. **Tab 3: Datasets** — `mo.ui.table` showing every BIEP DuckDB
   table + column count + LanceDB table mount + row count. Read-only.
4. **Tab 4: Stacks** — `mo.ui.multiselect` listing every Docker
   Compose stack in `bonneagar/stacks/`. Toggle on/off.
5. **Tab 5: Registry** — `mo.ui.table` showing the full
   `MODEL_REGISTRY` view + drift warnings.

#### Scenario: Notebook runs end-to-end with all 5 tabs

- **GIVEN** the `MODEL_REGISTRY` populated + the BIEP lakehouse
  reachable + `deployment-choice.yaml` writable
- **WHEN** the operator runs
  `marimo edit notebooks/00_control_panel.py`
- **THEN** all 5 tabs load without error
- **AND** Tab 1 lists every MODEL_REGISTRY entry grouped by family
- **AND** Tab 2 lists every DLT source + CocoIndex App
- **AND** Tab 3 shows the BIEP DuckDB tables + LanceDB mounts
- **AND** Tab 4 lists every Docker Compose stack
- **AND** Tab 5 shows the full MODEL_REGISTRY view + drift count

#### Scenario: Toggling an entry writes deployment-choice.yaml

- **GIVEN** the notebook open with Tab 1 "Models" visible
- **WHEN** the operator toggles off `qwen3-vl-8b` and clicks "Save"
- **THEN** `deployment-choice.yaml` is updated with
  `enabled_models: [..., qwen3-vl-8b: false, ...]`
- **AND** the file write is atomic (via `fcntl.flock`)

#### Scenario: Notebook reads deployment-choice.yaml on startup

- **GIVEN** `deployment-choice.yaml` exists with
  `enabled_models: {qwen3-vl-8b: false, ...}`
- **WHEN** the operator opens the notebook
- **THEN** Tab 1 shows `qwen3-vl-8b` pre-toggled OFF
- **AND** the other entries are pre-toggled ON per the YAML

### Requirement: One web UI control panel with 5 TanStack Start routes

The system SHALL provide a TanStack Start app at
`web/apps/cianfhoghlaim-web/control-panel/` with 5 routes:

1. `/control-panel/models` reading `MODEL_REGISTRY` via Hono API
2. `/control-panel/pipelines` reading `list_dlt_sources()` +
   `list_cocoindex_apps()` via Hono
3. `/control-panel/datasets` reading `schema_introspect()` via Hono
4. `/control-panel/stacks` reading the stack list via Hono
5. `/control-panel/registry` showing `MODEL_REGISTRY` + drift warnings

Plus an oRPC mutation `/api/deployment-choice` that writes
`deployment-choice.yaml` after a toggle.

#### Scenario: Web UI boots with all 5 routes

- **GIVEN** `web/apps/cianfhoghlaim-web/` configured with the
  control-panel routes
- **WHEN** the operator runs `bun run dev` and navigates to
  `http://localhost:3000/control-panel`
- **THEN** all 5 routes render without error
- **AND** `/control-panel/models` lists every MODEL_REGISTRY entry
- **AND** `/control-panel/registry` shows the drift count from
  `mise run lint:registry`

#### Scenario: Web UI toggle writes deployment-choice.yaml

- **GIVEN** the web UI at `/control-panel/models` with
  `qwen3-vl-8b` currently enabled
- **WHEN** the operator toggles `qwen3-vl-8b` OFF and clicks "Save"
- **THEN** the oRPC mutation `/api/deployment-choice` writes
  `deployment-choice.yaml` with `enabled_models: {qwen3-vl-8b: false}`
- **AND** the marimo notebook re-reads the YAML on next open and
  shows `qwen3-vl-8b` pre-toggled OFF

### Requirement: One CLI extending scripts/cianfhoghlaim-cli.ts

The system SHALL extend `scripts/cianfhoghlaim-cli.ts` with the
following subcommands:

- `models list` — prints `MODEL_REGISTRY` entries (human + JSON)
- `models enable <key>` / `models disable <key>` — writes
  `deployment-choice.yaml`
- `pipelines list` — prints every DLT source + CocoIndex App
- `pipelines enable <id>` / `pipelines disable <id>` — writes
  `deployment-choice.yaml`
- `stacks list` — prints every Docker Compose stack
- `stacks enable <name>` / `stacks disable <name>` — writes
  `deployment-choice.yaml`
- `registry audit` — runs `scripts/registry_audit.py` and prints
  drift count
- `schema introspect <table>` — runs
  `notebooks/_shared/schema.py:schema_introspect_table`

#### Scenario: CLI models list prints every entry

- **GIVEN** the `MODEL_REGISTRY` populated with the 5 families
- **WHEN** the operator runs
  `bun run cianfhoghlaim models list`
- **THEN** the output lists every entry grouped by family
  (ocr_vision, text_llm, embedder, rerank, image_gen, voice,
  translation)
- **AND** the JSON variant
  (`bun run cianfhoghlaim models list --json`)
  outputs `[{key, family, role, upstream_id, backend, available}, ...]`

#### Scenario: CLI registry audit reports drift count

- **GIVEN** the `MODEL_REGISTRY` populated
- **WHEN** the operator runs `bun run cianfhoghlaim registry audit`
- **THEN** the output prints the number of hardcoded model strings
  detected by `scripts/registry_audit.py`
- **AND** the exit code is `0` if drift count is `0`,
  non-zero otherwise

#### Scenario: CLI schema introspect returns column metadata

- **GIVEN** the BIEP MotherDuck + DuckLake lakehouse populated
- **WHEN** the operator runs
  `bun run cianfhoghlaim schema introspect cianfhoghlaim.leaving_cert.mathematics_syllabus`
- **THEN** the output lists every column with name + type + nullable
- **AND** the JSON variant
  (`bun run cianfhoghlaim schema introspect <table> --json`)
  outputs `[{column_name, column_type, is_nullable}, ...]`

### Requirement: A deployment-choice.yaml is the canonical enablement file

The system SHALL maintain a `deployment-choice.yaml` (committed,
~100 LOC) at the repo root with at minimum 3 sections:

- `enabled_models: dict[str, bool]` — every `MODEL_REGISTRY` key with
  on/off toggle
- `enabled_pipelines: dict[str, bool]` — every DLT source + CocoIndex
  App with on/off toggle
- `enabled_stacks: dict[str, bool]` — every Docker Compose stack with
  on/off toggle

The file is the single source of truth for "what's enabled in this
deployment". The 3 surfaces (notebook + web UI + CLI) all read from
and write to this file.

#### Scenario: deployment-choice.yaml has sane defaults

- **GIVEN** a fresh clone of the repo
- **WHEN** the operator opens `deployment-choice.yaml`
- **THEN** the file has all 3 sections
- **AND** `enabled_models` contains every MODEL_REGISTRY key with
  `true` (except for the 5 deprecated entries: `uccix-llama2-13b`,
  `gemma-3-4b`, `llama-3.2-vision-11b`, the 5 ghost models, etc.)
- **AND** `enabled_pipelines` contains every DLT source + CocoIndex App
  with `true`
- **AND** `enabled_stacks` contains every Docker Compose stack with
  `true`

#### Scenario: deployment-choice.yaml is JSON-schema validated

- **GIVEN** the `deployment-choice.yaml` committed
- **WHEN** the operator runs `bun run cianfhoghlaim schema:validate`
- **THEN** the YAML validates against the JSON schema at
  `scripts/deployment-choice.schema.json`
- **AND** the exit code is `0`

#### Scenario: Concurrent writes are safe

- **GIVEN** the notebook open in Tab 1 AND the web UI open at
  `/control-panel/models` simultaneously
- **WHEN** the operator toggles `qwen3-vl-8b` OFF in the notebook
  while the web UI is reading the YAML
- **THEN** the file write acquires an exclusive `fcntl.flock` lock
- **AND** the web UI re-reads the YAML after the lock releases
- **AND** both surfaces show the same final state

### Requirement: All three surfaces show the same data

The system SHALL guarantee that the marimo notebook, web UI, and CLI
all read from and write to the same `deployment-choice.yaml` file
via the same `notebooks/_shared/deployment_choice.py:read_choice() /
write_choice()` helpers.

#### Scenario: State is consistent across surfaces

- **GIVEN** `deployment-choice.yaml` has
  `enabled_models: {qwen3-vl-8b: false, ...}`
- **WHEN** the operator opens the marimo notebook + the web UI +
  runs `bun run cianfhoghlaim models list`
- **THEN** all 3 surfaces show `qwen3-vl-8b` as disabled
- **AND** the 3 surfaces all reference the same `MODEL_REGISTRY`

#### Scenario: Surface-agnostic deployment-choice.yaml

- **GIVEN** an operator who has only used the CLI to set
  `enabled_models: {qwen3-vl-8b: false}`
- **WHEN** the operator opens the marimo notebook for the first time
- **THEN** Tab 1 pre-toggles `qwen3-vl-8b` OFF
- **AND** the web UI at `/control-panel/models` also shows
  `qwen3-vl-8b` as disabled
- **AND** the changes made in any surface propagate to the other
  2 surfaces on next read

### Requirement: Audit log for control-panel actions

The system SHALL record every change made through the deployment
control panel (model enable/disable + jurisdiction enable/disable) in
a `stedding/deployment-control-panel/audit.log` file. Each line
SHALL be a JSON object with the timestamp, the user (from
Pocket ID OIDC), the action type, and the changed value.

#### Scenario: operator disables a model via the control panel

- **GIVEN** the operator opens the marimo control panel
- **WHEN** they click "disable" on `minimax-m3` in the text_llm family
- **THEN** the system SHALL append a JSON line to
  `stedding/deployment-control-panel/audit.log`:
  `{"timestamp": "...", "user": "...", "action": "disable",
   "family": "text_llm", "model": "minimax-m3"}`
- **AND** the next `mise run sync:all` SHALL reflect the change in
  the deployment-choice.yaml

### Requirement: Deployment-choice editor notebook

The system MUST publish a deployment-choice editor notebook at
`notebooks/14_dev_env_tools_10_deployment_choice_editor.py` that
provides a visual interface for toggling `enabled_models` +
`enabled_pipelines` + `enabled_stacks` in `deployment-choice.yaml`.

The notebook MUST:

1. Load `deployment-choice.yaml` via `read_deployment_choice()` from
   `notebooks/_shared/schema.py` (graceful degradation if the
   import fails — return an empty choice).
2. Render `mo.ui.switch` toggles for every entry in the 3 sections
   (one per model + one per pipeline + one per stack).
3. Show a live count of enabled entries per section.
4. Include a `mo.ui.button` "Save changes" that calls
   `write_deployment_choice(modified_choice)`.
5. Be **dry-run by default** — only writes the actual
   `deployment-choice.yaml` when the env var
   `DEPLOYMENT_CHOICE_EDIT=write` is set.
6. Reference the canonical spec (`openspec/specs/deployment-control-panel/spec.md`)
   + the canonical skill
   (`.agents/skills/centralized-registry/SKILL.md`) + the
   companion notebooks (`14_dev_env_tools_07_model_registry.py` +
   `14_dev_env_tools_09_registry_drift_history.py`).

#### Scenario: Operator opens the editor

- **GIVEN** the operator runs `marimo edit notebooks/14_dev_env_tools_10_deployment_choice_editor.py`
- **WHEN** the notebook loads
- **THEN** it shows the current `enabled_models` count + the
  `enabled_pipelines` count + the `enabled_stacks` count
- **AND** it shows a `mo.ui.switch` per entry in all 3 sections
- **AND** the Save button is visible

#### Scenario: Operator toggles a model OFF and saves

- **GIVEN** the operator toggles `minimax-m3` to OFF
- **AND** they click "Save changes"
- **WHEN** `DEPLOYMENT_CHOICE_EDIT=write` is set
- **THEN** `write_deployment_choice()` is called with the modified choice
- **AND** `deployment-choice.yaml` is updated on disk
- **AND** the change is visible in the marimo control panel
  (`notebooks/00_control_panel.py`) on next read

#### Scenario: Operator toggles a model OFF in dev mode (dry-run)

- **GIVEN** the operator toggles `minimax-m3` to OFF
- **AND** they click "Save changes"
- **WHEN** `DEPLOYMENT_CHOICE_EDIT` is NOT set
- **THEN** `write_deployment_choice()` is NOT called
- **AND** the notebook shows a "dry-run" warning
- **AND** `deployment-choice.yaml` is unchanged

