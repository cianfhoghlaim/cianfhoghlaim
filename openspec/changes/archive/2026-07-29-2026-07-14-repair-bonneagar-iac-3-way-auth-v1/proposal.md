## Shipped in code

All work proposed here has been delivered to the codebase since this change was opened. The remaining tasks are validation gates + the final `openspec archive` call.

# Change: 2026-07-14-repair-bonneagar-iac-3-way-auth-v1

## Why

Phase 1 of the `2026-07-14-cleanup-of-5-deferred-improvements` session
discovered that the bonneagar IaC's 3-way auth is broken:

1. **`PANGOLIN_API_KEY`** in `~/.env` is **invalid** (returns HTTP 401 "Invalid API key" from `GET /v1/org/cianfhoghlaim/site-resources`). The key was either rotated/revoked or minted for a different org.

2. **`KOMODO_PASSWORD`** + **`KOMODO_JWT`** are **NOT in `~/.env`**. The IaC's `iac:health` cannot authenticate to Komodo without one of these.

3. **`INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET`** in `~/.env` is a **placeholder** (`Hackathon2026BuildSmallSecret!`). The real secret lives in the Infisical vault under `dev-baile/infisical-universal-auth/secret` and was never hydrated.

4. The bons IaC's `iac/auth.ts` line 36 says `// TODO: Pocket ID OIDC client_credentials flow` — meaning the only way to mint a fresh Pangolin API key today is **manually via the Pangolin web UI**, then copy-paste it into `~/.env`. This is fragile + undocumented.

This change implements the Pocket ID OIDC `client_credentials` flow
(per the bons auth.ts TODO) + writes a one-shot script that
auto-rotates all 3 secrets on demand.

## What Changes

### 1. New file: `iac/auth-pocketid.ts` (~120 LOC)

Implements `pocketIdLogin()`:
- Discovers Pocket ID's `.well-known/openid-configuration`
- POSTs to `/oidc/token` with `grant_type=client_credentials` + `client_id` + `client_secret`
- Receives an `access_token` (JWT) signed by Pocket ID
- POSTs to Pangolin's `/api/v1/auth/login` (the form-login endpoint) to exchange the Pocket ID token for a Pangolin session cookie
- The session cookie is used for the first API call to `PUT /org/{orgId}/api-key` which mints a fresh API key
- The fresh API key is written to `PANGOLIN_API_KEY` in `~/.env`

### 2. New file: `iac/commands/rotate-auth.ts` (~80 LOC)

The one-shot rotation script:
- Calls `pocketIdLogin()` to mint a fresh Pangolin API key
- Reads `KOMODO_PASSWORD` from Infisical (using the universal auth client) and writes to `~/.env`
- Reads `INFISICAL_UNIVERSAL_AUTH_CLIENT_SECRET` from the Infisical vault and writes to `~/.env` (so the same secret can be used by Locket sidecars)
- Emits a JSON audit record to `/tmp/auth-rotation-{ts}.json`

### 3. Wire into `iac:auth.ts`

Replace the `// TODO: Pocket ID OIDC client_credentials flow` placeholder with `await pocketIdLogin()` calls.

### 4. Wire into `iac:cli.ts` + `package.json`

Add the `rotate-auth` command.

## Affected specs

| Spec | Why |
|:--|:--|
| `agent-platform-cluster` | Adds 1 ADDED Requirement: "iac:rotate-auth mints fresh Pangolin + Komodo + Infisical credentials via Pocket ID OIDC" |

## Acceptance gates

- [ ] `openspec validate 2026-07-14-repair-bonneagar-iac-3-way-auth-v1 --strict` returns 0
- [ ] `bun run iac:rotate-auth` successfully mints a fresh `PANGOLIN_API_KEY` (verified by `iac:health` exit 0)
- [ ] The rotated API key works for the new `iac:sync:sites` command (from `2026-07-14-iac-sync-sites-pangolin-integrations-api-v1`)

## Dependencies

`Blocked by: none` (can be developed in isolation; auth required to test)

`Blocked by (soft): all 4 other changes in this session` (the other 4 changes depend on the auth being fixed to test end-to-end)

`Affected repos: bonneagar`

## Cross-repo sync

See `cross-repo-sync.md` — **bonneagar only** (the auth code is all in bonneagar; the openspec change is documentation only).

## Out of scope

- Rotating the Pocket ID client_secret itself (out of band; manual via Pocket ID web UI)
- Rotating the Cloudflare DNS API token (separate workflow; not blocking newt provisioning)
- Migrating to Pocket ID OIDC's PKCE flow for browser-based users (the service-to-service `client_credentials` flow is sufficient for IaC)
