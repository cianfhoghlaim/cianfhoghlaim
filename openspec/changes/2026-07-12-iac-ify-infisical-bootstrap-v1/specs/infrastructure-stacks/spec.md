# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: Stacks reference Infisical secrets via the canonical pattern (no plaintext fallback)

Every Docker Compose stack under `bonneagar/stacks/<name>/` SHALL
reference secrets via one of two patterns (in priority order):

1. **Preferred**: `infisical://dev-baile/<path>/<key>` references in `secrets.env` — these are resolved at container startup by the Locket sidecar (no plaintext secrets in the repo)
2. **Bootstrap-only**: hardcoded env vars in `compose.yaml`'s `environment:` section — used ONLY for the Infisical stack itself (and other bootstrap stacks that must start before Infisical exists) — these have a `<!-- bootstrap-only -->` comment marking them as temporary

No stack SHALL have plaintext secrets in `compose.yaml`, `secrets.env`, or any other file (with the bootstrap-only exception above).

#### Scenario: a consumer stack uses Infisical URIs

- **GIVEN** `stacks/komodo/secrets.env` has `KOMODO_PASSWORD=infisical://dev-baile/komodo/password`
- **WHEN** the Komodo stack is deployed
- **THEN** the Locket sidecar resolves `KOMODO_PASSWORD` from Infisical at container startup
- **AND** the resolved value is written to `/run/secrets/locket/secrets.env` inside the Komodo container
- **AND** Komodo reads the password from the secrets file
- **AND** no plaintext password is visible in the bons IaC repo

#### Scenario: the Infisical stack itself uses bootstrap-only secrets

- **GIVEN** `stacks/infisical/compose.yaml` has hardcoded `POSTGRES_PASSWORD` and `ENCRYPTION_KEY` env vars (marked with `<!-- bootstrap-only -->`)
- **WHEN** the Infisical stack is deployed for the FIRST time
- **THEN** the container starts with these hardcoded secrets (because no Infisical instance exists yet to source them from)
- **AND** the bons IaC's `iac:bootstrap-infisical` command then moves those secrets into the fresh Infisical vault (path: `/infisical/`)
- **AND** the NEXT deploy of the Infisical stack uses `infisical://dev-baile/infisical/...` URIs in `secrets.env` (not the hardcoded values)

### Requirement: Infisical stack is GitOps-managed (not raw `docker run`)

The system SHALL provide a Komodo-orchestrated deployment of the Infisical
stack on `arm1-oci` (the canonical production host per the bons
AGENTS.md "infrastructure" tier). The deployment MUST go through
Komodo's stack runner (not raw `docker run`), so the Infisical
container appears in Komodo's stack registry + can be redeployed +
rolled back via Komodo's UI.

The stack SHALL follow the 6-file GOLD_STANDARD pattern:

- `compose.yaml` — Docker Compose definitions for Infisical + Postgres + Redis + Locket sidecar
- `sidecar.yaml` — Locket Infisical provider config (the same pattern every other stack uses)
- `secrets.env` — Infisical secret references (`infisical://dev-baile/infisical/encryption_key`, etc.)
- `pangolin.yaml` — Traefik routing for `https://infisical.cianfhoghlaim.ie`
- `blueprint.yaml` — Komodo Resource Sync definition
- `.env.example` — Local dev defaults (copy to `.env` for testing)

The stack MUST be wired into `komodo/stacks/infisical-arm1-oci.toml` AND
deployed via the new `komodo/procedures/deploy-infisical-arm1-oci.toml`
procedure.

#### Scenario: Infisical is GitOps-managed

- **WHEN** `km run procedure deploy-infisical-arm1-oci` completes
- **THEN** the Infisical container appears in Komodo's stack registry under `infisical` on the `arm1-oci` server
- **AND** the container is reachable at `https://infisical.cianfhoghlaim.ie/api/status` (HTTP 200, returns `{"message":"Ok",...}`)
- **AND** any subsequent deploy via Komodo's UI uses the same compose.yaml + secrets.env (no drift)
- **AND** any rollback via Komodo's UI restores the previous container version

#### Scenario: previous undocumented Infisical container is abandoned

- **GIVEN** the previous Infisical deployment was `docker run` (not Komodo-managed), with hash `3c1be3d92f88`
- **WHEN** `km run procedure deploy-infisical-arm1-oci` runs
- **THEN** the new Komodo-managed Infisical is deployed alongside the old one
- **AND** the bons IaC writes a note in `.audit.local.md` about the old container being abandoned (operator can `docker rm 3c1be3d92f88` after exporting any unique secrets)
- **AND** the Locket sidecars on every other host automatically point at the new Infisical (via `INFISICAL_URL=https://infisical.cianfhoghlaim.ie`)

### Requirement: Stacks re-use the Locket Infisical provider (no per-stack provider divergence)

Every stack under `bonneagar/stacks/<name>/` that uses Locket SHALL
configure the Locket sidecar with the Infisical provider
(`--provider=infisical`) AND use the canonical env-var names:

- `INFISICAL_URL` — the Infisical server URL (default: `https://infisical.cianfhoghlaim.ie`)
- `INFISICAL_CLIENT_ID` — the bons-iac machine identity client_id
- `INFISICAL_CLIENT_SECRET` — the bons-iac machine identity client_secret
- `INFISICAL_PROJECT_ID` — `f3cff583-b74b-4804-b9d3-db8b68885236` (the dev-baile project)
- `INFISICAL_DEFAULT_ENVIRONMENT` — `dev`
- `INFISICAL_DEFAULT_PATH` — `/` (the root path for shared secrets)

The bons IaC MUST validate this via `bun run validate-stacks` (the
stack-doctor turbo task). A stack that diverges from this pattern
SHALL fail the validation.

#### Scenario: a stack uses non-canonical Locket config

- **WHEN** `stacks/<name>/sidecar.yaml` uses `--provider=hashicorp-vault` (not Infisical)
- **THEN** `bun run validate-stacks` exits 1
- **AND** reports `ERROR: <name>: sidecar uses non-canonical provider (got hashicorp-vault, expected infisical)`
- **AND** the stack is NOT added to Komodo's resource registry

#### Scenario: a stack uses canonical Locket config

- **WHEN** `stacks/<name>/sidecar.yaml` uses `--provider=infisical` + the canonical env-var names
- **THEN** `bun run validate-stacks` exits 0
- **AND** the stack is added to Komodo's resource registry under the `bons` resource-sync
