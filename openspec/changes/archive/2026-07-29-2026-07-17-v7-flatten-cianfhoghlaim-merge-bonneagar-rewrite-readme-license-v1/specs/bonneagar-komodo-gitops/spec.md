# Requirements

> **MODIFIED** by `2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/`.

The pre-v7 spec referenced `bonneagar/komodo/resource-syncs/*.toml`
which is still correct post-v7 (bonneagar/ is preserved as a
subdirectory, not flattened). However, two changes are needed:

1. The `iac:bootstrap at root` simplification (which would have
   deleted the `--cwd bonneagar` shim) is **reverted**.
2. The repo URL in `CONFIG.gitRepo` is clarified.

## ADDED Requirements

### Requirement: Resource-Sync Per Host

The Komodo fleet SHALL be managed via 3 resource-syncs —
`bonneagar/komodo/resource-syncs/{arm1-oci,bunchloch,cross-cutting}.toml`
— each of which is registered with Komodo via `POST /resource-sync`
and auto-pulled from the repo on every commit.

The `arm1-oci.toml` resource-sync SHALL contain the procedures +
stacks for the control plane: Pangolin + Komodo Core + Infisical +
Locket + Backrest + observability (logfire, dozzle, beszel) +
OpenClaw + OpenChamber + Pangolin tunnels (newt-arm1-oci +
olm-arm1-oci) + Pocket ID + TinyAuth + Traefik (the 3 Pangolin
bundle components).

The `bunchloch.toml` resource-sync SHALL contain the procedures +
stacks for the data plane + dev: Oideachais + litellm + langfuse +
mlflow + Dagster + lakehouse + Cognee + lancedb + falkordb +
graphiti + Memgraph + hermes + mlx-omni + lmnr + Marimo +
mailcow-dockerized + leabharlann-email-inbox + 5 action-only
procedures + croilar procedures + 5 high-value orchestrator
procedures.

The `cross-cutting.toml` resource-sync SHALL contain the 4
cross-cutting prerequisites: `pangolin-first`, `komodo-core`,
`infisical-first`, `locket-deploy`.

#### Scenario: New procedure auto-deploys via resource-sync

- **GIVEN** a developer adds a new `[[procedure]]` block to
  `bonneagar/komodo/resource-syncs/bunchloch.toml`
- **WHEN** the commit is pushed to `main`
- **THEN** Komodo SHALL auto-pull the updated file within 60s (via
  the resource-sync `on_pull: true`)
- **AND** the new procedure SHALL appear in the Komodo UI
- **AND** no manual `iac:deploy` invocation SHALL be required

### Requirement: IaC Slims to Orchestration Layer

The `bonneagar/iac/` IaC SHALL NOT push procedures + stacks +
monitors + alerts (these are owned by the resource-syncs). The IaC
SHALL keep only the orchestration responsibilities: `iac:bootstrap`
(8-phase state machine orchestrating Pulumi → Infisical → Pangolin
→ Komodo → Newt → resource-syncs), `iac:sync:secrets`,
`iac:sync:resources` (Pangolin private resource DELETE-then-CREATE
for the 3 manually-created resources), `iac:sync:variables`,
`iac:sync:action-recipients`, `iac:sync:olm`, `iac:health`.

The deprecated `iac:sync:procedures` + `iac:sync:resource-syncs`
commands SHALL be removed (the canonical Komodo GitOps pattern
auto-pulls via the resource-syncs; no manual sync is required).

The IaC entry point remains at `bonneagar/iac/cli.ts`. The root
`package.json` iac:* scripts delegate via `--cwd bonneagar`.

#### Scenario: iac:health reports Komodo resource-sync state

- **WHEN** `bun run iac:health` is run (delegating to
  `bun run --cwd bonneagar iac:health`)
- **THEN** the output SHALL include a Komodo `listResourceSyncs()`
  section with the 3 resource-syncs + their `last_pull_at`
  timestamps
- **AND** any resource-sync whose `last_pull_at` is > 1 hour old
  SHALL be flagged as `STALE`

### Requirement: Resource-Sync Auto-Pull

Each resource-sync `.toml` file SHALL declare `on_pull: true` +
`interval: 60000` (60 seconds) so Komodo auto-pulls from the repo
on every commit. The `repo`, `branch`, `git_provider`, and
`git_account` fields SHALL match the values in
`bonneagar/iac/config.ts`
(`CONFIG.gitRepo = "kings_college_galway"`,
`CONFIG.gitProvider = "forgejo.cianfhoghlaim.ie"`).

The resource-sync SHALL set `delete = false` (safe; never
auto-delete on drift) and `managed = true` (Komodo tracks the
resource but doesn't own the file).

#### Scenario: Resource-sync auto-pulls on commit

- **GIVEN** a commit is pushed to `main` on
  `forgejo.cianfhoghlaim.ie/cliste/kings_college_galway`
- **WHEN** Komodo detects the new commit (via its 60s poll interval)
- **THEN** it SHALL `git pull` the repo and apply any resource-sync
  changes within 60s
- **AND** the Komodo UI SHALL show the updated resource-sync + its
  `last_pull_at` timestamp

### Requirement: Pre-flight gate before resource-sync apply

The 3 Komodo resource-syncs MUST NOT be applied without first
running `bun run preflight:arm-oci`. The resource-syncs are
`bonneagar/komodo/resource-syncs/{arm1-oci,bunchloch,cross-cutting}.toml`.

#### Scenario: Resource-sync apply attempted without preflight

- **WHEN** an agent runs `iac:bootstrap` (which registers the 3
  resource-syncs) without first running
  `bun run preflight:arm-oci`
- **THEN** the IaC SHALL refuse with exit 1 and the message
  "REFUSING TO APPLY: run `bun run preflight:arm-oci` first"

## ADDED Requirements

### Requirement: Bonneagar/ subdir is the IaC root

The Komodo GitOps pattern SHALL treat `bonneagar/` as the canonical
IaC root. Any future IaC change SHALL add files under
`bonneagar/{iac,stacks,komodo,pangolin,deploy-runbooks,...}/` — not
under the repo root.

#### Scenario: IaC change lives under bonneagar/

- **WHEN** a developer adds a new IaC resource (stack, procedure,
  monitor, alert, etc.)
- **THEN** the file SHALL land at `bonneagar/{stacks,komodo,...}/...`
- **AND** the resource-sync toml SHALL reference the file by its
  bonneagar-relative path
