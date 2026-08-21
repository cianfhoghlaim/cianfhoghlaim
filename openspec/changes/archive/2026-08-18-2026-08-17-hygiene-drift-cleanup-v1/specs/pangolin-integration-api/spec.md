# pangolin-integration-api

> NEW capability (added by the `2026-08-17-hygiene-drift-cleanup-v1` change).

## Purpose

The canonical reference for how the Cianfhoghlaim platform integrates
with Pangolin (the Fossorial self-hosted reverse-proxy with identity
+ access control). Covers the 3 canonical Pangolin surfaces in use:

1. **Identity Providers** — PocketID as the OIDC provider for SSO
2. **Site Resources** — the `PUT /org/{orgId}/site-resource` API
   (per `https://docs.pangolin.net/manage/integration-api`)
3. **Traefik routing** — the HTTP-01 ACME certificate resolver for
   `*.cianfhoghlaim.ie`

This spec was added because the previous infrastructure umbrella
spec covered 88 stacks but didn't document the canonical
PocketID + Auto Provision Users + PKCE S256 configuration
required for production SSO.

## ADDED Requirements

### Requirement: Pangolin OIDC + Auto Provision Users + PKCE S256

The Pangolin identity provider integration for PocketID SHALL use
the canonical secure configuration per
`https://docs.pangolin.net/manage/identity-providers/pocket-id`
and `https://pocket-id.org/docs/client-examples/pangolin`:

1. **Auto Provision Users** enabled (per `fosrl/pangolin#1437`)
   — when a user authenticates via PocketID, Pangolin auto-creates
   the remote user without manual approval
2. **PKCE required** (`require_pkce: true` + `pkce_challenge_method: S256`)
3. **`certResolver: letsencrypt` for HTTP-01** (not DNS-01) on the
   10 `*.cianfhoghlaim.ie` hostnames

This configuration SHALL be documented in
`docs/PANGOLIN_OIDC_CONFIG.md` (added by the
`2026-08-17-hygiene-drift-cleanup-v1` change).

#### Scenario: Operator adds a new PocketID OIDC client

- **WHEN** `bun run scripts/create-pocketid-oidc-client.ts` creates
  a new OIDC client in PocketID for a new internal service
- **THEN** the client SHALL be configured with:
  - `require_pkce: true`
  - `pkce_challenge_method: S256`
  - `redirect_uri: https://<service>.cianfhoghlaim.ie/api/auth/callback`
  - `scopes: openid profile email groups`
- **AND** the Pangolin Identity Provider setup SHALL have
  `Auto Provision Users` enabled

#### Scenario: PocketID user authenticates for the first time

- **WHEN** a new user authenticates via PocketID for the first time
- **THEN** Pangolin SHALL auto-create the remote user (no manual
  approval required) per `fosrl/pangolin#1437`
- **AND** the user SHALL be assigned to the default Pangolin organization

#### Scenario: Traefik ACME certificate renewal

- **WHEN** the Let's Encrypt certificate for
  `litellm.cianfhoghlaim.ie` approaches expiry (within 30 days)
- **THEN** Traefik SHALL renew via the HTTP-01 challenge using the
  `letsencrypt` resolver (per `certResolver: letsencrypt` in
  `bonneagar/pangolin/config/traefik/traefik_config.yml`)
- **AND** the renewed certificate SHALL be pushed to the
  Pangolin site connector