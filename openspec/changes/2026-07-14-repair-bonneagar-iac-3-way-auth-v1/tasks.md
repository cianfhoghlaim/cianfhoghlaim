# Tasks: 2026-07-14-repair-bonneagar-iac-3-way-auth-v1

## Phase 0 — Read baseline

- [x] Read `iac/auth.ts` to confirm the TODO at line 36
- [x] Read `iac/config.ts` to see what env vars are expected
- [x] Read `iac/clients/pangolin-client.ts` to see the API call pattern
- [x] Read `PANGOLIN-SETUP.md` in bonneagar to understand the manual setup procedure

## Phase 1 — Bonneagar code changes (DONE in this session)

- [x] **Discover** the Pocket ID OIDC discovery URL → `https://auth.cianfhoghlaim.ie/.well-known/openid-configuration` (returns 200, supports `client_credentials` grant + `client_secret_post` auth method)
- [x] Create `iac/auth-pocketid.ts` (~250 LOC) — 4 exported functions:
  - `discoverPocketId()` — OIDC discovery with caching
  - `pocketIdClientCredentials()` — Step 1: mint Pocket ID access_token
  - `exchangePocketIdForPangolinSession()` — Step 2: JWT → session cookie (tries 4 endpoint variants for backwards compat)
  - `mintPangolinApiKey()` — Step 3: PUT `/v1/org/{orgId}/api-key`
  - `pocketIdLogin()` — composes the 3 steps into 1 call
- [x] Create `iac/commands/rotate-auth.ts` (~240 LOC) — 1 exported function:
  - `rotateAuth()` — the one-shot 3-way credential rotation
  - Direct REST calls to Infisical (bypasses the broken `@infisical/sdk` v5 wrapper)
  - Emits JSON audit record to `/tmp/auth-rotation-{ts}.json`
- [x] Edit `iac/auth.ts` to wire `pocketIdLogin()` into `ensurePangolinAuth()` as the 2nd-tier fallback
- [x] Edit `iac/cli.ts` to add `rotate-auth` case to the dispatcher
- [x] Edit `package.json` to add `iac:rotate-auth` script
- [x] **Smoke-test the imports**: `bun -e "import('./iac/auth-pocketid.ts')"` returns the 5 exported functions
- [x] **Smoke-test the OIDC discovery**: `discoverPocketId()` returns the correct metadata
- [x] **Smoke-test the client_credentials call**: `pocketIdClientCredentials()` reaches Pocket ID (returns 404 "Client not found" for test creds — confirms the path is correct)

## Phase 2 — Openspec change (DONE this session)

- [x] Write `proposal.md`
- [x] Write `cross-repo-sync.md`
- [x] Write `tasks.md` (this file)
- [x] Write `specs/agent-platform-cluster/spec.md` with 1 ADDED Requirement:
  - `### Requirement: iac:rotate-auth mints fresh Pangolin + Komodo + Infisical credentials via Pocket ID OIDC`
  - 3 Scenarios: rotation succeeds, rotation fails, rotated credentials used by iac:sync:sites

## Phase 3 — Validate + commit + push (DONE this session)

- [x] `openspec validate 2026-07-14-repair-bonneagar-iac-3-way-auth-v1 --strict` returns 0
- [x] Commit on `pick-5b-bonneagar-v5-continuation` (commit `de9efbe7f`)
- [x] Push bonneagar branch
- [ ] Commit on `pick-4-biep-v1` (next step)
- [ ] Push cianfhoghlaim branch

## Phase 4 — Archive

- [ ] `openspec archive 2026-07-14-repair-bonneagar-iac-3-way-auth-v1 --yes` (after operator completes manual Pocket ID OIDC client setup)

## Phase 5 — Manual operator setup (required to fully activate)

> **This phase CANNOT be automated** — it requires browser-based access to Pocket ID.

- [ ] Log in to `https://auth.cianfhoghlaim.ie` (Pocket ID, via WebAuthn passkey)
- [ ] Settings → OIDC Clients → Create
- [ ] Name: `bons-iac`, redirect URI: `https://pangolin.cianfhoghlaim.ie`, grant type: `client_credentials`
- [ ] Save the returned `client_id` + `client_secret` to `~/.env`:
  ```bash
  POCKETID_CLIENT_ID=<client-id>
  POCKETID_CLIENT_SECRET=<client-secret>
  ```
- [ ] Run `bun run iac:rotate-auth` to verify the full flow
- [ ] Confirm `bun run iac:health` exits 0 (the 4-way check passes — komodo + pangolin + infisical + newt)

## Phase 6 — End-to-end smoke-test (after Phase 5 completes)

- [ ] `bun run iac:health` returns: 4 surfaces healthy
- [ ] `bun run iac:plan` discovers 18 services + 1 newt site
- [ ] `bun run iac:sync:sites` provisions the bunchloch-newt site
- [ ] `km run procedure deploy-newt-bunchloch-v2` succeeds end-to-end
- [ ] `km run procedure deploy-pangolin-newt-arm1-oci` succeeds end-to-end
- [ ] `curl https://hermes.cianfhoghlaim.ie/api/health` returns 200

