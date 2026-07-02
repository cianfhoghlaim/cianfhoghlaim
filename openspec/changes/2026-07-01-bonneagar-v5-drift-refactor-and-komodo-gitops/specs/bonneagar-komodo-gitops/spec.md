# Bonneagar Komodo GitOps Capability (NEW for v5)

## Purpose

`bonneagar-komodo-gitops` is a capability of the Cianfhoghlaim
platform. It defines the canonical Komodo GitOps pattern for
the `bonneagar/` fleet: 3 resource-syncs (one per host + one
cross-cutting) that auto-pull from the repo on every commit.
The corresponding source code lives at:

- `bonneagar/komodo/resource-syncs/{arm1-oci,bunchloch,cross-cutting}.toml`
- `bonneagar/iac/commands/health.ts` (registers the
  resource-syncs with Komodo via `listResourceSyncs()`)
- `bonneagar/komodo/procedures/*.toml` (the procedures the
  resource-syncs import)
- `bonneagar/komodo/stacks/*.toml` (the stack registrations
  the resource-syncs import)

## Background

Pre-v5, the IaC pushed procedures via `iac:sync:procedures` —
a state mutation, not a sync. The canonical Komodo GitOps
pattern is resource-syncs: declare the resource (stack,
procedure, monitor, action-recipient, variable, schedule)
in TOML, register it with Komodo via
`POST /resource-sync/{sync_id}/sync`, and let Komodo
auto-pull from the repo on every commit. This change converts
the 84 procedures (minus the 38 deleted + 4 phantom in
Phases 6.7-6.9) to 3 resource-syncs and slims the IaC to
the orchestration layer that ensures resource-syncs are
configured + secrets are synced.

## ADDED Requirements

### Requirement: Resource-Sync Per Host

The Komodo fleet SHALL be managed via 3 resource-syncs —
`arm1-oci.toml`, `bunchloch.toml`, `cross-cutting.toml` —
each of which is registered with Komodo via
`POST /resource-sync` and auto-pulled from the repo on every
commit.

The `arm1-oci.toml` resource-sync SHALL contain the
procedures + stacks for the control plane:
- **Pangolin** + **Komodo Core** + **Infisical** + **Locket**
- **Backrest**, **observability** (logfire, dozzle, beszel)
- **OpenClaw**, **OpenChamber**
- **Pangolin tunnels** (newt-arm1-oci + olm-arm1-oci)
- **Pocket ID**, **TinyAuth**, **Traefik** (the 3 Pangolin
  bundle components)

The `bunchloch.toml` resource-sync SHALL contain the
procedures + stacks for the data plane + dev:
- **Oideachais** + **litellm** + **langfuse** + **mlflow**
- **Dagster** + **lakehouse** (the 11-service data plane)
- **Cognee** + **lancedb** + **falkordb** + **graphiti**
- **Memgraph** + **hermes** + **mlx-omni** + **lmnr**
- **Marimo** + **mailcow-dockerized** + **leabharlann-email-inbox**
- The 5 action-only procedures (`stack-health-snapshot`,
  `team-backup`, `team-stack-health`, `team-workflow-reload`,
  `cron-ccc-reindex-bunchloch`)
- The 9 croilar-* procedures
- The 5 high-value orchestrator procedures
  (`deploy-agent-platform-cluster-bunchloch`,
  `deploy-leabharlann-email-inbox-bunchloch`,
  `deploy-oideachais-bunchloch`,
  `deploy-hermes-bunchloch`,
  `deploy-mailcow-dockerized-bunchloch`)

The `cross-cutting.toml` resource-sync SHALL contain the
4 cross-cutting prerequisites:
- `pangolin-first` (initial Pangolin install)
- `komodo-core` (initial Komodo Core deploy)
- `infisical-first` (initial Infisial vault creation)
- `locket-deploy` (initial Locket sidecar runtime)

#### Scenario: New procedure auto-deploys via resource-sync

- **GIVEN** a developer adds a new `[[procedure]]` block to
  `komodo/resource-syncs/bunchloch.toml`
- **WHEN** the commit is pushed to `main`
- **THEN** Komodo SHALL auto-pull the updated file within
  60s (via the resource-sync `on_pull: true`)
