# Tasks for IaC-ify the arm1-oci Control Plane

## 1. OpenSpec change (cianfhoghlaim repo)

- [ ] **1.1** Create `openspec/changes/2026-07-15-iac-ify-arm1-oci-control-plane-v1/proposal.md` (with `## Dependencies` + `## Cross-repo sync` sections)
- [ ] **1.2** Create `openspec/changes/2026-07-15-iac-ify-arm1-oci-control-plane-v1/tasks.md` (this file)
- [ ] **1.3** Create `openspec/changes/2026-07-15-iac-ify-arm1-oci-control-plane-v1/specs/agent-platform-cluster/spec.md` (delta: adds the control-plane bootstrap flow)
- [ ] **1.4** Create `openspec/changes/2026-07-15-iac-ify-arm1-oci-control-plane-v1/specs/infrastructure-stacks/spec.md` (delta: adds the 6-file control-plane stack)
- [ ] **1.5** Create `openspec/changes/2026-07-15-iac-ify-arm1-oci-control-plane-v1/cross-repo-sync.md` (commit order: cianfhoghlaim first, then bonneagar)
- [ ] **1.6** Validate with `openspec validate 2026-07-15-iac-ify-arm1-oci-control-plane-v1 --strict` (must pass before commit)
- [ ] **1.7** Commit + push to `cianfhoghlaim/main`

## 2. Phase 1: Pulumi IaC migration + iac:bootstrap wiring (5 files)

- [ ] **2.1** Update `iac/pulumi/oci/setup.ts` — replace `import { InfisicalSDK } from "@infisical/sdk"` with `import * as infisical from "../clients/infisical-rest.ts"`; update all `client.secrets().createSecret(...)` / `client.secrets().updateSecret(...)` calls to use the direct REST helpers
- [ ] **2.2** Update `iac/pulumi/oci/deploy.ts` — same migration; update the `getInfisicalClient()` function to return the bons IaC's REST client
- [ ] **2.3** Update `iac/commands/bootstrap.ts` — replace `// (Future: import { deploy as pulumiDeploy } from '../../pulumi/oci/deploy.ts'; await pulumiDeploy();)` with the actual call (Pulumi IaC runs FIRST, before anything else)
- [ ] **2.4** Add the Pulumi IaC to the cross-cutting prereq order in `komodo/resource-syncs/cross-cutting.toml` (position 0 — runs first, before `pangolin-first`)
- [ ] **2.5** Verify all changes compile (`bun build iac/cli.ts --target=bun`)

## 3. Phase 2: iac:bootstrap-locket-binary (2 files)

