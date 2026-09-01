## ADDED Requirements

### Requirement: GCP mirror stacks MUST be opt-in via `deployment-choice.yaml`

The Cianfhoghlaim deployment-control-panel capability MUST expose
the 6 GCP mirror stacks (gemini-vertex + gemma-unsloth +
bigquery-mirror + gcs-bucket + secret-manager + cloud-run) as
opt-in surfaces via the `deployment-choice.yaml` file.

Per the 2026-09-01-gcp-opt-in-completion-v1 change (Phase 9 of
the cianfhoghlaim-nua v6 era plan), the OSS-first substrate
remains canonical (operator direction 2026-09-01). The GCP
opt-in is for users who specifically want the managed-cloud
substrate.

#### Scenario: A user enables the GCP substrate

- **WHEN** the operator sets `gcp-gemini-vertex: true` (and the other 5 stacks) in `deployment-choice.yaml`
- **THEN** the canonical `mise run gcp:deploy` command can deploy the 6 GCP mirrors
- **AND** the OSS-first substrate (self-hosted via `mise run stack:up`) remains the default

### Requirement: The 6 GCP mirror stacks MUST follow the canonical GOLD_STANDARD pattern

The Cianfhoghlaim deployment-control-panel capability MUST enforce
the canonical 6-file GOLD_STANDARD pattern for every GCP mirror
stack at `bonneagar/stacks/gcp-*/`:

1. `README.md` — stack purpose + opt-in instructions
2. `blueprint.yaml` — the IaC blueprint
3. `compose.yaml` — the Docker Compose definition
4. `pangolin.yaml` — the Pangolin resource definition
5. `secrets.env` — the env-var → secret mapping
6. `sidecar.yaml` — the Locket sidecar config

#### Scenario: A new GCP stack is added

- **WHEN** a developer adds `bonneagar/stacks/gcp-<name>/`
- **THEN** the developer SHALL create all 6 GOLD_STANDARD files
- **AND** the `mise run lint:stacks` CI gate SHALL verify the 6-file structure