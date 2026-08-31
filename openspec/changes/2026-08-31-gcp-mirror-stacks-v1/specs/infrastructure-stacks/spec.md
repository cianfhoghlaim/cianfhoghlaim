# infrastructure-stacks — Delta for GCP Mirror Stacks v1

## ADDED Requirements

### Requirement: GCP_MIRROR_STACKS SHALL be opt-in via deployment-choice.yaml

The system MUST require the 6 GCP mirror stacks at
`bonneagar/stacks/gcp-*/` to be opt-in via `deployment-choice.yaml`.
Each stack MUST be present in the `enabled_stacks` block with a
default value of `false`. The opensource stacks (pangolin + komodo +
bunchloch) stay canonical for local dev.

#### Scenario: All 6 GCP mirror stacks are present

- **WHEN** the operator runs `jq '.enabled_stacks | keys' deployment-choice.yaml`
- **THEN** the output MUST include all 6 keys: `gcp-gemini-vertex`,
  `gcp-gemma-unsloth`, `gcp-bigquery-mirror`, `gcp-gcs-bucket`,
  `gcp-secret-manager`, `gcp-cloud-run`
- **AND** each MUST be set to `false`

#### Scenario: Operator enables a GCP mirror stack

- **WHEN** the operator edits `deployment-choice.yaml` to set
  `gcp-gemini-vertex: true`
- **THEN** `mise run stack:gcp-gemini-vertex` is enabled
- **AND** the stack can be deployed via Komodo

### Requirement: Each GCP mirror stack MUST follow the GOLD_STANDARD pattern

The system MUST require each `bonneagar/stacks/gcp-*/` directory to
contain the 6-file GOLD_STANDARD pattern: `compose.yaml` +
`sidecar.yaml` + `secrets.env` + `pangolin.yaml` + `blueprint.yaml`
+ `.env.example`.

#### Scenario: gcp-gemini-vertex has the 6 files

- **WHEN** the operator runs `ls bonneagar/stacks/gcp-gemini-vertex/`
- **THEN** the output MUST include all 6 filenames

#### Scenario: gcp-gemma-unsloth has the 6 files

- **WHEN** the operator runs `ls bonneagar/stacks/gcp-gemma-unsloth/`
- **THEN** the output MUST include all 6 filenames

#### Scenario: gcp-bigquery-mirror has the 6 files

- **WHEN** the operator runs `ls bonneagar/stacks/gcp-bigquery-mirror/`
- **THEN** the output MUST include all 6 filenames

#### Scenario: gcp-gcs-bucket has the 6 files

- **WHEN** the operator runs `ls bonneagar/stacks/gcp-gcs-bucket/`
- **THEN** the output MUST include all 6 filenames

#### Scenario: gcp-secret-manager has the 6 files

- **WHEN** the operator runs `ls bonneagar/stacks/gcp-secret-manager/`
- **THEN** the output MUST include all 6 filenames

#### Scenario: gcp-cloud-run has the 6 files

- **WHEN** the operator runs `ls bonneagar/stacks/gcp-cloud-run/`
- **THEN** the output MUST include all 6 filenames

### Requirement: GCP mirror stacks MUST NOT replace opensource stacks

The system MUST keep the opensource substrate (pangolin + komodo +
bunchloch + lakehouse + garage + infisical + locket) canonical for
local dev. The 6 GCP mirror stacks are additive — they MUST NOT
delete or rename any opensource stack.

#### Scenario: Opensource stacks remain canonical

- **WHEN** the operator enables any GCP mirror stack
- **THEN** all 105 existing opensource stacks remain in
  `bonneagar/stacks/`
- **AND** none of them are renamed or deleted