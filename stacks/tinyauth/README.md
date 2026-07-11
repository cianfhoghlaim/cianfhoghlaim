# Tinyauth

> **Tinyauth v4 + Locket sidecar.** Self-hosted ForwardAuth middleware
> that sits between Traefik and the services behind it, with Pocket ID
> as the OIDC identity provider. This stack was added in
> `2026-07-14-tightly-knit-auth-stack-v1` to fix the persistent crash
> loop caused by a missing Locket sidecar.

## The 6-file GOLD_STANDARD contract

| File | Purpose |
|:--|:--|
| `compose.yaml` | Tinyauth v4 + Locket Infisical sidecar (2 services) |
| `sidecar.yaml` | Locket sidecar overlay — sets `INFISICAL_SECRET_PATH=/tinyauth` + the secret keys to materialize |
| `secrets.env` | Locket `{{ infisical:/// }}` references for the 2 Pocket ID OIDC secrets |
| `pangolin.yaml` | Private resource: `https://tinyauth.cianfhoghlaim.ie` + the OIDC callback sub-route |
| `.env.example` | Local-dev defaults (copy to `.env` for testing) |
| `README.md` | This file |

## How it integrates

```
User browser
   ↓
Traefik (on arm1-oci, deployed by Pangolin)
   ↓ checks Tinyauth via forward-auth
Tinyauth (this stack, on bunchloch)
   ↓ checks Pocket ID OIDC session
Pocket ID (on bunchloch, deployed by stack-pocket-id)
   ↓ validates passkey (WebAuthn)
Returns user session to Tinyauth
   ↓ sets the auth cookie
Traefik forwards the request to the upstream service
```

## Bring-up

```bash
# 0. Bootstrap Pocket ID first (creates the bons-iac OIDC client)
bun run iac:bootstrap-pocketid-admin

# 1. Create the bons-iac OIDC client credentials in Infisical (done by step 0)

# 2. Deploy Tinyauth via Komodo
km run procedure deploy-tinyauth-bunchloch

# 3. Verify Tinyauth is healthy
bun run iac:health
#   expect: ✓ tinyauth: returned 200
```

## Operator runbook

- **Tinyauth crash-looping?** Check `/var/lib/docker/volumes/pangolin_stack-secrets/_data/`
  for the Locket-resolved `secrets.env`. If empty, the Locket sidecar isn't running
  (or can't reach Infisical).
- **Pocket ID OIDC 401s?** Check that `PROVIDERS_POCKETID_CLIENT_ID` is a **dedicated
  OIDC client for Tinyauth** (not the same as the bons-iac one for IaC use). The
  bootstrap command should create a separate `tinyauth` OIDC client.
- **Cookie not being set?** Check `APP_URL` matches the URL the user is accessing
  Tinyauth from (must be `https://tinyauth.cianfhoghlaim.ie`, not `http://`).
