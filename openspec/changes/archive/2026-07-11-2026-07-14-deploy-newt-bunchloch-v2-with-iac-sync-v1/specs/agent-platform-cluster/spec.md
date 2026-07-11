# Spec Delta: agent-platform-cluster

## ADDED Requirements

### Requirement: deploy-newt-bunchloch-v2 integrates with iac:sync:sites + asserts newt v1.14.0

The system SHALL provide a `deploy-newt-bunchloch-v2` Komodo procedure
that supersedes the legacy `deploy-newt-bunchloch` (v1). The v2
procedure SHALL integrate with the `iac:sync:sites` command (which
auto-provisions the bunchloch-newt site via the Pangolin Integrations
API) AND SHALL assert that the running newt container is at v1.14.0
(the canonical pin from `stacks/newt/IMAGE`).

The v2 procedure SHALL have 5 stages:
1. **preflight** — verify docker is present, env vars hydrated, locket healthy
2. **iac-provision** — `bun run iac:sync:sites` (provisions the site if not already)
3. **stackup** — `mkdir -p ~/.local/newt && docker compose up -d` (creates run-directory on first use)
4. **wireguard-tunnel** — wait up to 60s for the "tunnel established" log line + dump `wg show`
5. **health-checks** — all 4 services Up, locket secrets resolved, newt version = 1.14.0, WireGuard handshake present, komodo-core reachable

The v2 procedure is wired into the cross-cutting prereq order (runs
AFTER `locket-deploy`, BEFORE the per-host syncs).

#### Scenario: iac-provision runs as Stage 2

- **WHEN** `km run procedure deploy-newt-bunchloch-v2` runs
- **THEN** Stage 2 calls `bun run iac:sync:sites`
- **AND** the site is auto-provisioned via the Pangolin Integrations API
- **AND** the newtId + newtSecret are written to local `~/.env` + Infisical

#### Scenario: newt version mismatch detected

- **WHEN** the bunchloch-newt container is at v1.13.0 (or any version ≠ 1.14.0)
- **THEN** Stage 4 health-checks emits `newt version MISMATCH (expected 1.14.0)`
- **AND** the procedure exits non-zero
- **AND** the operator must re-deploy with the pinned IMAGE

#### Scenario: all 5 health-checks pass

- **WHEN** `km run procedure deploy-newt-bunchloch-v2` runs after `iac:sync:sites` has succeeded
- **THEN** Stage 5 verifies:
  1. 4 services Up (bunchloch-locket, bunchloch-newt, bunchloch-periphery, bunchloch-beszel-agent)
  2. Locket has resolved 3 secrets (NEWT_ID, NEWT_SECRET, PERIPHERY_ONBOARDING_KEY)
  3. newt version = 1.14.0
  4. WireGuard handshake present (`wg show` returns a "latest handshake" line)
  5. komodo-core on arm1-oci is reachable via the Pangolin mesh
- **AND** the procedure exits 0
