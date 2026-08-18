# Pangolin OIDC + Pocket ID Configuration

> Added 2026-08-17 by the `2026-08-17-hygiene-drift-cleanup-v1` change (P2.7).
> Canonical reference for how the Cianfhoghlaim platform integrates
> Pangolin (the Fossorial self-hosted reverse-proxy with identity + access control)
> with Pocket ID (the OIDC identity provider).

The patterns documented here are derived from:
- `https://docs.pangolin.net/manage/identity-providers/pocket-id`
- `https://pocket-id.org/docs/client-examples/pangolin`
- `https://github.com/fosrl/pangolin/issues/1437` (Auto Provision Users)
- `https://github.com/fosrl/pangolin/issues/1838` (known OIDC + PocketID config traps)

---

## 1. Pocket ID OIDC client configuration (canonical)

For every OIDC client created in Pocket ID for a Cianfhoghlaim service
(`bun run scripts/create-pocketid-oidc-client.ts` or
`bun run scripts/wire-pocketid-pangolin-komoid.sh`):

| Setting | Value | Why |
|:--|:--|:--|
| Client ID | `<service>-cianfhoghlaim` (e.g. `litellm-cianfhoghlaim`) | Stable, machine-parseable |
| Client type | Confidential | Service-to-service; PKCE S256 required |
| `require_pkce` | `true` | Prevents authorization code interception (per `https://www.authelia.com/integration/openid-connect/clients/pangolin/`) |
| `pkce_challenge_method` | `S256` | SHA-256 (mandatory for confidential clients) |
| `redirect_uri` | `https://<service>.cianfhoghlaim.ie/api/auth/callback` | Per service's Hono API route |
| `scopes` | `openid profile email groups` | Minimal set for SSO + group-based RBAC |
| Token endpoint auth method | `client_secret_basic` | Standard for confidential clients |
| Grant types | `authorization_code`, `refresh_token` | (Never `implicit` or `password`) |

**Pangolin side** (Identity Provider setup):
- Provider type: `OAuth2/OIDC`
- **Auto Provision Users: enabled** (per `fosrl/pangolin#1437`)
- Match against the default organization

---

## 2. Traefik + Let's Encrypt ACME (HTTP-01)

All 10 `*.cianfhoghlaim.ie` hostnames use the **HTTP-01** challenge
against Let's Encrypt:

```yaml
# bonneagar/pangolin/config/traefik/traefik_config.yml
tls:
  certificates:
    - certFile: /letsencrypt/cert.pem
      keyFile: /letsencrypt/key.pem
      stores:
        - default
  stores:
    default:
      defaultCertificate:
        certFile: /letsencrypt/cert.pem
        keyFile: /letsencrypt/key.pem
      defaultGeneratedCert:
        resolver: letsencrypt  # <-- HTTP-01, NOT letsencrypt-dns
```

The resolver name is `letsencrypt` (HTTP-01), NOT `letsencrypt-dns`
(DNS-01). The current configuration uses HTTP-01; any switch to
DNS-01 would require adding a `CLOUDFLARE_DNS_API_TOKEN` env var.

---

## 3. Auto Provision Users — the canonical pattern

When a new user authenticates via Pocket ID for the first time:

1. Pocket ID returns the OIDC `id_token` + `access_token`
2. Pangolin's Identity Provider validates the token (PKCE S256)
3. **Auto Provision Users** (if enabled) auto-creates the remote user
   in the default Pangolin organization — no manual approval required
4. The user is granted the default role on the bound resource

Per `fosrl/pangolin#1437`, this is the recommended setup. The previous
pattern of manually creating remote users in Pocket ID (or pre-creating
them in Pangolin) does not scale and breaks when users rotate credentials.

---

## 4. Locket sidecar dependency

Every Pangolin-routed service that uses Infisical secrets MUST use
the locket sidecar at `>= v0.18.0` OR substitute the
`ghcr.io/cianfhoghlaim/locket-shim:infisical-0.2.0` image.

The lint gate `mise run lint:locket-version` enforces this. See
`openspec/specs/infrastructure-stacks/spec.md` for the regression
context (Infisical v0.161+ requires camelCase field names; the
upstream `locket v0.17.3` ships snake_case and 422s on every call).

As of 2026-08-17, the canonical pattern is the shim image. The shim
is a 295-line Python script (`bonneagar/locket-shim/cianfhoghlaim-locket-shim.py`)
that replicates the upstream `locket` sidecar but with the correct
camelCase field names (`projectId`, `secretPath`, `secretType`).

---

## 5. Known config traps (from firecrawl + ccc research)

| Trap | Fix |
|:--|:--|
| OIDC client configured without PKCE (per `fosrl/pangolin#1838`) | Always set `require_pkce: true` + `pkce_challenge_method: S256` |
| Manual user approval breaks the SSO flow (per `fosrl/pangolin#1437`) | Enable Auto Provision Users |
| `certResolver: letsencrypt-dns` without DNS-01 token configured | Use `letsencrypt` (HTTP-01) |
| Bare `bpbradley/locket:infisical` (no version pin, breaks on Infisical v0.161+) | Pin to >= v0.18.0 OR substitute the shim image |
| `redirect_uri` mismatch (token endpoint rejects the auth code) | Use `https://<service>.cianfhoghlaim.ie/api/auth/callback` exactly |

---

## 6. Related documentation

- `openspec/specs/infrastructure-stacks/spec.md` — the canonical spec for the 94 Docker Compose stacks + Locket version invariant
- `openspec/specs/pangolin-integration-api/spec.md` — the new spec added by this change
- `openspec/specs/bonneagar-iac-merge/spec.md` — the unified TypeScript IaC at `bonneagar/iac/`
- `.agents/skills/infrastructure-stacks/SKILL.md` — the 6-file GOLD_STANDARD pattern
- `.agents/skills/pangolin/SKILL.md` — Fossorial Pangolin reverse-proxy operations