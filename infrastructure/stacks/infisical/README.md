# Infisical — Secret Vault

Self-hosted Infisical instance at `https://infisical.cianfhoghlaim.ie`
(private, Member role via Pocket ID SSO).

All 50+ stacks pull secrets from this vault via Locket sidecars.
The `dev-baile` environment is the canonical source of truth.
Use `bun run scripts/init-vault.ts` (alias: `mise run secrets:init`)
to sync `.env` → vault.

### Infisical → Locket → Container Flow

1. `.infisical.env` contains `infisical://dev-baile/<item>/<key>` references
2. `mise` directory hooks auto-hydrate `.env` on cd
3. Locket sidecar watches for changes, injects into `/run/secrets/locket/secrets.env`
4. Containers read from tmpfs (never written to disk)

### OIDC / Pocket ID setup

Pocket ID is the OIDC IdP for the Infisical UI. To wire it:

1. In Pocket ID at https://auth.cianfhoghlaim.ie:
   - Settings → OIDC Clients → **+ New**
   - Name: `Infisical Vault`
   - Redirect URI: `https://infisical.cianfhoghlaim.ie/api/v1/auth/oidc/callback`
   - Scopes: `openid profile email`
   - Save; copy `client_id` + `client_secret` to `.env` as
     `INFISICAL_OIDC_CLIENT_ID` / `INFISICAL_OIDC_CLIENT_SECRET`
     (or to the Infisical vault at `dev-baile/infisical-oidc/`)
2. In Infisical UI at https://infisical.cianfhoghlaim.ie:
   - Organization Settings → Authentication → OIDC → **+ Add**
   - Configuration name: `Pocket ID`
   - Discovery URL: `https://auth.cianfhoghlaim.ie/.well-known/openid-configuration`
   - Client ID / Secret: from step 1
   - Friendly name / email claim: `name` / `email`
3. Test: sign out of Infisical, sign back in — you should see a
   "Sign in with Pocket ID" button.

The OIDC client vars are templated in `.infisical.env`:

```
INFISICAL_OIDC_CLIENT_ID=infisical://dev-baile/infisical-oidc/client_id
INFISICAL_OIDC_CLIENT_SECRET=infisical://dev-baile/infisical-oidc/client_secret
INFISICAL_OIDC_ISSUER=infisical://dev-baile/infisical-oidc/issuer
```

### Pangolin private resource

The labels in `pangolin.yaml` register the resource when Komodo
re-deploys the infisical stack. Member role required for any team
member who should have UI access.

### Initial bring-up (one-time)

If the Infisical stack is not yet deployed, follow the standard
stack-up flow:

```bash
# 1. Update the secrets.env with the values from .env
cd infrastructure/infisical
cat .env | grep -E "POSTGRES|REDIS|ENCRYPTION|SITE_URL|JWT|LICENSE" > secrets.env

# 2. Bring up the stack (or via Komodo UI)
docker compose up -d

# 3. Bootstrap the vault: create the dev-baile env + folders
bun run scripts/create-env.ts

# 4. Seed the vault with the contents of .env
bun run scripts/init-vault.ts
```

After the first sync, the vault is the source of truth; `.env` becomes
a hydrated view of the vault (via `mise` directory hooks).
