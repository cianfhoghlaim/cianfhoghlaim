# Spec Delta: agent-platform-cluster

## ADDED Requirements

### Requirement: deploy-pangolin-newt-arm1-oci brings the arm1-oci-side newt client online

The system SHALL provide a `deploy-pangolin-newt-arm1-oci` Komodo
procedure that brings the secondary newt client online on the
`arm1-oci` control plane. This secondary newt is required so that
arm1-oci-hosted services (hermes, openclaw, openchamber, langfuse)
can route through the local gerbil WireGuard server without going
back to bunchloch first.

The procedure SHALL have 5 stages (mirrors `deploy-newt-bunchloch-v2`):
1. **preflight** — verify Pangolin + Infisical are reachable + healthy
2. **iac-provision** — `bun run iac:sync:sites` (auto-provisions the arm1-oci newt site)
3. **stackup** — extend the pangolin compose with the newt service (`docker compose -f compose.yaml -f newt.yaml -f newt.sidecar.yaml up -d newt`)
4. **wireguard-tunnel** — wait up to 60s + dump `wg show`
5. **health-checks** — 5 verifications including newt v1.14.0 assertion + pangolin-core reachability

The v2 procedure is wired into the cross-cutting prereq order (runs
AFTER `locket-deploy`, BEFORE `deploy-newt-bunchloch-v2`).

#### Scenario: iac-provision runs as Stage 2

- **WHEN** `km run procedure deploy-pangolin-newt-arm1-oci` runs
- **THEN** Stage 2 calls `bun run iac:sync:sites`
- **AND** the arm1-oci newt site is auto-provisioned via the Pangolin Integrations API
- **AND** the newtId + newtSecret are written to local `~/.env` + Infisical (under `PANGOLIN_NEWT_ARM1_*`)

#### Scenario: newt version mismatch detected

- **WHEN** the pangolin-newt container is at v1.13.0 (or any version ≠ 1.14.0)
- **THEN** Stage 5 health-checks emits `newt version MISMATCH (expected 1.14.0)`
- **AND** the procedure exits non-zero

#### Scenario: all 5 health-checks pass

- **WHEN** `km run procedure deploy-pangolin-newt-arm1-oci` runs after `iac:sync:sites` has succeeded
- **THEN** Stage 5 verifies:
  1. pangolin-newt container is Up
  2. newt-sidecar Locket has resolved 2 secrets (NEWT_ARM1_ID, NEWT_ARM1_SECRET)
  3. newt version = 1.14.0
  4. WireGuard handshake present
  5. pangolin-core on arm1-oci remains reachable (the newt shouldn't break the control plane)
- **AND** the procedure exits 0
- **AND** the arm1-oci-hosted services (hermes, openclaw, openchamber) are now reachable via the Pangolin mesh without going through bunchloch
