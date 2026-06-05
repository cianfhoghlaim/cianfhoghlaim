# Pocket ID — Passkey-Based OIDC Identity Provider

## Overview

Pocket ID is a lightweight, self-hosted OpenID Connect provider built around passkeys (WebAuthn/FIDO2). It provides single sign-on without passwords — users authenticate using biometrics or hardware security keys. Written in Go and Svelte, it is designed as a simpler alternative to Keycloak or Authentik for small-to-medium deployments.

## Why This Matters for Kings' College Galway

Pocket ID is the authentication backbone of the entire infrastructure. Every user-facing service — LiteLLM gateway, Dagster UI, Langfuse, Komodo, Grafana, Forgejo — authenticates through Pocket ID's OIDC endpoint. Using passkeys instead of passwords eliminates credential stuffing and phishing as attack vectors against the curriculum platform. For a project that handles student data and exam materials, this passwordless-by-default posture is a regulatory and ethical requirement, not a luxury.

## Key Features

- **Passkey-only auth** — No passwords; WebAuthn/FIDO2 biometrics or hardware keys
- **OIDC compliance** — Standard OpenID Connect; works with any OIDC-compatible service
- **Lightweight** — Single Go binary with SQLite backend; ~50 MB memory at idle
- **Self-hosted** — Zero dependency on Google, Microsoft, or any external identity provider

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/infrastructure/pocket-id
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. Pocket ID must be running before any service that depends on OIDC authentication — it is the second service brought up after Pangolin.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `PUBLIC_APP_URL` | No | Public URL for OIDC callbacks | `https://auth.cianfhoghlaim.ie` |
| `POCKET_ID_PORT` | No | Listening port | `1411` |

## Access

- **Login Portal**: `https://auth.cianfhoghlaim.ie`
- **OIDC Discovery**: `https://auth.cianfhoghlaim.ie/.well-known/openid-configuration`
- **Health**: `http://localhost:1411/healthz`
- **Auth**: Passkey (WebAuthn) — biometric or hardware security key

## Upstream

- **Repository**: <https://github.com/pocket-id/pocket-id>
- **Documentation**: <https://pocket-id.org>
- **Latest**: Active development (2025) — OIDC compliance improvements, Svelte 5 UI rewrite, multi-tenancy support

## Screenshot

Pocket ID's web UI shows a clean login screen with WebAuthn passkey prompt. The admin panel provides user management, OIDC client registration, and session monitoring. The `/healthz` endpoint returns a simple JSON status response.