- **AND** the new procedure SHALL appear in the Komodo UI
- **AND** no manual `iac:deploy` invocation SHALL be
  required

#### Scenario: Resource-sync detects a deleted stack

- **GIVEN** a stack TOML is removed from
  `komodo/stacks/bunchloch-support.toml` (the canonical
  `bunchloch-support` bundle)
- **WHEN** the resource-sync auto-pulls
- **THEN** Komodo SHALL mark the stack as `removed` in the
  UI
- **AND** the next `iac:health` run SHALL report the
  resource-sync as `drifted` (one fewer stack than
  expected)

### Requirement: IaC Slims to Orchestration Layer

The `iac/` IaC SHALL NOT push procedures + stacks +
monitors + alerts (these are owned by the resource-syncs).
The IaC SHALL keep only the orchestration responsibilities:

- `iac:bootstrap` (8-phase state machine; orchestrates the
  Pulumi → Infisical → Pangolin → Komodo → Newt →
  resource-syncs sequence)
- `iac:sync:secrets` (Infisical vault sync)
- `iac:sync:resources` (Pangolin private resource
  DELETE-then-CREATE — for the 3 manually-created
  resources `komodo`, `cal-diy`, `infisical` that override
  blueprints)
- `iac:sync:variables` (cross-stack env vars)
- `iac:sync:action-recipients` (Discord / email / Slack)
- `iac:sync:olm` (Pangolin OLM clients — idempotent via
  `getOrCreateOlmClient()`)
- `iac:health` (all 3 systems + Komodo resource-sync
  health)

The deprecated `iac:sync:procedures` +
`iac:sync:resource-syncs` commands SHALL be removed (the
canonical Komodo gitops pattern auto-pulls via the
resource-syncs; no manual sync is required).

#### Scenario: iac:health reports Komodo resource-sync state

- **WHEN** `bun run iac:health` is run
- **THEN** the output SHALL include a Komodo
  `listResourceSyncs()` section with the 3 resource-syncs
  + their `last_pull_at` timestamps
- **AND** any resource-sync whose `last_pull_at` is > 1
  hour old SHALL be flagged as `STALE`

### Requirement: Resource-Sync Auto-Pull

Each resource-sync `.toml` file SHALL declare
`on_pull: true` + `on_pull: true` + `interval: 60000` (60
seconds) so Komodo auto-pulls from the repo on every commit.

The `repo`, `branch`, `git_provider`, and `git_account`
fields SHALL match the values in `iac/config.ts`
(`CONFIG.gitRepo = "kings_college_galway"`,
`CONFIG.gitProvider = "forgejo.cianfhoghlaim.ie"`).

The resource-sync SHALL set `delete = false` (safe; never
auto-delete on drift) and `managed = true` (Komodo tracks
the resource but doesn't own the file).

#### Scenario: Resource-sync auto-pulls on commit

- **GIVEN** a commit is pushed to `main` on
  `forgejo.cianfhoghlaim.ie/cliste/kings_college_galway`
- **WHEN** Komodo detects the new commit (via its 60s
  poll interval)
- **THEN** it SHALL `git pull` the repo and apply any
  resource-sync changes within 60s
- **AND** the Komodo UI SHALL show the updated
  resource-sync + its `last_pull_at` timestamp

#### Scenario: Resource-sync drift detection

- **GIVEN** a stack TOML is removed from a resource-sync
  file in the repo
- **WHEN** the resource-sync auto-pulls
- **THEN** Komodo SHALL mark the resource as `removing`
  (in 2-phase delete mode)
- **AND** if no `.gitignore` or `komodo_skip=true` label
  blocks it, Komodo SHALL delete the resource on the next
  sync

## Cross-references

- [`infrastructure-stacks`](../infrastructure-stacks/spec.md) —
  the 88 stacks at `bonneagar/stacks/`
- [`bonneagar-iac-merge`](../bonneagar-iac-merge/spec.md) —
  the IaC capability (slimmed to orchestration layer)
- [`dagger-pipelines`](../dagger-pipelines/spec.md) —
  the Dagger module that wires `iac:bootstrap` into CI
- [`secrets-management`](../../../.agents/skills/secrets-management/SKILL.md) —
  the Infisical + Locket + mise 3-way contract
