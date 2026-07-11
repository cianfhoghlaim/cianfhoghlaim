# Spec Delta: infrastructure-stacks

## ADDED Requirements

### Requirement: iac:health checks 6 auth surfaces (was 4-way; now komodo + pangolin + infisical + newt + pocket-id + tinyauth)

The system SHALL provide a `bun run iac:health` command that checks
all 6 auth surfaces in the bons IaC:

1. **Komodo** — the GitOps orchestrator
2. **Pangolin** — the identity-aware reverse proxy + WireGuard server (gerbil)
3. **Infisical** — the secrets source of truth
4. **Newt** — the WireGuard client(s) on bunchloch + arm1-oci
5. **Pocket ID** — the OIDC identity provider (admin SSO for Pangolin + newt creds)
6. **Tinyauth** — the ForwardAuth middleware (Pangolin's auth gate)

Each check SHALL report a clear actionable error message. The command
SHALL exit 0 only if all 6 are healthy.

#### Scenario: all 6 surfaces healthy

- **WHEN** the bons IaC has been fully bootstrapped
- **THEN** `bun run iac:health` outputs:
  ```
  ✓ komodo: N servers, M stacks
  ✓ pangolin: healthy
  ✓ infisical: healthy
  ✓ newt (bunchloch): container Up, version 1.14.0, WireGuard tunnel LIVE
  ✓ pocket-id: v2.9.0, U users, C OIDC clients, signup=off
  ✓ tinyauth: http://tinyauth.cianfhoghlaim.ie returned 200
  ```
- **AND** exits 0

#### Scenario: Pocket ID DB is empty (the common operator-error case)

- **WHEN** `bun run iac:health` runs and Pocket ID has 0 users
- **THEN** the output is:
  ```
  ✗ pocket-id: v2.9.0 but DB is empty (run: bun run iac:bootstrap-pocketid-admin)
  ```
- **AND** the command exits 1

#### Scenario: Tinyauth container is down (the Locket sidecar missing case)

- **WHEN** `bun run iac:health` runs and Tinyauth is not Up
- **THEN** the output is:
  ```
  ✗ tinyauth: http://tinyauth.cianfhoghlaim.ie returned 502
  ```
- **AND** the command exits 1
- **AND** the operator can run `km run procedure deploy-tinyauth-bunchloch` to fix it

#### Scenario: pocketIdHealth() has a 3-second timeout on docker exec

- **WHEN** the SQLite query inside the docker container takes longer than 3s
- **THEN** the function returns with `dbUsers=0, dbOidcClients=0, signupEnabled=false` (defaults)
- **AND** the rest of the health check still completes in <5s
- **AND** the operator sees a partial-but-actionable health result
