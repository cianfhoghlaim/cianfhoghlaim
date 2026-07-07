# `author-archive-pipeline` capability spec — bonneagar-v4-canonical-and-stack-migration delta

The `author-archive-pipeline` capability spec governs the
author-archive DLT sources + BAML extraction + Dagster
assets. After the migration, the `hf-watchdog` stack (which
monitors the v4 OCR/VLM registry) is at
`bonneagar/stacks/ci/hf-watchdog/` with the Python code at
`cianfhoghlaim/ci/hf_watchdog.py`.

## ADDED Requirements

### Requirement: `hf-watchdog` stack at `bonneagar/stacks/ci/hf-watchdog/`

The system SHALL deploy the HF Hub liveness watchdog as a
Docker Compose stack at `bonneagar/stacks/ci/hf-watchdog/`
with the 6-file GOLD_STANDARD pattern.

#### Scenario: hf-watchdog is IaC-registered

- **WHEN** `bun run iac:deploy-stacks` runs
- **THEN** the `hf-watchdog-bunchloch` stack SHALL be
  registered in Komodo with tags `host:bunchloch` + `tier:ci`
  + `project:cianfhoghlaim`
- **AND** the stack SHALL be deployable via
  `komodo run procedure deploy-hf-watchdog-bunchloch`

#### Scenario: hf-watchdog reads VISION_MODELS from the cianfhoghlaim image

- **WHEN** the `hf-watchdog` container starts
- **THEN** it SHALL `import cianfhoghlaim.ocr.models.VISION_MODELS`
  from the `ghcr.io/cianfhoghlaim/cianfhoghlaim:dev` image
  (which provides the `cianfhoghlaim` Python package)
- **AND** it SHALL verify every `unsloth_id` / `mlx_id` /
  `upstream_id` against the HF Hub API
- **AND** it SHALL post a Slack alert on any 404 (using the
  `SLACK_WEBHOOK_URL` env var from Infisical)

### Requirement: `watchdog.py` lives in `cianfhoghlaim/ci/`

The system SHALL ship the watchdog Python code at
`cianfhoghlaim/ci/hf_watchdog.py` (a new `ci` subdir at the
top of `cianfhoghlaim/`).

#### Scenario: `cianfhoghlaim.ci` is importable

- **WHEN** the user runs `python -c "import cianfhoghlaim.ci.hf_watchdog"`
- **THEN** the import SHALL succeed
- **AND** the module SHALL expose a `run_watchdog(interval=86400)`
  function

## MODIFIED Requirements

*(None — the change only ADDs the new hf-watchdog stack
location; the existing 7 dagster assets + 1 BAML metadata
extraction + 3 CocoIndex apps are unchanged.)*

## REMOVED Requirements

*(None.)*
