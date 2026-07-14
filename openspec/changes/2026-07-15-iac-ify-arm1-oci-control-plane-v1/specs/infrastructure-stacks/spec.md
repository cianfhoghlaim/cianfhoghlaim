# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: A single bundled `stacks/control-plane/` stack contains all 5 control-plane services

The system SHALL provide a `stacks/control-plane/` 6-file GOLD_STANDARD
stack that bundles the 5 control-plane services (Komodo + Infisical +
Pangolin + Pocket ID + Tinyauth + Locket) into a single docker-compose
deployment. The stack MUST follow the standard 6-file pattern:

- `compose.yaml` — 7 services (komodo-core + pangolin-core + pocket-id + tinyauth + infisical + 3 data store services) + 5 locket sidecars + 1 traefik TLS terminator
- `sidecar.yaml` — Locket Infisical provider config (watch mode, project_id from env, env from env)
- `secrets.env` — `{{ infisical:///... }}` refs for each service's secrets (Pangolin signing_key, Pocket ID encryption_key, Komodo DB url, Infisical encryption_key, Tinyauth Pocket ID client_id/secret)
- `pangolin.yaml` — Traefik routes for `komodo.`, `auth.`, `infisical.`, `tinyauth.`, `pocket-id.` (6-label pattern)
- `blueprint.yaml` — Komodo Resource Sync manifest (the stack is GitOps-managed by Komodo)
- `.env.example` — Bootstrap-mode env vars (Infisical ENCRYPTION_KEY + DB creds, OIDC config placeholders)

Each service fetches its secrets via the Locket sidecar pattern. The
Locket sidecar reads from Infisical via the `infisical:///` URI syntax.
The stack is deployable on either bunchloch (local dev) or arm1-oci
(production via Pulumi-provisioned VM).

#### Scenario: deploy the bundled stack on bunchloch

- **GIVEN** the operator is on bunchloch with Docker + the bons IaC installed
- **WHEN** `cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar/stacks/control-plane && docker compose up -d` runs
- **THEN** the 7 services (komodo-core + pangolin-core + pocket-id + tinyauth + infisical) start
- **AND** the 3 data store services (komodo-ferretdb + komodo-postgres + infisical-db + infisical-redis) start
- **AND** the 5 locket sidecars start and resolve the `{{ infisical:///... }}` refs from secrets.env
- **AND** the traefik TLS terminator starts
- **AND** all 5 services have their secrets materialized to `/run/secrets/locket/secrets.env`
- **AND** the stack is reachable at `http://localhost:3000` (komodo) + `http://localhost:8080` (infisical) + `http://localhost:1411` (pocket-id) + `http://localhost:3001` (tinyauth) + `http://localhost:3002` (pangolin)

#### Scenario: deploy the bundled stack on arm1-oci via Komodo

- **GIVEN** the bons IaC's Pulumi IaC has provisioned an arm1-oci VM
- **AND** Komodo Core is running on arm1-oci
- **WHEN** `km run procedure deploy-control-plane-arm1-oci` runs
- **THEN** Komodo creates a Server resource for arm1-oci
- **AND** Komodo clones the bons IaC repo
- **AND** Komodo deploys the `stacks/control-plane/` docker-compose via the Periphery agent on arm1-oci
- **AND** the 5 locket sidecars resolve the secrets from the same Infisical instance (on bunchloch OR arm1-oci, depending on target)
- **AND** the stack is reachable at the production domains (e.g. `https://komodo.cianfhoghlaim.ie`)

### Requirement: Every stack uses the Locket Infisical provider (no per-stack provider divergence)

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
`stack-doctor` turbo task). A stack that diverges from this pattern
SHALL fail the validation.

The `iac/docs/locket.md` file (NEW in this change) documents the
canonical Locket Infisical setup pattern (port from `/stedding/locket`).

#### Scenario: a stack uses non-canonical Locket config

- **WHEN** `stacks/<name>/sidecar.yaml` uses `--provider=hashicorp-vault` (not Infisical)
- **THEN** `bun run validate-stacks` exits 1
- **AND** reports `ERROR: <name>: sidecar uses non-canonical provider (got hashicorp-vault, expected infisical)`
- **AND** the stack is NOT added to Komodo's resource registry

#### Scenario: a stack uses canonical Locket config

- **WHEN** `stacks/<name>/sidecar.yaml` uses `--provider=infisical` + the canonical env-var names
- **THEN** `bun run validate-stacks` exits 0
- **AND** the stack is added to Komodo's resource registry under the `bons` resource-sync
