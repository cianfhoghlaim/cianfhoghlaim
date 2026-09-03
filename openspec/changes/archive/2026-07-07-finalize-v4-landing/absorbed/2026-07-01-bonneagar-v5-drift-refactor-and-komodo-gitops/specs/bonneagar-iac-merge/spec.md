# Bonneagar IaC Merge — MODIFIED requirements for v5 (completion)

## MODIFIED Requirements

### Requirement: Pocket ID OIDC Authentication

The `iac/auth.ts:ensurePangolinAuth()` function SHALL
implement the Pocket ID OIDC `client_credentials` flow as
the fallback path when `PANGOLIN_API_KEY` is unset or returns
401. The OIDC token SHALL be cached for 1 hour and refreshed
on expiry. The Pocket ID client credentials SHALL be stored
in Infisical at `infisical://dev-baile/pangolin/pocket_id_*`
(not in the IaC repo).

The `iac/auth.ts:ensureKomodoAuth()` function SHALL
implement a `komodo-recover.sh` fallback (docker exec into
`komodo-ferretdb` to reset the admin password) when both
`KOMODO_JWT` and `KOMODO_PASSWORD` are unset.

The hardcoded username `ciansedai` SHALL be replaced with
`CONFIG.komodoUsername` (env-configurable).

#### Scenario: Pocket ID OIDC flow succeeds

- **GIVEN** `PANGOLIN_API_KEY` is unset
- **WHEN** `bun run iac:health` is run
- **THEN** `iac/auth.ts:ensurePangolinAuth()` SHALL mint a
  new OIDC token via `POST ${POCKET_ID_URL}/oidc/token` with
  `grant_type=client_credentials` + the client_id +
  client_secret from Infisical
- **AND** the Pangolin client SHALL be constructed with
  the Bearer token

#### Scenario: Komodo JWT is missing

- **GIVEN** `KOMODO_JWT` is unset
- **WHEN** `bun run iac:health` is run
- **THEN** `iac/auth.ts:ensureKomodoAuth()` SHALL attempt
  `KOMODO_PASSWORD` login first
- **AND** if that also fails, it SHALL invoke
  `komodo-recover.sh` (docker exec into komodo-ferretdb to
  reset the admin password)

### Requirement: 8-Phase Bootstrap State Machine

The `iac/commands/bootstrap.ts` SHALL implement a real
8-phase state machine:

1. **Phase 1 — Pulumi**: provision the cloud resources
2. **Phase 2 — Infisical**: create the `dev-baile`
   environment + machine identity for Komodo + machine
   identity for Locket
3. **Phase 3 — Pangolin private resources**: create the
   30 key-stack resources via the Integrations API
4. **Phase 4 — Komodo Core**: deploy `komodo.toml` + the
   FerretDB container
5. **Phase 5 — Komodo Periphery**: deploy the 2 Periphery
   agents (one per host)
6. **Phase 6 — Newt**: deploy the Newt tunnel client on
   both hosts; register the Newt ID + secret with Pangolin
7. **Phase 7 — Resource-syncs + all syncs**: register the
   3 resource-syncs; sync secrets, resources, monitors,
   alerts, variables, schedules, action-recipients, OLM
   clients
8. **Phase 8 — Blueprint import**: bulk-import the
   `pangolin/blueprint.yaml` (opt-in via
   `--with-blueprint-import`)

Each phase SHALL be idempotent + re-runnable. `--force`
SHALL skip confirmation prompts. `--dry-run` SHALL print
the planned actions without executing them.

Phase 0 (added in v5) SHALL verify Docker is installed on
the target host before any IaC commands run (this replaces
the Docker pre-install check from the deleted
`ansible/compose.yaml` lines 27-35).

#### Scenario: iac:bootstrap completes end-to-end

- **WHEN** `bun run iac:bootstrap` is run on a fresh
  `arm1-oci`
- **THEN** all 8 phases SHALL execute without `logWarn`
  stubs
- **AND** `iac:health` SHALL return 0 after completion

### Requirement: Idempotent OLM Client Sync

The `iac/commands/sync-olm.ts` SHALL be idempotent:
`getOrCreateOlmClient()` SHALL list existing OLM clients,
check if the desired client exists, and only create it if
missing. The pre-v5 behavior (unconditional `createOlmClient`
which fails on duplicates) SHALL be replaced.

#### Scenario: sync-olm re-runs successfully

- **WHEN** `bun run iac:sync:olm` is run twice in a row
- **THEN** the first run SHALL create the 5 OLM clients
- **AND** the second run SHALL report "5 already exist" +
  exit 0

### Requirement: Hetzner Exclusion

The IaC SHALL NOT reference the `cax41-hetzner` host. The
2-host topology SHALL be `arm1-oci` + `bunchloch` only.
Hetzner provisioning SHALL live exclusively in
`bonneagar/pulumi/`.

The IaC `config.ts` SHALL NOT export a `CAX41_HETZNER_IP`
env var. The IaC sync-olm command SHALL NOT reference
`cax41-hetzner-olm` as an OLM client target.

The `iac/commands/sync-resources.ts` DELETE-then-CREATE list
SHALL be `{"komodo", "cal-diy", "infisical"}` (no Hetzner
references).

#### Scenario: iac:health does not reference Hetzner

- **WHEN** `bun run iac:health` is run
- **THEN** the output SHALL NOT mention `cax41-hetzner`
- **AND** `iac/config.ts` SHALL NOT export
  `CAX41_HETZNER_IP`
- **AND** `grep -r 'cax41-hetzner' bonneagar/iac/`
  SHALL return zero results

#### Scenario: Hetzner provisioning is Pulumi-only

- **WHEN** Hetzner infrastructure needs provisioning
- **THEN** `bonneagar/pulumi/Pulumi.yaml` SHALL be the
  exclusive source of truth
- **AND** the IaC SHALL NOT add or maintain Hetzner
  resources
