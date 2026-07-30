# Pre-deploy blockers

## Purpose

The 3 pre-deploy blockers (GitHub issues #81 image digest pinning, #82 arm1-oci headroom check, #107 T1 stack docs follow-up) that have been open since 2026-06-26 / 2026-07-10. The 2 Komodo deploy procedures (`deploy-openclaw-arm1-oci` + `deploy-openchamber-arm1-oci`) are blocked until these 3 are resolved. This spec documents the canonical resolution pattern.
## Requirements
### Requirement: SHA256 image digest pinning for all multi-CPU/RAM agent surfaces

The system SHALL replace every placeholder `sha256:0000…0000` image digest in `bonneagar/stacks/{openclaw,openchamber,...}/compose.yaml` with the real upstream image digest. The `scripts/fetch-image-digest.sh` shell script SHALL fetch the digest via `docker buildx imagetools inspect --raw` for any `ghcr.io/<org>/<repo>:<tag>` image and emit it in the canonical `ghcr.io/<org>/<repo>:<tag>@sha256:<64-hex>` format.

#### Scenario: openclaw image digest is fetched + pinned

- **WHEN** `mise run pre-deploy:fetch-image-digests` is invoked
- **THEN** the task SHALL call `bash scripts/fetch-image-digest.sh ghcr.io/openclaw/openclaw:v1.16.3`
- **AND** the returned SHA256 SHALL be substituted for the `0000…0000` placeholder in `bonneagar/stacks/openclaw/compose.yaml`
- **AND** the task SHALL append the digest to `stedding/pre-deploy/image-digests-{date}.json`

### Requirement: arm1-oci headroom check before deploy

The system SHALL provide a deploy-time headroom check that runs against the `arm1-oci` Oracle Cloud Ampere A1 host. The check SHALL emit a JSON snapshot with `host_info.{cpu_pct,mem_pct,disk_pct}` + `containers[]`, then derive a deploy-or-abort verdict: `✅ proceed` (all 3 < 80%) / `⚠️ migrate` (80-95%) / `🚫 abort` (> 95%).

#### Scenario: arm1-oci has sufficient headroom

- **WHEN** `mise run pre-deploy:arm1-oci-headroom` is invoked
- **THEN** the task SHALL run `./infrastructure/audit/scripts/inventory-arm1-oci.sh`
- **AND** the task SHALL emit `✅ proceed` if `cpu_pct < 80 && mem_pct < 80 && disk_pct < 80`
- **AND** the task SHALL write the JSON snapshot to `stedding/pre-deploy/arm1-oci-headroom-{date}.json`

### Requirement: T1 stack docs + secrets env auto-generation

The system SHALL provide `scripts/generate-stack-docs.sh` + `scripts/generate-stack-secrets-env.sh` that produce canonical per-stack docs (one per stack directory under `bonneagar/stacks/`) + verify every stack's `secrets.env` has the canonical Infisical URI grammar.

#### Scenario: T1 stack docs + secrets env generated for all 89 stacks

- **WHEN** `mise run pre-deploy:generate-stack-docs` is invoked
- **THEN** the task SHALL call `bun run scripts/stack-doctor.sh --emit-md cianfhoghlaim/docs/stacks/` for every `bonneagar/stacks/*/`
- **AND** all 89 stacks SHALL have a `cianfhoghlaim/docs/stacks/<name>.md` doc
- **WHEN** `mise run pre-deploy:generate-stack-secrets` is invoked
- **THEN** the task SHALL verify 0 mixed-grammar stacks via `bun run scripts/stack-doctor.sh --check-grammar`

### Requirement: pre-deploy tasks surface in the deployment control panel

The system SHALL surface the 4 pre-deploy mise tasks (pre-deploy:fetch-image-digests,
pre-deploy:arm1-oci-headroom, pre-deploy:generate-stack-docs,
pre-deploy:generate-stack-secrets) in the deployment control panel marimo notebook
(`notebooks/24_deployment_control_panel.py`) as a "Pre-deploy blockers" panel
at the top of the notebook, with one click-to-run button per task.

#### Scenario: Deployment control panel surfaces pre-deploy status

- **WHEN** the user opens `notebooks/24_deployment_control_panel.py`
- **THEN** the "Pre-deploy blockers" panel SHALL show the current status of all 4 tasks
  (✅ done / ⚠️ pending / 🚫 failing) based on the latest pre-deploy reports in
  `stedding/pre-deploy/`
- **AND** clicking each task button SHALL emit a click-to-run marker (the actual
  `mise run` invocation is operator-side; the click only sets the intent flag)

#### Scenario: Pre-deploy panel auto-refreshes after each mise run

- **WHEN** any of the 4 pre-deploy mise tasks is invoked
- **THEN** the `stedding/pre-deploy/` reports SHALL be regenerated
- **AND** the deployment control panel SHALL re-read the reports on the next
  refresh

