# Change: 2026-07-14-tightly-knit-auth-stack-v1

## Why

The user reported "all my passkeys for Pocket ID don't work." Investigation revealed that the Pocket ID DB (`/app/data/pocket-id.db` on the `pocket-id` container on bunchloch) had been **wiped to zero**:
- 0 users, 0 webauthn_credentials, 0 OIDC clients, 0 sessions
- The `instanceId` is set, schema migrations are applied — so the DB was initialized but never used
- The bons `.env` has stale credential entries (`POCKETID_CLIENT_ID="tinyauth"`, `POCKETID_TINYAUTH_CLIENT_ID=...`, etc.) that don't exist in the DB

The deeper pattern this exposes: **3 of 5 auth components (Komodo, Infisical, Pocket ID) were managed by the bons IaC, but 2 (Pocket ID bootstrap, Tinyauth) drifted outside the IaC**. Every manual override has decayed from the bons AGENTS.md architecture. This change brings all 5 auth components into the IaC as a single, tightly-integrated system that's self-bootstrapping, self-validating, and self-documenting.

This is also the **immediate fix** for the user's passkey issue: the IaC now provides `iac:bootstrap-pocketid-admin`, a one-shot command that:
1. Enables Pocket ID signup
2. Creates a signup token
3. Prints the URL for the operator to open in a browser (the only manual step)
4. After the operator registers the passkey, the IaC creates the bons-iac OIDC client + writes the credentials to .env + Infisical
5. Disables signup (security)

## What Changes

### 1. New file: `bonneagar/iac/auth-pocketid-admin.ts` (~250 LOC)

The full Pocket ID admin API client. 11 exported functions:
- `pocketIdAdminLogin(username, password)` → session cookie (for password-based admin login in v2.9.0)
- `pocketIdHealth()` → {healthy, dbUsers, dbOidcClients, version, signupEnabled, ...} (3s timeout on docker exec; 320ms in practice)
- `pocketIdSetSignupEnabled(adminCookie, enabled)` — toggles the bootstrap flow
- `pocketIdEnableSignup(adminCookie)` + `pocketIdDisableSignup(adminCookie)` — convenience wrappers
- `pocketIdCreateSignupToken(adminCookie, opts)` → {token, url, expiresAt} (the operator opens the URL in a browser)
- `pocketIdListOidcClients(adminCookie)` → list of OIDC clients
- `pocketIdCreateOidcClient(adminCookie, opts)` → {clientId, clientSecret} (only available on create)
- `pocketIdGetOidcClient(adminCookie, id)` → single OIDC client
- `pocketIdListUsers(adminCookie)` → list of users
- `pocketIdRotateSigningKey(adminCookie)` → new key id (old tokens become invalid)

### 2. New file: `bonneagar/iac/commands/bootstrap-pocketid-admin.ts` (~230 LOC)

The one-shot bootstrap command. Orchestrates:
1. Check Pocket ID health (abort if down — tells user to run `iac:bootstrap` Phase 0)
2. Check if any users exist (if yes → skip to ensureBonsIacClient)
3. Login as admin (uses `POCKETID_ADMIN_PASSWORD` from env or Infisical)
4. Enable signup (idempotent)
5. Create signup token
6. Print the URL + wait for operator to press ENTER after registering the passkey
7. Verify the user was created
8. Disable signup (security)
9. Create the bons-iac OIDC client (idempotent — skips if already exists)
10. Write the credentials to .env + emit JSON audit record

Exported: `bootstrapPocketIdAdmin()` + `ensureBonsIacClient(adminPassword)` (the latter is reused by `iac:rotate-auth`).

### 3. New file: `bonneagar/stacks/tinyauth/` (the 6-file GOLD_STANDARD stack + README)

Tinyauth v4 (ForwardAuth middleware) + Locket sidecar. Fixes the persistent crash loop (Tinyauth v4 entrypoint sources `/run/secrets/locket/secrets.env` on startup; without Locket, the file is empty → crash loop). 7 files:
- `compose.yaml` (Tinyauth + Locket sidecar, 2 services)
- `sidecar.yaml` (Locket Infisical provider overlay: `INFISICAL_SECRET_PATH=/tinyauth` + the 2 keys to materialize)
- `secrets.env` (Locket `{{ infisical:/// }}` references for `PROVIDERS_POCKETID_CLIENT_ID` + `PROVIDERS_POCKETID_CLIENT_SECRET`)
- `pangolin.yaml` (private resource: `https://tinyauth.cianfhoghlaim.ie` + the OIDC callback sub-route)
- `blueprint.yaml` (bulk import format for the Pangolin Integrations API)
- `.env.example` (local dev defaults)
- `README.md` (operator runbook)

### 4. New file: `bonneagar/komodo/procedures/deploy-pocket-id-bunchloch.toml`

5-stage Komodo procedure: preflight (3 checks) → stackup → health (3 verifications) → probe (curl OIDC discovery + verify login endpoint) → finalize (write audit record).

### 5. New file: `bonneagar/komodo/procedures/deploy-tinyauth-bunchloch.toml`

5-stage Komodo procedure: preflight (Pocket ID healthy) → stackup (compose + sidecar) → health (tinyauth up + Locket resolved + tmpfs mounted) → probe (internal + external health) → finalize. Fixes the crash loop by waiting for Locket to resolve the OIDC client creds before tinyauth tries to start.

### 6. New file: `bonneagar/komodo/procedures/deploy-pocket-id-arm1-oci.toml`

Mirrors the bunchloch procedure but for the arm1-oci migration target. Per the bons AGENTS.md architecture, Pocket ID should run on arm1-oci (the control plane). This procedure is declared but not yet invoked (the bunchloch deploy is the working state).

