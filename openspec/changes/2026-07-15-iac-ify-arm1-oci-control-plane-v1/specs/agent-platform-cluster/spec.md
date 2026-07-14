# Spec Delta: agent-platform-cluster

## ADDED Requirements

### Requirement: iac:bootstrap-control-plane operator one-shot provisions the full 5-control-plane setup

The system SHALL provide a `bun run iac:bootstrap-control-plane` command
that orchestrates the full control-plane setup (5 components: Komodo +
Infisical + Pangolin + Pocket ID + Tinyauth + Locket + Periphery + Newt)
end-to-end on either bunchloch (local) or arm1-oci (production).

The command MUST take a `--target` flag (`bunchloch` or `arm1-oci`) that
selects the deployment target. The command MUST run the following 8
phases IN ORDER (idempotent — each phase checks the current state and
(re)deploys as needed):

1. **locket binary** — downloads the locket Rust binary to `~/.local/bin/locket` (or `locket:infisical` Docker image for the IaC's own use); verifies it works
2. **Pulumi IaC** — provisions the VM via Pulumi (no-op for bunchloch target); for arm1-oci target, calls `iac/pulumi/oci/{deploy,setup}.ts` to provision the VM + save Cloudflare creds + DNS records to Infisical
3. **bundled stack deploy** — deploys `stacks/control-plane/` via `docker compose up -d` (bunchloch) or `km run procedure deploy-control-plane-arm1-oci` (arm1-oci)
4. **Infisical bootstrap** — invokes `iac:bootstrap-infisical` to create the first admin (via Pocket ID admin API when 1+ users exist, via Chrome MCP fallback when 0) + 8 machine identities
5. **Pocket ID OIDC wire** — invokes `iac:wire-pocketid-as-oidc` to create the `komodo` OIDC client in Pocket ID + wire Pocket ID as the OIDC IdP in Komodo + Pangolin
6. **Komodo Periphery** — invokes `iac:deploy-periphery` to create a Komodo Onboarding Key + register the Server (with `address: ""` for outbound mode) + render the Periphery compose
7. **Newt** — invokes `iac:deploy-newt` to provision a Newt site via Pangolin Integrations API + render the Newt compose
8. **health verify** — runs `iac:health` to verify all 6 surfaces report `✓` (komodo + pangolin + infisical + newt + pocket-id + tinyauth)

The command SHALL emit a JSON audit record to
`/tmp/control-plane-bootstrap-{ts}.json` containing the timestamp + the
8 phase results.

#### Scenario: cold deploy on bunchloch (local dev/canary)

- **GIVEN** a clean bunchloch with no locket installed + no Infisical running + no Komodo
- **WHEN** `bun run iac:bootstrap-control-plane-bunchloch` runs
- **THEN** phase 1 downloads locket to `~/.local/bin/locket`
- **AND** phase 2 (Pulumi) is a no-op on bunchloch
- **AND** phase 3 deploys `stacks/control-plane/` via `docker compose up -d`
- **AND** phase 4 invokes `iac:bootstrap-infisical` which detects 0 users and falls back to Chrome MCP for the first admin
- **AND** phase 5 wires Pocket ID as the OIDC IdP for Komodo + Pangolin
- **AND** phase 6 deploys Komodo Periphery on bunchloch
- **AND** phase 7 deploys Newt on bunchloch
- **AND** phase 8 verifies all 6 surfaces report `✓`
- **AND** the audit record is written to `/tmp/control-plane-bootstrap-{ts}.json`
- **AND** the command completes within 10 minutes

#### Scenario: cold deploy on arm1-oci (production)

- **GIVEN** the bons IaC's Pulumi IaC has NOT yet provisioned an arm1-oci VM
- **AND** the operator has `~/.oci/config` with the `bunchloch` profile configured
- **WHEN** `bun run iac:bootstrap-control-plane-arm1-oci` runs
- **THEN** phase 2 provisions a `VM.Standard.A1.Flex` (4 OCPUs, 24 GB RAM) on Oracle Cloud Frankfurt via Pulumi
- **AND** phase 2 saves Cloudflare creds + DNS records to Infisical
- **AND** phase 3 deploys `stacks/control-plane/` to the new VM via `km run procedure deploy-control-plane-arm1-oci`
- **AND** phase 4 bootstraps Infisical on the new VM (first admin + 8 machine identities)
- **AND** phase 5 wires Pocket ID as the OIDC IdP on the new VM
- **AND** phase 6 deploys Komodo Periphery on the new VM
- **AND** phase 7 deploys Newt on the new VM
- **AND** phase 8 verifies all 6 surfaces report `✓`
- **AND** the audit record is written to `/tmp/control-plane-bootstrap-{ts}.json`
- **AND** the command completes within 30 minutes (Pulumi VM provisioning is the long pole)

#### Scenario: warm deploy (re-run)

- **GIVEN** the control plane is already running on the target host
- **WHEN** `bun run iac:bootstrap-control-plane-<target>` runs
- **THEN** each phase detects the current state and skips the work that's already done (idempotent)
- **AND** only the missed steps run
- **AND** the audit record shows the skipped steps
- **AND** the command completes within 1 minute

### Requirement: Pocket ID as the OIDC IdP for both Komodo + Pangolin

The system SHALL provide a `bun run iac:wire-pocketid-as-oidc` command
that wires Pocket ID as the OIDC identity provider for BOTH Komodo AND
Pangolin. The command MUST:

1. Create the `komodo` OIDC client in Pocket ID via the Pocket ID admin
   API (`POST /api/oidc/clients`) with:
   - `name: "komodo"`
   - `callbackURLs: ["https://komodo.<DOMAIN>/auth/oidc/callback"]`
   - `grantTypes: ["authorization_code"]`
   - `scopes: ["openid", "profile", "email", "groups"]`
2. Update Komodo's config (via the Komodo REST API) with:
   - `KOMODO_OIDC_ENABLED=true`
   - `KOMODO_OIDC_PROVIDER=https://auth.<DOMAIN>`
   - `KOMODO_OIDC_CLIENT_ID=<the new Pocket ID client_id>`
   - `KOMODO_OIDC_CLIENT_SECRET=<the new Pocket ID client_secret>`
   - `KOMODO_OIDC_USE_FULL_EMAIL=true`
3. Create the Pocket ID Identity Provider in Pangolin (via the Pangolin
   Integrations API: `POST /v1/org/{orgId}/identity-provider`) with:
   - `name: "PocketID"`
   - `provider_type: "OAuth2/OIDC"`
   - `client_id: <the new Pocket ID client_id>`
   - `client_secret: <the new Pocket ID client_secret>`
   - `authorization_url: "https://auth.<DOMAIN>/authorize"`
   - `token_url: "https://auth.<DOMAIN>/api/oidc/token"`
   - `scopes: ["openid", "profile", "email", "groups"]`
   - `identifier_path: "email"`
4. Restart Komodo (via the Komodo REST API: `POST /execute/RestartResource`)
5. Write the 2 client_id/client_secret pairs to local `~/.env` for operator inspection
6. Emit a JSON audit record to `/tmp/oidc-wiring-{ts}.json`

#### Scenario: OIDC wire after bootstrap

- **GIVEN** Pocket ID is already bootstrapped (1+ users exist + the bons-iac machine identity is seeded)
- **AND** Komodo is running with `KOMODO_OIDC_ENABLED=false` (default)
- **WHEN** `bun run iac:wire-pocketid-as-oidc` runs
- **THEN** the Pocket ID admin API call to `POST /api/oidc/clients` succeeds (no Chrome MCP needed since 1+ users exist)
- **AND** the Komodo config update succeeds (the new client_id/secret are written)
- **AND** the Pangolin Integrations API call to add the Identity Provider succeeds
- **AND** Komodo restarts automatically
- **AND** the operator can now log into Komodo via Pocket ID at `https://komodo.<DOMAIN>/auth/oidc/callback`
- **AND** the audit record is written

#### Scenario: Pocket ID admin API preferred over Chrome MCP

- **GIVEN** the Pocket ID DB has 1+ users (warm state, not bootstrap)
- **WHEN** the IaC needs to create a new OIDC client (e.g. for the `komodo` client)
- **THEN** the IaC MUST use `POST /api/oidc/clients` (the admin API)
- **AND** the IaC MUST NOT use Chrome MCP
- **AND** the IaC MUST NOT require an operator click-through

### Requirement: Komodo Periphery + Newt provisioned via IaC SDK + Integrations API

The system SHALL provide 2 IaC commands for provisioning the agent
infrastructure on a managed host (bunchloch or arm1-oci):

1. **`bun run iac:deploy-periphery`** — uses the `komodo_client` (via
   `iac/clients/komodo-client.ts`) to:
   - Call `CreateOnboardingKey` to get a one-time-use onboarding key
   - Call `CreateServer` with `address: ""` (outbound mode) + `connect_as: <hostname>`
   - Render the Periphery `core.config.toml` with the onboarding key + the
     Core address (from `KOMODO_URL` env)
   - Generate the `docker-compose.yaml` for the Periphery stack
   - Write both files to `/etc/komodo/` (or a configurable path)
   - Emit a JSON audit record

2. **`bun run iac:deploy-newt`** — uses the Pangolin Integrations API
   (via `iac/clients/pangolin-client.ts`) to:
   - Call `pick-site-defaults` to get newtId + newtSecret + clientAddress
   - Call `CreateSite` (or `UpdateSite` if it already exists) with `type: "newt"`
   - Write `PANGOLIN_NEWT_<HOST>_ID` + `PANGOLIN_NEWT_<HOST>_SECRET` to local `~/.env`
   - Write the same to Infisical (so Locket sidecars can fetch them)
   - Render the Newt `docker-compose.yaml` with the locket sidecar
   - Emit a JSON audit record

Both commands MUST be idempotent (re-running on a host that already
has a Periphery/Newt connection is a no-op + emits a "skipped" audit entry).

#### Scenario: deploy Periphery on bunchloch

- **GIVEN** the Komodo Core is running on arm1-oci (or bunchloch for local dev)
- **AND** the bons IaC has a valid `KOMODO_JWT` in env (obtained via the bootstrap)
- **WHEN** `bun run iac:deploy-periphery --connect-as=bunchloch` runs
- **THEN** the IaC calls Komodo's `CreateOnboardingKey` API → gets the onboarding key
- **AND** the IaC calls Komodo's `CreateServer` API with `name: "bunchloch"` + `address: ""`
- **AND** the IaC writes `/etc/komodo/periphery.config.toml` + `/etc/komodo/docker-compose.yaml`
- **AND** the operator can run `docker compose up -d` to start the Periphery
- **AND** the Periphery connects outbound to Komodo Core (verified via the Core's UI)

#### Scenario: deploy Newt on bunchloch

- **GIVEN** Pangolin Core is running on arm1-oci
- **AND** the bons IaC has a valid `PANGOLIN_API_KEY` in env
- **WHEN** `bun run iac:deploy-newt --host=bunchloch` runs
- **THEN** the IaC calls Pangolin's `pick-site-defaults` → gets newtId + newtSecret
- **AND** the IaC calls Pangolin's `CreateSite` with `type: "newt"` + the newtId/secret
- **AND** the IaC writes `PANGOLIN_NEWT_BUNCHLOCH_ID` + `..._SECRET` to local `~/.env`
- **AND** the IaC writes the same to Infisical
- **AND** the operator can run `docker compose up -d` to start the Newt
- **AND** the Newt establishes a WireGuard tunnel to Pangolin Core (verified via the Pangolin UI)

## MODIFIED Requirements

### Requirement: iac:bootstrap orchestrates all 5 auth components as a single tightly-integrated system (now with control-plane bootstrap)

The system SHALL provide a `bun run iac:bootstrap` command that
orchestrates all 5 auth components (Pulumi → Infisical → Pocket ID →
Pangolin → Komodo → Tinyauth → Newt → sync) as a single, idempotent
end-to-end flow. Each phase MUST check the current state and
(re)deploy as needed.

The orchestrator MUST auto-invoke `iac:bootstrap-control-plane` at
Phase 1 (replacing the prior TODO). The control-plane bootstrap handles:
Pulumi VM provisioning → Infisical first-admin → Pocket ID OIDC bootstrap
→ Komodo + Pangolin + Tinyauth deploy → Komodo Periphery + Newt deploy
→ 6-way health verify. This is the single end-to-end reproducible
flow that the operator runs to bootstrap a fresh arm1-oci.

The system SHALL also provide `iac:health` that does a 7-way check
(komodo + pangolin + infisical + newt + pocket-id + tinyauth +
machine-identities-seeded). Each check SHALL report a clear actionable
error message.

#### Scenario: iac:bootstrap runs end-to-end on cold-boot (updated order with control-plane bootstrap)

- **WHEN** the bons host has nothing running (no Infisical, no Pocket ID, no Komodo, no Pangolin, no Tinyauth)
- **THEN** `iac:bootstrap` orchestrates all 10 phases in order:
  1. **Pulumi IaC** (calls `iac:bootstrap-pulumi-oci` — replaces the prior TODO)
  2. **Infisical secrets** (mount the `dev-baile` project into the local filesystem)
  2.5. **Infisical bootstrap** (invokes `iac:bootstrap-infisical` which does the first-admin via admin API / Chrome MCP fallback + seeds all 8 machine identities)
  2.75. **Pocket ID OIDC wire** (invokes `iac:wire-pocketid-as-oidc` to wire Pocket ID as OIDC IdP for Komodo + Pangolin)
  3. **bundled stack deploy** (invokes `iac:bootstrap-control-plane` which deploys `stacks/control-plane/` on either bunchloch or arm1-oci)
  4. Komodo Core + Periphery (now managed by Komodo's stack runner via the bundled stack deploy)
  5. Pangolin private resources (now managed via the Pangolin Integrations API)
  6. Tinyauth deploy + health check
  7. Newt (sync-sites)
  8. All sync commands
- **AND** the bootstrap is idempotent: re-running on a warm cluster skips the already-done phases
- **AND** the operator only has to run `bun run iac:bootstrap` (single command, end-to-end)

## REMOVED Requirements

### Requirement: iac:bootstrap Phase 1 (Pulumi) is a TODO (REMOVED)

**Reason**: The previous Phase 1 was a placeholder `// Pulumi (Future: ...)` comment. Replaced by the actual Pulumi IaC call wired into Phase 1, which delegates to `iac:bootstrap-control-plane` for the operator's one-shot.

**Migration**: Any code that was waiting for Phase 1 to be implemented is now satisfied. The Pulumi IaC scripts (`iac/pulumi/oci/deploy.ts` + `setup.ts`) are still present but now called by the new orchestrator.