- [ ] **3.1** Create `iac/commands/bootstrap-locket-binary.ts` — downloads the locket Rust binary to `~/.local/bin/locket` (or `locket:infisical` Docker image for the IaC's own use); verifies it works (`locket --version`)
- [ ] **3.2** Register the new command in `iac/cli.ts` + add the `iac:bootstrap-locket-binary` bun script to `iac/package.json`

## 4. Phase 3: ia/docs/locket.md (1 file)

- [ ] **4.1** Create `iac/docs/locket.md` — port the provider patterns from `/stedding/locket/README.md` + `docs/providers/infisical.md`. Document:
  - The 5 supported providers (1password Connect, BWS, Infisical, OpenBao/Vault, 1password Service Accounts)
  - The Infisical provider setup (Machine Identity + Universal Auth + Client Secret)
  - The Infisical URI syntax (`infisical:///SECRET?env=dev&path=/folder&project_id=...`)
  - The 3 sidecar modes (`watch`, `exec`, `one-shot`)
  - The sidecar docker-compose pattern (mount `templates:/templates:ro` + `out:/run/secrets/locket` + `--map /templates:/run/secrets/locket`)

## 5. Phase 3: stacks/control-plane/ (7 files, the bundled stack)

- [ ] **5.1** Create `stacks/control-plane/compose.yaml` — 7 services (komodo-core, komodo-ferretdb, komodo-postgres, pangolin-core, pocket-id, tinyauth, infisical) + 3 data store services (infisical-db, infisical-redis) + 1 traefik + 5 locket sidecars. Use the 6-file GOLD_STANDARD pattern.
- [ ] **5.2** Create `stacks/control-plane/sidecar.yaml` — the locket.toml config (Infisical provider, watch mode, project_id from env, env from env)
- [ ] **5.3** Create `stacks/control-plane/secrets.env` — `{{ infisical:///... }}` refs for each service's secrets (Pangolin signing_key, Pocket ID encryption_key, Komodo DB url, Infisical encryption_key, Tinyauth Pocket ID client_id/secret)
- [ ] **5.4** Create `stacks/control-plane/pangolin.yaml` — Traefik routes for `komodo.`, `auth.`, `infisical.`, `tinyauth.`, `pocket-id.` (6-label pattern with `mode`, `full-domain`, `destination-port`, `protocol`, `roles[0]`)
- [ ] **5.5** Create `stacks/control-plane/blueprint.yaml` — Komodo Resource Sync manifest (`name`, `repo`, `branch`, `resource_path`, `managed`, `delete`, `interval`)
- [ ] **5.6** Create `stacks/control-plane/.env.example` — bootstrap-mode env vars (Infisical ENCRYPTION_KEY + DB creds, OIDC config placeholders)
- [ ] **5.7** Create `stacks/control-plane/README.md` — operator handoff (the 2 phases of bootstrap, the 7-way health check, the troubleshooting guide)

## 6. Phase 4: iac:wire-pocketid-as-oidc (2 files)

- [ ] **6.1** Create `iac/commands/wire-pocketid-as-oidc.ts` — the post-bootstrap OIDC wiring command that:
  1. Uses `iac/clients/pocketid-rest.ts` (or the existing `iac/clients/infisical-client.ts`) to create the `komodo` OIDC client in Pocket ID with `redirect_uri: https://komodo.<DOMAIN>/auth/oidc/callback` and `grant_types: ["authorization_code"]`
  2. Uses `iac/clients/komodo-client.ts` to write the new Pocket ID client_id + secret to Komodo's `oidc_client_id` + `oidc_client_secret` config (via the Komodo REST API)
  3. Uses `iac/clients/pangolin-client.ts` to add Pocket ID as a Pangolin Identity Provider (via `POST /org/{orgId}/identity-provider`)
  4. Writes the 3 client_id/client_secret pairs to `.env` for the operator to inspect
  5. Audit record to `/tmp/oidc-wiring-{ts}.json`
- [ ] **6.2** Add the `--api-only` flag to `iac/commands/bootstrap-pocketid-admin.ts` that prefers the admin API (`POST /api/v1/users`) over Chrome MCP when 1+ users exist (Q4 implementation)

## 7. Phase 5: iac:deploy-periphery + iac:deploy-newt (2 files)

- [ ] **7.1** Create `iac/commands/deploy-periphery.ts` — the agent-on-managed-host command that:
  1. Uses `iac/clients/komodo-client.ts` to call `CreateOnboardingKey` → get the onboarding key
  2. Calls `CreateServer` with `address: ""` (outbound mode) and `connect_as: <hostname>`
  3. Renders the Periphery `core.config.toml` with the onboarding key + the core address (from `KOMODO_URL` env)
  4. Generates the `docker-compose.yaml` for the Periphery stack (with the bons IaC's standard Periphery image + a locket sidecar)
  5. Writes both files to the local `/etc/komodo/` directory (or a configurable path)
  6. Returns the compose path + the onboarding key for the operator to verify
  7. Audit record to `/tmp/periphery-deploy-{ts}.json`
- [ ] **7.2** Create `iac/commands/deploy-newt.ts` — the tunnel-on-managed-host command that:
  1. Uses `iac/clients/pangolin-client.ts` to call `pick-site-defaults` → get newtId + newtSecret
  2. Calls `CreateSite` (or `UpdateSite` if it already exists) with `type: "newt"` + the newtId/secret
  3. Writes `PANGOLIN_NEWT_<HOST>_ID` + `PANGOLIN_NEWT_<HOST>_SECRET` to `.env`
  4. Writes the same to Infisical (so Locket sidecars can fetch them)
  5. Renders the Newt `docker-compose.yaml` with the locket sidecar + the newtId/secret
  6. Returns the compose path for the operator to verify

## 8. Phase 6: iac:bootstrap-control-plane (1 file, the operator one-shot)

- [ ] **8.1** Create `iac/commands/bootstrap-control-plane.ts` — the single entrypoint that runs all 8 phases in order:
  1. `iac:bootstrap-locket-binary` — installs locket locally
  2. `iac:bootstrap-pulumi-oci` — provisions the VM via Pulumi (no-op for bunchloch target)
  3. `iac:deploy-control-plane-<host>` — deploys the bundled stack (via `docker compose up -d` on bunchloch; via `km run procedure deploy-control-plane-arm1-oci` on arm1-oci)
  4. `iac:bootstrap-infisical` — first admin + 8 machine identities (API-preferred, Chrome-MCP-fallback)
  5. `iac:wire-pocketid-as-oidc` — OIDC wiring for Komodo + Pangolin
  6. `iac:deploy-periphery-<host>` — Periphery on the managed host
  7. `iac:deploy-newt-<host>` — Newt tunnel on the managed host
  8. `iac:health` — verify 6-way health (komodo + pangolin + infisical + newt + pocket-id + tinyauth)
- [ ] **8.2** Register the new command in `iac/cli.ts` + add the `iac:bootstrap-control-plane` bun script to `iac/package.json`
- [ ] **8.3** Add 2 sub-scripts to `iac/package.json`:
  - `iac:bootstrap-control-plane-bunchloch` (calls `iac:bootstrap-control-plane --target=bunchloch`)
  - `iac:bootstrap-control-plane-arm1-oci` (calls `iac:bootstrap-control-plane --target=arm1-oci`)

## 9. Phase 7: GitOps + openspec archive (4 steps)

- [ ] **9.1** Commit all bons IaC changes (the 15+ files from phases 2-8) on the current bons worktree
- [ ] **9.2** Push to `archive-bonneagar` remote on the bons standalone repo's `pick-5b-bonneagar-v5-continuation` branch
- [ ] **9.3** Open a new PR (or update PR #7) on `github.com/cianfhoghlaim/bonneagar` with the new commits
- [ ] **9.4** After the bons PR merges + the operator verifies the deploy, archive the openspec change: `openspec archive 2026-07-15-iac-ify-arm1-oci-control-plane-v1 --yes`

## 10. End-to-end test (post-merge)

- [ ] **10.1** On a clean `bunchloch`, run `bun run iac:bootstrap-control-plane-bunchloch` — verify all 8 phases succeed
- [ ] **10.2** Verify the 6-way health: `bun run iac:health` — all 6 surfaces should report `✓`
- [ ] **10.3** Open `https://komodo.cianfhoghlaim.ie` in a browser — Pocket ID OIDC login flow should work end-to-end
- [ ] **10.4** Open `https://auth.cianfhoghlaim.ie` — passkey login should work
- [ ] **10.5** On a clean `arm1-oci` (after Pulumi provisions the VM), run `bun run iac:bootstrap-control-plane-arm1-oci` — verify all 8 phases succeed on the new VM
