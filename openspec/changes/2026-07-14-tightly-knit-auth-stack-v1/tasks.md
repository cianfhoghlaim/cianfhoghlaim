# Tasks: 2026-07-14-tightly-knit-auth-stack-v1

## Phase 0 — Discover Pocket ID state (immediate fix for the user's passkey issue)

- [x] Verify Pocket ID is reachable (HTTPS + OIDC discovery)
- [x] Inspect Pocket ID DB state (users = 0; DB was wiped)
- [x] Confirm the canonical Pocket ID URL is `auth.cianfhoghlaim.ie` (not `pocketid.`)
- [x] Identify that the bons `.env` has stale credential entries (`POCKETID_CLIENT_ID="tinyauth"`, etc.) that don't exist in the DB
- [x] Document the operator's manual bootstrap path (open the URL in a browser)

## Phase 1 — Extend iac/auth-pocketid.ts with 7 admin API functions

- [x] Add `pocketIdAdminLogin(username, password)` → session cookie
- [x] Add `pocketIdHealth()` → {healthy, dbUsers, dbOidcClients, version, signupEnabled}
- [x] Add `pocketIdSetSignupEnabled(adminCookie, enabled)`
- [x] Add `pocketIdCreateSignupToken(adminCookie, opts)`
- [x] Add `pocketIdListOidcClients(adminCookie)` + `pocketIdGetOidcClient(adminCookie, id)`
- [x] Add `pocketIdCreateOidcClient(adminCookie, opts)` (returns clientSecret only on create)
- [x] Add `pocketIdListUsers(adminCookie)`
- [x] Add `pocketIdRotateSigningKey(adminCookie)`
- [x] Add the `iac:bootstrap-pocketid-admin` command (~230 LOC) — orchestrates the full operator flow
- [x] Wire into iac:cli.ts + package.json (`iac:bootstrap-pocketid-admin` script)
- [x] Wire `ensureBonsIacClient` into iac:rotate-auth (so the bons-iac OIDC client is created/verified on every credential rotation)
- [x] Smoke-test: all modules import + `pocketIdHealth()` returns in 320ms

## Phase 2 — Restructure iac:bootstrap into 9 phases (Pocket ID + Tinyauth integrated)

- [x] Phase 1: Pulumi (TODO)
- [x] Phase 2: Infisical secrets
- [x] Phase 3: Pocket ID (NEW — health check + bootstrap warning if empty)
- [x] Phase 4: Cross-system auth wiring (Pocket ID → Pangolin → Komodo → Infisical)
- [x] Phase 5: Pangolin private resources
- [x] Phase 6: Komodo Core + Periphery
- [x] Phase 7: Tinyauth (NEW)
- [x] Phase 8: Newt (sync-sites)
- [x] Phase 9: All sync commands

## Phase 3 — Extend iac:health to 6-way check

- [x] Add the Pocket ID probe (with 3s timeout on docker exec; 320ms in practice)
- [x] Add the Tinyauth probe (HTTP GET to `tinyauth.cianfhoghlaim.ie/api/health`)
- [x] Update the header text: "Health check (5-way: komodo + pangolin + infisical + newt + pocket-id + tinyauth)"
- [x] Update the early-exit text + add a note for the bootstrap case
- [x] Smoke-test: all 6 probes run + report clear actionable errors

## Phase 4 — Fix Tinyauth (the crash loop)

- [x] Identify the root cause: Tinyauth v4 entrypoint sources `/run/secrets/locket/secrets.env`; without Locket sidecar, this file is empty → crash loop
- [x] Stop the crash-looping Tinyauth container
- [x] Create `bonneagar/stacks/tinyauth/` with the 6-file GOLD_STANDARD + README:
  - [x] `compose.yaml` (Tinyauth v4 + Locket sidecar, 2 services)
  - [x] `sidecar.yaml` (Locket Infisical provider overlay: `INFISICAL_SECRET_PATH=/tinyauth` + the 2 keys to materialize)
  - [x] `secrets.env` (Locket `{{ infisical:/// }}` references for `PROVIDERS_POCKETID_CLIENT_ID` + `PROVIDERS_POCKETID_CLIENT_SECRET`)
  - [x] `pangolin.yaml` (private resource: `https://tinyauth.cianfhoghlaim.ie` + the OIDC callback sub-route)
  - [x] `blueprint.yaml` (bulk import format for the Pangolin Integrations API)
  - [x] `.env.example` (local dev defaults)
  - [x] `README.md` (operator runbook)

