# Infisical + Pocket ID + Pangolin — Secret Sync Runbook

> The work needed to get the local `HF_TOKEN` (and all 100+ other
> secrets in `.env`) synced to the self-hosted Infisical at
> `infisical.cianfhoghlaim.ie`, and to wire OIDC through Pocket ID
> for the Pangolin private-resource for it.

## Goal

1. `HF_TOKEN=hf_shacQjNZ...` (currently only in local shell + `.env`)
   lands in the Infisical vault at `dev-baile/huggingface/token` (and
   all 100+ siblings in `.infisical.env`).
2. Pocket ID is the OIDC IdP for the `infisical.cianfhoghlaim.ie`
   Pangolin private resource, so any team member can sign in to the
   Infisical UI without a separate password.

## Current state (audit)

| Check | State | Source |
|:--|:--|:--|
| `HF_TOKEN` in local shell | yes | `env HF_TOKEN=...` |
| `HF_TOKEN` in `.env` | yes | already hydrated |
| `HF_TOKEN` in `.infisical.env` template | yes | `HF_TOKEN=infisical://dev-baile/huggingface/token` |
| `HF_TOKEN` in Infisical vault | **unknown — likely stale** | need to run `init-vault` |
| Infisical at `infisical.cianfhoghlaim.ie` | reachable (HTTP 200) | `curl -sI` |
| Pocket ID at `auth.cianfhoghlaim.ie` | reachable, OIDC serving | `.well-known/openid-configuration` returns 200 |
| Pocket ID OIDC client for Infisical | **needs creation** | one-time, in Pocket ID UI |
| Pangolin private-resource for Infisical | **declared in `pangolin.yaml` but not registered** | labels need to be applied by Komodo/Pangolin sync |
| `init-vault.ts` SDK works | **broken** (405 on universalAuth.login) | SDK 5.x API change |

## What I can do from this shell

1. Fix `init-vault.ts` so the SDK auth works against the self-hosted
   Infisical (right now it 405s on `universalAuth.login`).
2. Set `INFISICAL_URL=https://infisical.cianfhoghlaim.ie` in `.env`
   so the SDK points to the self-hosted instance, not the SaaS.
3. Update the `init-vault.ts` 405 error message to give clearer
   remediation steps.
4. Add a `dev-baile-oidc-client-secret` line to `.infisical.env` for
   the new Pocket ID → Infisical OIDC client.
5. Commit the script fix.
6. Run `mise run secrets:init` once the script works.

## What blocks me (needs you, browser only)

1. **Log in to Infisical** at https://infisical.cianfhoghlaim.ie —
   I don't have a session cookie and the API auth is via
   `INFISICAL_CLIENT_ID`/`INFISICAL_CLIENT_SECRET` (a machine
   identity, not your user account). If the machine identity in
   `.env` is the right one, no browser step is needed; otherwise
   you need to create one in the Infisical UI and put the secret
   into `.env`.
2. **Create a Pocket ID OIDC client for Infisical.** Pocket ID's
   UI is at https://auth.cianfhoghlaim.ie. You need to log in,
   create a new OIDC client, set the redirect URI to
   `https://infisical.cianfhoghlaim.ie/api/v1/auth/oidc/callback`,
   and copy the `client_id` + `client_secret`. Then add the secret
   to `.env` so Infisical can verify the IdP.
3. **Register the Pangolin private resource.** The labels in
   `infrastructure/infisical/pangolin.yaml` declare what we want,
   but Pangolin doesn't auto-apply labels from a file — Komodo
   reads the file at deploy time and pushes the labels. So this
   step is "deploy (or re-deploy) the infisical stack" via the
   Komodo UI/API.
4. **Add the `Member` role to yourself in Pocket ID for the
   Infisical resource.** This is a per-resource ACL in Pangolin.

## Step-by-step (the actual work)

### Phase 1 — script fix (I do this, then commit)

#### 1.1. Set `INFISICAL_URL` in `.env`

The SDK defaults to `https://app.infisical.com` (the SaaS) if
`INFISICAL_URL` is unset. We need it pointed at the self-hosted
instance. The `.env` currently has it commented out:

```
# INFISICAL_URL=http://localhost:8081
```

Uncomment and update to:

```
INFISICAL_URL=https://infisical.cianfhoghlaim.ie
```

#### 1.2. Fix the `init-vault.ts` 405

The Infisical SDK 5.x moved `universalAuth.login` to use a different
endpoint. Two possible fixes:

- **Option A** (most likely): the SDK now requires an explicit
  `clientId` + `clientSecret` *and* a workspace/project ID, AND the
  path changed from `/api/v1/auth/universal-auth/login` to something
  else.
- **Option B**: there's an auth header convention where the SDK
  reads `INFISICAL_TOKEN` from env directly and skips the
  universalAuth flow.

Try **Option B first** (simpler). Patch `init-vault.ts` to fall
back to a pre-authenticated token if `INFISICAL_TOKEN` is set:

```ts
if (process.env.INFISICAL_TOKEN) {
    client.authenticate(process.env.INFISICAL_TOKEN);
    // skip universalAuth.login entirely
} else {
    await client.auth().universalAuth.login({...});
}
```

