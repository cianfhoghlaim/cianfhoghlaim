# Infisical — Secret Vault

Self-hosted Infisical instance at `https://infisical.cianfhoghlaim.ie` (private, Member role via PocketID SSO).

All 50+ stacks pull secrets from this vault via Locket sidecars.
The `dev-baile` environment is the canonical source of truth.
Use `bun run scripts/init-vault.ts` to sync `.infisical.env` → vault.

### Infisical → Locket → Container Flow
1. `.infisical.env` contains `infisical://dev-baile/<item>/<key>` references
2. `mise` directory hooks auto-hydrate `.env` on cd
3. Locket sidecar watches for changes, injects into `/run/secrets/locket/secrets.env`
4. Containers read from tmpfs (never written to disk)
