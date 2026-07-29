## ADDED Requirements

### Requirement: 3 agent surfaces on arm1-oci (control plane)

The system SHALL provide the 3 agent-platform surfaces on `arm1-oci` (the control-plane host on Oracle Cloud Free Tier, Frankfurt): **hermes** + **openclaw** + **openchamber**. Each surface SHALL follow the 6-file `GOLD_STANDARD` pattern (`compose.yaml` + `sidecar.yaml` + `pangolin.yaml` + `blueprint.yaml` + `.env.example` + a `secrets.env` compatible with Locket) PLUS a Komodo `[[stack]]` registration PLUS a deploy procedure, all wired into the `arm1-oci` resource-sync.

The 3 surfaces SHALL share the existing `langfuse` observability sink (which itself depends on the `lakehouse` data plane on bunchloch). They SHALL be reachable at `https://<service>.cianfhoghlaim.ie/api/health` via the Pangolin mesh on `arm1-oci`, gated by Pocket ID OIDC + TinyAuth. Access from this Mac (bunchloch) to the arm1-oci surfaces SHALL be mediated by the `newt` (Pangolin client) stack running on bunchloch.

The upstream GHCR images for `openchamber` (`:1.0.0`) and `openclaw` (`:2026.2.6`) are private (401 on GHCR HEAD). The arm1-oci stacks SHALL reference code-owned images built from local Dockerfiles: `ghcr.io/cianfhoghlaim/openchamber:1.14.1-arm1` and `ghcr.io/cianfhoghlaim/openclaw:2026.6-arm1`. The `hermes` stack SHALL reference the **public** Docker Hub image `nousresearch/hermes-agent:v2026.7.1` (the upstream `0.17.0` tag is also private).

The omnibus procedure `deploy-agent-platform-cluster-arm1-oci` brings all 3 surfaces up in dependency order and includes a `preflight:arm-oci` safety check (Pangolin + Komodo + Infisical health + process namespace isolation) as the first stage. The omnibus accepts `--skip=<stage>` flags for partial re-deploys.

#### Scenario: openclaw.cianfhoghlaim.ie is reachable

- **WHEN** `km run procedure deploy-openclaw-arm1-oci` completes
- **THEN** `https://openclaw.cianfhoghlaim.ie/api/health` returns 200
- **AND** the `openclaw` container joins the `cianfhoghlaim` bridge network
- **AND** Locket injects the `dev-baile/openclaw/*` Infisical secrets
- **AND** the WS protocol v3 handshake (challenge + auth + connect) returns 200 at `ws://openclaw.cianfhoghlaim.ie:18789`

#### Scenario: openchamber.cianfhoghlaim.ie is reachable

- **WHEN** `km run procedure deploy-openchamber-arm1-oci` completes
- **THEN** `https://openchamber.cianfhoghlaim.ie/api/health` returns 200
- **AND** the openchamber UI serves its bundled React frontend at `https://openchamber.cianfhoghlaim.ie/`
- **AND** the `openchamber` container joins the `cianfhoghlaim` bridge network
- **AND** Locket injects the `dev-baile/openchamber/*` Infisical secrets

#### Scenario: hermes.cianfhoghlaim.ie is reachable

- **WHEN** `km run procedure deploy-hermes-arm1-oci` completes
- **THEN** `https://hermes.cianfhoghlaim.ie/api/health` returns 200
- **AND** `https://hermes.cianfhoghlaim.ie/api/status` returns `version: 0.18.0` (or newer)
- **AND** the hermes `users.allowlist` is populated with the operator's Pocket ID subject (via the `init-allowlist.sh` one-shot container)
- **AND** Locket injects the `dev-baile/hermes/*` Infisical secrets

#### Scenario: Omnibus brings all 3 surfaces up in dependency order

- **WHEN** `km run procedure deploy-agent-platform-cluster-arm1-oci` runs
- **THEN** the `preflight:arm-oci` stage passes all 4 checks
- **AND** the 3 Komodo `Build` resources complete (openchamber + openclaw + hermes)
- **AND** Stage 1 (control-plane foundation) brings up `pangolin-core-arm1` + `langfuse` + `observability`
- **AND** Stage 2 (the 3 surfaces) brings up `hermes` + `openclaw` + `openchamber` in that order
- **AND** Stage 3 (Pangolin routes) applies the 3 blueprints via the Pangolin Integration API
- **AND** Stage 4 (health checks) returns 200 for all 3 endpoints
- **AND** Stage 5 (validate) reports 0 hard failures
- **AND** the omnibus completes within 15 minutes on the arm1-oci host

#### Scenario: Operator skips a stage

- **WHEN** `km run procedure deploy-agent-platform-cluster-arm1-oci -- --skip=foundation,observability` runs
- **THEN** Stage 1 (foundation) and Stage 1b (observability) SHALL be skipped
- **AND** the skipped stages SHALL appear in the output with `SKIPPED: <reason>` markers
- **AND** the remaining stages (agent surfaces + Pangolin routes + health + validate) SHALL run as normal

#### Scenario: Remote dev workflow from this Mac

- **WHEN** the `newt` (Pangolin client) stack is up on `bunchloch` (via `km run procedure deploy-newt-bunchloch`)
- **AND** the WireGuard tunnel is established (verified via `docker exec bunchloch-newt -- newt --version` showing 1.14.0)
- **THEN** from this Mac, `curl https://hermes.cianfhoghlaim.ie/api/health` returns 200 (proves the newt → Pangolin → arm1-oci → hermes path works end-to-end)
- **AND** the same path works for `openclaw.cianfhoghlaim.ie` and `openchamber.cianfhoghlaim.ie`