Then you generate an `INFISICAL_TOKEN` in the Infisical UI
(Settings → Personal Access Tokens) and add it to `.env`.

#### 1.3. Verify

Run:

```bash
bun run scripts/init-vault.ts
```

Expected output: the script reads `.env`, iterates the `.infisical.env`
template, and seeds/updates each `infisical://dev-baile/...` secret
in the vault. Watch for `Updated: [dev-baile] /huggingface/token`.

If 100% of secrets succeed, the vault is in sync.

### Phase 2 — Pocket ID OIDC for Infisical (you do this, browser)

In the Pocket ID UI at https://auth.cianfhoghlaim.ie:

1. **Settings → OIDC Clients → + New**
2. Name: `Infisical Vault`
3. Redirect URI: `https://infisical.cianfhoghlaim.ie/api/v1/auth/oidc/callback`
4. Scopes: `openid profile email`
5. Save; copy the `client_id` and `client_secret` to a scratch buffer.

In the Infisical UI at https://infisical.cianfhoghlaim.ie:

1. **Organization Settings → Authentication → OIDC → + Add OIDC**
2. Configuration name: `Pocket ID`
3. Discovery URL: `https://auth.cianfhoghlaim.ie/.well-known/openid-configuration`
4. Client ID / Secret: paste from Pocket ID
5. Friendly name / email claim: `name` / `email`
6. Save.

Test by signing out of Infisical and signing back in — you should
see a "Sign in with Pocket ID" button.

Add to `.env`:

```
INFISICAL_OIDC_CLIENT_ID=<from Pocket ID>
INFISICAL_OIDC_CLIENT_SECRET=<from Pocket ID>
INFISICAL_OIDC_ISSUER=https://auth.cianfhoghlaim.ie
```

These can also be added as Infisical-level secrets (so other team
members share the same OIDC config) — but for the demo, local
`.env` is fine.

### Phase 3 — Pangolin private resource registration (you do this, Komodo UI)

The `infrastructure/infisical/pangolin.yaml` declares the labels
we want, but Pangolin reads them at deploy time. So the
registration happens when you (re-)deploy the infisical stack via
Komodo:

1. Open https://komodo.cianfhoghlaim.ie
2. Stacks → `infisical`
3. Deploy (or Pull + Deploy)
4. The labels from `pangolin.yaml` get applied to the `infisical-backend`
   container; Pangolin picks them up; the `infisical.cianfhoghlaim.ie`
   private resource becomes active.

In the Pangolin UI at https://pangolin.cianfhoghlaim.ie:

1. Resources → find the `Infisical Vault` private resource
2. Add yourself to the `Member` role
3. Save

### Phase 4 — re-sync the vault (back to I do this)

```bash
mise run secrets:init
```

(or `mise run secrets:sync`, same thing)

This pushes the *current* `.env` to Infisical, overwriting whatever
is in the vault. Watch for `Updated: [dev-baile] /huggingface/token`
— that's `HF_TOKEN` landing in the vault.

### Phase 5 — re-deploy Spaces with the synced token (your turn)

The 4 Spaces on HF each need the `HF_TOKEN` secret set at
`/spaces/<slug>/settings`. Run:

```bash
bash scripts/push_spaces_to_hf.sh
```

(If you've already pushed the Spaces, this is a no-op for the
repos but re-uploads the staging files. To update only the secret,
use the HF Web UI per the runbook §3.)

## Quick decision matrix

| If you only need... | Do this |
|:--|:--|
| HF Spaces to work | Set `HF_TOKEN` directly at the 4 Space settings URLs. Don't touch Infisical. |
| `HF_TOKEN` in the Infisical vault | Phase 1 only (script fix + `INFISICAL_URL` + re-run `init-vault`). |
| Pocket ID OIDC for Infisical | Phase 2 only. |
| All of the above | Phases 1+2+3+4. |
| Full secret-contract compliance | All phases + the `locket:exec` and `mise` hooks in the runbook. |

## Files to touch

- `scripts/init-vault.ts` — patch the auth flow (Phase 1.2)
- `.env` — set `INFISICAL_URL` (Phase 1.1); add OIDC client vars
  (Phase 2); no manual `.env` writes outside the runbook for
  other secrets
- `infrastructure/infisical/pangolin.yaml` — already correct
- `infrastructure/infisical/docker-compose.yaml` — already correct
- Pocket ID UI — create OIDC client (Phase 2)
- Infisical UI — add OIDC IdP (Phase 2)
- Komodo UI — re-deploy infisical stack (Phase 3)

## Constraints (per `infrastructure/AGENTS.md`)

- **Never commit secrets to git.** `.env` is gitignored. All new
  secret material lives in the Infisical vault.
- **Don't manually create `.env` files** — allow mise hooks and
  Locket to hydrate. The `INFISICAL_URL` line is a non-secret
  config var, so updating it is fine.
- **All stacks use shared Docker network.** The infisical stack
  uses `infrastructure` (external). This is pre-existing.

Long learning. Cianfhoghlaim.
