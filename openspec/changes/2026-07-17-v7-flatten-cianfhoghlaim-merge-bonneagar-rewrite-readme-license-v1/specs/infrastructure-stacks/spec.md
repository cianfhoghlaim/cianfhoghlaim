# infrastructure-stacks — MODIFIED Requirements

> **MODIFIED** by `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/`.

The pre-v7 spec already references `bonneagar/stacks/`, which is
still correct post-v7. The 88 stacks continue to live at
`bonneagar/stacks/`. The integration into the main repo (as a
subdirectory) means the stack-doctor now runs from the repo root,
not from the bonneagar subdirectory.

## MODIFIED Requirements

### Requirement: 88 Docker Compose stacks at bonneagar/stacks/

The system SHALL provide 88 Docker Compose stacks at
`bonneagar/stacks/<name>/`. Each stack SHALL follow the 6-file
GOLD_STANDARD pattern: `compose.yaml` + `sidecar.yaml` +
`secrets.env` + `pangolin.yaml` + `blueprint.yaml` + `.env.example`.

#### Scenario: Stack count is 88 post-v7

- **WHEN** `bun run iac:health` runs from the repo root
  (delegating to `bun run --cwd bonneagar iac:health`)
- **THEN** the output SHALL report 88 stacks at `bonneagar/stacks/`
- **AND** each stack SHALL pass the GOLD_STANDARD check
- **AND** the stack-doctor script (`bonneagar/audit/scripts/stack-doctor.sh`)
  SHALL be runnable from the repo root via
  `bun run validate-stacks` (which delegates via `--cwd bonneagar`)

#### Scenario: Stack-doctor runs from repo root

- **WHEN** `bun run validate-stacks` is invoked
- **AND** the delegation to
  `bash bonneagar/audit/scripts/stack-doctor.sh` succeeds
- **THEN** the script SHALL walk `bonneagar/stacks/*/compose.yaml`
  and verify the 6-file GOLD_STANDARD
- **AND** the exit code SHALL be 0 on success, non-zero on failure

### Requirement: Stack-doctor.sh is at bonneagar/audit/scripts/

The stack-doctor.sh script SHALL live at
`bonneagar/audit/scripts/stack-doctor.sh`. It SHALL use the relative
path `bonneagar/stacks/` (relative to the repo root) to walk the
88 stacks.

#### Scenario: stack-doctor.sh paths are repo-root-relative

- **WHEN** stack-doctor.sh runs (from the repo root via
  `bun run validate-stacks`)
- **THEN** its `REPO_ROOT` variable SHALL resolve to the cianfhoghlaim
  repo root
- **AND** its stack walks SHALL be `for d in bonneagar/stacks/*/; do`

## ADDED Requirements

### Requirement: NEW — IaC is reachable from repo root via --cwd

The root `package.json` MUST provide `iac:*` scripts that delegate
to the IaC via `bun run --cwd bonneagar`. The delegation MUST be
the ONLY way to invoke the IaC from the root (no symlinks, no
path manipulation, no shell aliases).

After v7, the IaC is part of the main repo; reaching it from the
repo root MUST go through this delegation.

#### Scenario: Root package.json delegates iac:* to bonneagar/

- **WHEN** a developer runs `bun run iac:health` from the repo root
- **THEN** bun SHALL execute `bun run --cwd bonneagar iac:health`
- **AND** the IaC SHALL run from `bonneagar/iac/cli.ts`
- **AND** the exit code SHALL propagate to the root command