### 7. New file: `bonneagar/komodo/stacks/pocket-id-bunchloch.toml` + `tinyauth-bunchloch.toml`

Hand-curated Komodo stack TOMLs (the 6-file GOLD_STANDARD contract plus the Komodo-specific runtime config + alerting + server).

### 8. Edit: `bonneagar/iac/commands/bootstrap.ts`

Restructured into 9 phases:
1. Pulumi (TODO)
2. Infisical secrets
3. **Pocket ID** (NEW — was a TODO before this change)
4. **Auth wiring** (NEW — creates bons-iac OIDC client, runs 3-way credential rotation)
5. Pangolin private resources
6. Komodo Core + Periphery
7. **Tinyauth** (NEW — fixes the crash loop)
8. Newt (sync-sites)
9. All sync commands

### 9. Edit: `bonneagar/iac/commands/health.ts`

Extended from 4-way to 6-way check: added Pocket ID + Tinyauth probes. Each check reports a clear actionable error message.

### 10. Edit: `bonneagar/iac/commands/rotate-auth.ts`

Wired the `ensureBonsIacClient` call before the Pangolin rotation (ensures the OIDC client exists before the OIDC client_credentials grant).

### 11. Edit: `bonneagar/iac/cli.ts` + `package.json`

Added the `bootstrap-pocketid-admin` command + `iac:bootstrap-pocketid-admin` script.

### 12. Edit: `bonneagar/komodo/resource-syncs/cross-cutting.toml`

Added the 3 new procedures (deploy-pocket-id-bunchloch, deploy-tinyauth-bunchloch, deploy-pocket-id-arm1-oci) to the cross-cutting prereq list. Updated the comment to reflect the new 9-stage ordering.

### 13. Edit: `bonneagar/komodo/procedures/server_id_legend.md`

Added the 3 new procedures (2 to bunchloch section, 1 to arm1-oci section).

## Affected specs

| Spec | Why |
|:--|:--|
| `agent-platform-cluster` | Adds 1 ADDED Requirement: "iac:bootstrap orchestrates all 5 auth components as a single tightly-integrated system" |
| `infrastructure-stacks` | Adds 1 ADDED Requirement: "iac:health checks 6 auth surfaces (was 4-way; now komodo + pangolin + infisical + newt + pocket-id + tinyauth)" |

## Acceptance gates

- [ ] `openspec validate 2026-07-14-tightly-knit-auth-stack-v1 --strict` returns 0
- [ ] `git -C bonneagar push` succeeds
- [ ] `git push origin pick-4-biep-v1` succeeds
- [ ] `bun run iac:health` exits 0 (after the operator does the Pocket ID browser bootstrap)
- [ ] The operator can run `bun run iac:bootstrap-pocketid-admin` and the flow completes in <2 min

## Dependencies

`Blocked by: none` (all work is on bunchloch; no arm1-oci migration required for the user's passkey fix)

`Blocked by (soft): 2026-07-14-repair-bonneagar-iac-3-way-auth-v1` (which provides `iac:rotate-auth` for the 3-way credential rotation; this change extends it with the `ensureBonsIacClient` call)

`Affected repos: bonneagar, cianfhoghlaim`

## Cross-repo sync

See `cross-repo-sync.md` — **bonneagar first** (the IaC code + Komodo procedures), then **cianfhoghlaim** (the openspec change).

## Out of scope

- **The arm1-oci migration of Pocket ID + Tinyauth** — the `deploy-pocket-id-arm1-oci` procedure is declared but not invoked. When arm1-oci is fully bootstrapped (via the existing `2026-07-13-deploy-agent-platform-cluster-arm1-oci-and-remote-dev-workflow` change), the same IaC files work there.
- **Backrest backups of Pocket ID** — should be a follow-up change. Without backups, the DB-wipe scenario could repeat.
- **Removing Tinyauth entirely in favor of Pangolin's built-in Pocket ID integration** — considered but rejected; Tinyauth provides per-app OIDC + fine-grained access control that Pangolin's built-in auth doesn't.

## Operator handoff (the immediate fix for the user's passkey issue)

After this change is committed + pushed, the operator does:

```bash
# 1. Run the bootstrap command
cd /Users/cianmacandeisigh/dev/kings_college_galway/bonneagar
POCKETID_ADMIN_PASSWORD=<the-password-you-set-during-signup> bun run iac:bootstrap-pocketid-admin

# 2. Open the printed URL in a browser (Safari/Chrome with Touch ID)
# 3. Register Touch ID passkey
# 4. Press ENTER in the terminal

# 5. Verify the full chain
bun run iac:health
#   expect: ✓ komodo, ✓ pangolin, ✓ infisical, ✓ newt, ✓ pocket-id (with users > 0), ✓ tinyauth

# 6. Deploy Tinyauth
km run procedure deploy-tinyauth-bunchloch

# 7. Verify Tinyauth
bun run iac:health
#   expect: all 6 surfaces healthy
```

If `POCKETID_ADMIN_PASSWORD` isn't set, the operator must first do the manual UI bootstrap:
1. Enable signup: `docker exec pocket-id sqlite3 /app/data/pocket-id.db "UPDATE app_config_variables SET value='true' WHERE key='signupEnabled';"` (or the IaC will do this for them)
2. Open `https://auth.cianfhoghlaim.ie/signup/setup` in a browser
3. Register Touch ID passkey for `ciansedai` + set a password
4. Add `POCKETID_ADMIN_PASSWORD=<password>` to `~/.env`
5. Re-run `iac:bootstrap-pocketid-admin`
