# Tasks for IaC-ify the Infisical Stack

## 1. Fix the Infisical client (bons IaC)

- [ ] **1.1** Rewrite `iac/clients/infisical-client.ts` to use direct REST calls instead of `@infisical/sdk`. Remove the SDK dependency from `iac/models/infisical.ts` types if any.
- [ ] **1.2** Add `iac/clients/infisical-rest.ts` with 4 helper functions: `infisicalLogin()`, `infisicalListProjects()`, `infisicalListMachineIdentities()`, `infisicalCreateMachineIdentity()`. All use form-encoded body for login, Bearer token for everything else.
- [ ] **1.3** Add URL fallback chain: env `INFISICAL_URL` → `http://localhost:8081` (dev) → `https://infisical.cianfhoghlaim.ie` (prod).
- [ ] **1.4** Update `package.json` to remove `@infisical/sdk` from dependencies (if it's only used by the IaC and not by anything else — verify first).
- [ ] **1.5** Verify `bun run iac/cli.ts health` still compiles.

## 2. Create `iac:bootstrap-infisical` command

- [ ] **2.1** Create `iac/commands/bootstrap-infisical.ts` with the structure mirror of `bootstrap-pocketid-admin.ts`:
  - Detect first-admin-vs-existing
  - If first admin: use Chrome MCP to drive the `/signup/setup` wizard (form-fill email + password + click submit + handle 2FA if needed)
  - After admin login: create machine identity `bons-iac` with Admin role via API
  - Save machine identity client_id + client_secret to `.env`
- [ ] **2.2** Add the machine identity creation step (idempotent — checks if exists first).
- [ ] **2.3** Add to `iac/cli.ts` as a new command + add the script to `package.json`.
- [ ] **2.4** Verify `bun run iac:bootstrap-infisical --help` shows usage + dry-run flag.

## 3. Create `deploy-infisical-arm1-oci` Komodo procedure

- [ ] **3.1** Create `komodo/procedures/deploy-infisical-arm1-oci.toml` with 6 stages:
  1. **preflight**: `HttpCheck` against `https://infisical.cianfhoghlaim.ie/api/status` (should 404 initially — that's the expected state, means Infisical isn't deployed yet)
  2. **image-pullable**: `docker manifest inspect infisical/infisical:latest`
  3. **stack-deploy**: `cd /etc/komodo/infisical && docker compose up -d`
  4. **health**: poll `/api/status` until 200 (max 90s)
  5. **bootstrap**: `cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar && bun run iac:bootstrap-infisical` (the IaC does the admin + machine identity work)
  6. **audit**: write JSON to `/tmp/infisical-bootstrap-{ts}.json` with image, version, oidc_issuer, etc.
- [ ] **3.2** Verify TOML parses with `komodo parse-config` or a similar dry-run tool.

## 4. Rewrite `infisical-first` Komodo procedure

- [ ] **4.1** Remove the `ssh arm1-oci` step entirely.
- [ ] **4.2** Replace with HTTP-based checks (no SSH):
  - `HttpCheck` against `https://infisical.cianfhoghlaim.ie/api/status`
  - `HttpCheck` against the dev-baile project via `/api/v3/projects/{id}` with the bons-iac machine identity token
  - `HttpCheck` that each of the 8 required machine identities exist (`bons-iac`, `pocket-id`, `komodo`, `pangolin`, `tinyauth`, `openclaw`, `openchamber`, `hermes`)
- [ ] **4.3** Set `server_id = "arm1-oci"` (already is).

## 5. Update `komodo/resource-syncs/cross-cutting.toml`

- [ ] **5.1** Update the procedure list comment from "9 cross-host prerequisite procedures" to "10" (add `deploy-infisical-arm1-oci`).
- [ ] **5.2** Add `deploy-infisical-arm1-oci` to the deploy order (position 4, after `locket-deploy` since Locket needs Infisical already alive).
- [ ] **5.3** Fix the outdated "4 procedures" wording at the top of the file.

## 6. Update `iac:rotate-auth` to use the fixed Infisical client

- [ ] **6.1** Replace the inline `fetchInfisicalSecret` function in `iac/commands/rotate-auth.ts` with a call to the new `iac/clients/infisical-rest.ts`.
- [ ] **6.2** Verify `bun run iac:rotate-auth` succeeds end-to-end (after the Infisical bootstrap has been run).

## 7. Update `iac:health` to query Infisical via API

- [ ] **7.1** Update the Infisical check in `iac/commands/health.ts` to use the API (`/api/status`) not just `docker exec`. If the API returns 200 + version info, report it as healthy. If `INFISICAL_API_KEY` is in env, also verify machine identities are seeded.

## 8. Wire Komodo + Pangolin to use Infisical (the part that was missing)

- [ ] **8.1** Update `stacks/komodo/secrets.env` to use `infisical://dev-baile/komodo/password` instead of hardcoded.
- [ ] **8.2** Update `stacks/pangolin/secrets.env` to add `PANGOLIN_API_KEY=infisical://dev-baile/pangolin/api_key`.
- [ ] **8.3** Verify `stack-doctor` passes on both stacks.

## 9. OpenSpec + GitOps

- [ ] **9.1** Create `openspec/changes/2026-07-12-iac-ify-infisical-bootstrap-v1/specs/agent-platform-cluster/spec.md` (delta from current).
- [ ] **9.2** Create `openspec/changes/2026-07-12-iac-ify-infisical-bootstrap-v1/specs/infrastructure-stacks/spec.md` (delta from current).
- [ ] **9.3** Commit everything + push to `bonneagar/pick-5b-bonneagar-v5-continuation`.
- [ ] **9.4** Update the existing PR #7 description with the new commits.

## 10. End-to-end test (post-merge)

- [ ] **10.1** Run `km run procedure deploy-infisical-arm1-oci` against a fresh arm1-oci.
- [ ] **10.2** Verify Chrome MCP drives the `/signup/setup` wizard and creates the first admin.
- [ ] **10.3** Verify the bons-iac machine identity is created + creds are in `.env`.
- [ ] **10.4** Verify `km run procedure infisical-first` passes (no more SSH step).
- [ ] **10.5** Verify `bun run iac:health` shows `✓ infisical`.
- [ ] **10.6** Verify `bun run iac:rotate-auth` succeeds for all 3 surfaces.

