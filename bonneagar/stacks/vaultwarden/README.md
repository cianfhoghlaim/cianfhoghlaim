# Vaultwarden — Self-Hosted Bitwarden-Compatible Password Manager

## Overview

Vaultwarden is a lightweight, Rust-based implementation of the Bitwarden server API, compatible with all official Bitwarden clients (browser extension, desktop app, mobile app, CLI). It provides team password management, secure credential sharing, and OIDC single sign-on integration with a fraction of the resources of the official Bitwarden server.

## Why This Matters for Kings' College Galway

Infisical handles operational secrets (API keys, database passwords, S3 credentials) injected via Locket at runtime. Vaultwarden handles the human-facing secrets: teaching platform login credentials, shared research account passwords, SSH keys, and team-access tokens. The separation is deliberate — ops secrets are ephemeral and machine-readable; human secrets are persistent and need browser integration. With Pocket ID OIDC enabled, team members authenticate to Vaultwarden using the same passkey they use for every other service, maintaining the zero-password posture of the infrastructure.

## Key Features

- **Full Bitwarden compatibility** — Works with all official Bitwarden clients
- **Rust-native performance** — <100 MB memory vs 2+ GB for official Bitwarden server
- **OIDC SSO** — Pocket ID integration for passkey-based authentication
- **Organisation sharing** — Shared collections for team credentials
- **WebSocket support** — Real-time sync across browser extensions and mobile apps

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/vaultwarden
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on arm1-oci. SSO is configured via environment variables for Pocket ID OIDC. Admin invitations only (`SIGNUPS_ALLOWED=false`).

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `SIGNUPS_ALLOWED` | No | Allow open registration | `false` |
| `INVITATIONS_ALLOWED` | No | Allow admin invitations | `true` |
| `SHOW_PASSWORD_HINT` | No | Show password hints on login | `false` |
| `SSO_ENABLED` | No | Enable OIDC SSO | `true` |
| `SSO_CLIENT_ID` | Yes | OIDC client ID (Pocket ID) | — |
| `SSO_CLIENT_SECRET` | Yes | OIDC client secret | — |
| `SSO_AUTHORITY` | Yes | OIDC issuer URL | `https://auth.cianfhoghlaim.ie` |
| `RUST_LOG` | No | Log level | `info` |

## Access

- **Web Vault**: `https://vault.cianfhoghlaim.ie` (private, Member role)
- **WebSocket**: Port 3012 (for browser extension live sync)
- **Auth**: Pocket ID SSO (passkey) or master password

## Upstream

- **Repository**: <https://github.com/dani-garcia/vaultwarden>
- **Documentation**: <https://github.com/dani-garcia/vaultwarden/wiki>
- **Latest**: v1.33.x (2025) — WebSocket improvements, OIDC group mapping, Send file sharing, ARM64 optimisations

## Screenshot

Vaultwarden's web vault interface matches the Bitwarden client: password list with search, folder organisation, secure note editor, and organisation management for shared collections. The admin panel (`/admin`) shows registered users, active sessions, and server diagnostics.
