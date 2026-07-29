## ADDED Requirements

### Requirement: Locket sidecar env_file must be runtime-mounted, not host-validated

The system SHALL declare every `env_file:` path consumed by a Locket-using
service (openclaw, hermes, openchamber, langfuse, litellm, mlflow,
logfire, etc.) as a path inside the `stack-secrets` tmpfs volume that is
mounted into BOTH the locket sidecar AND the consuming service. The path
SHALL NOT be validated against the host filesystem at compose-parse time.
Stack-doctor MUST detect any `env_file:` entry whose source path is not
either (a) a host file inside the stack directory, or (b) a tmpfs volume
mount shared with a `locket` sidecar.

#### Scenario: Parse-time env_file failure surfaces as a stack-doctor finding

- **GIVEN** a developer commits a `sidecar.yaml` with
  `services.openclaw.env_file: /run/secrets/locket/secrets.env` AND
  no `stack-secrets` tmpfs volume shared with `locket`
- **AND** the developer's local docker compose parse fails with
  `env file /run/secrets/locket/secrets.env not found`
- **WHEN** `bun run validate-stacks` runs against that stack
- **THEN** the parse-time failure is reported as a **CRITICAL** finding
- **AND** the developer MUST either add the `stack-secrets` volume
  + mount OR replace the env_file with a host-readable bootstrap file

#### Scenario: A correct sidecar contract passes the gate

- **WHEN** the stack has `locket` + `<service>` both mounting
  `stack-secrets:/run/secrets/locket[:ro]` AND
  `env_file: /run/secrets/locket/secrets.env`
- **THEN** the stack-doctor parse-time gate returns OK
- **AND** `docker compose config` on the merged file resolves the
  env_file reference without error

### Requirement: Bunchloch fallback Infisical vault when arm1-OCI private resource is unhealthy

The system SHALL provide a fallback deployment path on the `bunchloch`
host that brings up a local Infisical vault (no Pangolin routing, port
8081 bound to `127.0.0.1` only) when the arm1-OCI Pangolin private
resource for `infisical.cianfhoghlaim.ie` is returning HTTP 5xx
(specifically 502 Bad Gateway at the WireGuard hop). The fallback MUST
seed a fresh `dev-baile` project with the 9 infisical paths consumed by
the openclaw + hermes services, and MUST write the bons-iac Universal
Auth client_id + client_secret to `/etc/komodo/secrets/infisical_secret`
so the Komodo Periphery mounts it identically to the OCI path.

The fallback MUST NOT modify the arm1-OCI Infisical vault. It MUST NOT
expose the local Infisical via Pangolin. The fallback MUST be torn down
with `docker compose -f bonneagar/stacks/infisical/compose.yaml down -v`
once the OCI path is repaired.

#### Scenario: Operator triggers the fallback when OCI is unhealthy

- **GIVEN** `mise run preflight:arm-oci --skip-namespace` reports
  `Infisical health: FAIL (502 Bad Gateway)`
- **AND** bunchloch has >= 25 GB free disk + >= 2 GB RAM headroom
- **WHEN** the operator runs
  `docker compose -f bonneagar/stacks/infisical/compose.yaml up -d`
- **THEN** the local Infisical backend (port 8081), postgres, and redis
  containers start
- **AND** `curl -fsS http://127.0.0.1:8081/api/status` returns 200
- **AND** running
  `bun run scripts/seed-bunchloch-fallback-vault.sh` populates the 9
  openclaw + hermes infisical paths under `dev-baile/dev`

#### Scenario: Locket resolves secrets from the fallback vault

- **GIVEN** the local Infisical is up and the seed script has populated
  the 9 secret paths
- **AND** `/etc/komodo/secrets/infisical_secret` contains the bons-iac
  Universal Auth client_id + client_secret
- **WHEN** the operator runs
  `cd bonneagar/stacks/openclaw && docker compose -f compose.yaml -f sidecar.yaml up -d`
- **THEN** the locket sidecar healthcheck returns OK
- **AND** `docker exec openclaw-locket -- /locket healthcheck` reports
  >= 9 resolved secrets
- **AND** the openclaw container starts with its env_file populated
  (no parse-time `env file not found` error)

#### Scenario: Fallback is torn down once the OCI path is repaired

- **WHEN** the operator runs
  `docker compose -f bonneagar/stacks/infisical/compose.yaml down -v`
- **THEN** the 3 local Infisical containers stop and the named volume
  is removed
- **AND** no orphan processes reference the local Infisical backend
- **AND** the operator can resume the canonical OCI path via
  `km run procedure deploy-openclaw-bunchloch`