## ADDED Requirements

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