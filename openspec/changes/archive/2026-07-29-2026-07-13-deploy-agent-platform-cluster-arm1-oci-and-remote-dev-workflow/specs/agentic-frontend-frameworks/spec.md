## ADDED Requirements

### Requirement: Remote dev workflow via newt (Pangolin client) on bunchloch

The system SHALL provide a Komodo-managed `newt` stack running on `bunchloch` (this Mac) that bridges the MacBook into the Pangolin mesh on `arm1-oci`. The `newt` stack is the canonical entry point for the operator to reach arm1-oci services (hermes + openclaw + openchamber) from a browser on this Mac via `https://*.cianfhoghlaim.ie`.

The newt stack SHALL follow the 6-file `GOLD_STANDARD` pattern under `bonneagar/stacks/newt/`:
- `compose.yaml` — 4 services: `locket` (secrets), `newt` (Pangolin client + WireGuard tunnel), `periphery` (Komodo agent), `beszel-agent` (monitoring)
- `sidecar.yaml` — canonical Locket shape (Infisical secret injection)
- `secrets.env` — `NEWT_ID` + `NEWT_SECRET` + `PERIPHERY_ONBOARDING_KEY` via Infisical
- `pangolin.yaml` — optional: newt as a private Pangolin resource
- `blueprint.yaml` — Pangolin private-resource def
- `.env.example` — local-dev defaults

The newt stack SHALL be managed by Komodo via `komodo/stacks/newt-bunchloch.toml` (server_id="bunchloch", labels `["komodo.skip=true"]` to prevent Komodo from trying to manage the newt container itself — the container is part of the operator-laptop site infrastructure, not a deployable stack).

The `deploy-newt-bunchloch` procedure SHALL verify all 4 newt services are up, the WireGuard tunnel is established (`docker exec bunchloch-newt -- newt --version` returns 1.14.0), the Komodo periphery is registered with komodo-core, and the Locket secrets are resolved.

#### Scenario: newt container is up + tunnel established

- **WHEN** `km run procedure deploy-newt-bunchloch` completes
- **THEN** `docker ps --filter name=bunchloch-newt --format "{{.Names}}\t{{.Status}}"` shows `bunchloch-newt` as `Up X minutes (healthy)`
- **AND** `docker exec bunchloch-newt -- newt --version` returns `1.14.0`
- **AND** `ifconfig` shows a `utun<N>` interface with a 100.64.x.x address (the WireGuard tunnel IP range)
- **AND** `docker logs bunchloch-locket 2>&1 | grep "secrets resolved"` shows `secrets resolved: 3 keys` (NEWT_ID, NEWT_SECRET, PERIPHERY_ONBOARDING_KEY)
- **AND** the bunchloch periphery is registered with komodo-core (verified via `docker logs bunchloch-periphery 2>&1 | grep "registered as bunchloch"`)

#### Scenario: Remote dev workflow from this Mac to arm1-oci surfaces

- **WHEN** the newt stack is up (per the previous scenario)
- **AND** the agent-platform cluster is up on arm1-oci (per the `agent-platform-cluster` spec)
- **THEN** from this Mac's terminal: `curl -fsS https://hermes.cianfhoghlaim.ie/api/health` returns 200
- **AND** the same `curl` returns 200 for `https://openclaw.cianfhoghlaim.ie/api/health` and `https://openchamber.cianfhoghlaim.ie/api/health`
- **AND** a browser on this Mac can reach each surface's WebUI at `https://<service>.cianfhoghlaim.ie/` (Pocket ID SSO via Pocket ID on arm1-oci)