## Phase 5 — Create 3 new Komodo procedures

- [x] `komodo/procedures/deploy-pocket-id-bunchloch.toml` (5 stages)
- [x] `komodo/procedures/deploy-tinyauth-bunchloch.toml` (5 stages; fixes the crash loop)
- [x] `komodo/procedures/deploy-pocket-id-arm1-oci.toml` (5 stages; for the migration target)
- [x] `komodo/stacks/pocket-id-bunchloch.toml` (hand-curated; the runtime config)
- [x] `komodo/stacks/tinyauth-bunchloch.toml` (hand-curated; the runtime config)

## Phase 6 — Wire Pocket ID + Tinyauth into the cross-cutting prereq order

- [x] Edit `komodo/resource-syncs/cross-cutting.toml` (add the 3 new procedures to the resource_path list)
- [x] Update the comment block (the 4-stage ordering → 9-stage ordering)
- [x] Update the "Server_id convention" comment to mention 9 procedures (was 4)
- [x] Edit `komodo/procedures/server_id_legend.md` (add the 3 new procedures to their respective host sections)

## Phase 7 — Create the openspec change

- [x] Write `proposal.md` (this change; the operator handoff is clear)
- [x] Write `cross-repo-sync.md`
- [x] Write `tasks.md` (this file)
- [x] Write `specs/agent-platform-cluster/spec.md` with 1 ADDED Requirement
- [x] Write `specs/infrastructure-stacks/spec.md` with 1 ADDED Requirement
- [ ] `openspec validate 2026-07-14-tightly-knit-auth-stack-v1 --strict` returns 0 (next step)

## Phase 8 — Commit + push + smoke-test + update audit log

- [ ] Commit on `pick-5b-bonneagar-v5-continuation` (the IaC code + 3 new procedures + Tinyauth stack)
- [ ] Push bonneagar branch
- [ ] Commit on `pick-4-biep-v1` (the openspec change)
- [ ] Push cianfhoghlaim branch
- [ ] `openspec archive 2026-07-14-tightly-knit-auth-stack-v1 --yes`
- [ ] Update `<root>/.audit.local.md` §6 with the new improvements
- [ ] Update `<root>/.audit.local.md` §7 with the operator handoff (the next-session handoff must clearly say "operator needs to do the browser bootstrap")

## Phase 9 — Operator smoke-test (after the operator does the browser bootstrap)

- [ ] Operator runs: `POCKETID_ADMIN_PASSWORD=<password> bun run iac:bootstrap-pocketid-admin`
- [ ] Operator opens the printed URL in a browser + registers Touch ID passkey
- [ ] `bun run iac:health` exits 0 with all 6 surfaces healthy
- [ ] `km run procedure deploy-tinyauth-bunchloch` succeeds (Tinyauth is now properly deployed with Locket)
- [ ] `curl https://tinyauth.cianfhoghlaim.ie/api/health` returns 200
- [ ] `curl https://auth.cianfhoghlaim.ie/.well-known/openid-configuration` returns the OIDC discovery (unchanged)
- [ ] `bun run iac:plan` reports 0 diffs (no drift)

## Phase 10 — Arm1-oci migration (follow-up session)

- [ ] SSH to arm1-oci, checkout pick-5b-bonneagar-v5-continuation
- [ ] Run `km run procedure deploy-pocket-id-arm1-oci` (the new procedure)
- [ ] Run `km run procedure deploy-tinyauth-bunchloch` (Tinyauth is host-agnostic)
- [ ] Update bons `.env` for arm1-oci (POCKETID_ENCRYPTION_KEY differs per host)
- [ ] Verify `bun run iac:health` from arm1-oci (cross-host probe; both hosts are now pocket-id providers behind the same URL)
