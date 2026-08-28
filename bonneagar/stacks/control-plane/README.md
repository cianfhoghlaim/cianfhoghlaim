# CONTROL-PLANE STACK — Bundled 5-control-plane setup for arm1-oci

> **Companion**: [openspec/changes/2026-07-15-iac-ify-arm1-oci-control-plane-v1](../../../../openspec/changes/2026-07-15-iac-ify-arm1-oci-control-plane-v1/proposal.md)

The full control-plane stack (5 services: Komodo + Infisical + Pangolin + Pocket ID + Tinyauth) bundled into a single docker-compose stack with Locket sidecars for secrets management.

## What's in the stack

| Service | Image | Port | Purpose | Locket sidecar |
|:--|:--|--:|:--|:--|
| `pangolin` | `fosrl/pangolin:ee-latest` | 3000 | Reverse proxy + WireGuard tunnel | ✅ |
| `pangolin-db` | `postgres:17` | 5432 | Pangolin data store | ❌ |
| `pocket-id` | `ghcr.io/pocket-id/pocket-id:latest` | 1411 | OIDC IdP | ✅ |
| `komodo` | `ghcr.io/moghtech/komodo-core:2` | 9120 | Orchestrator | ✅ |
| `komodo-ferretdb` | `ghcr.io/ferretdb/ferretdb:2` | - | Komodo Mongo API | ❌ |
| `komodo-postgres` | `ghcr.io/ferretdb/postgres-documentdb:17` | 5432 | Komodo data store | ❌ |
| `tinyauth` | `ghcr.io/steveiliop56/tinyauth:v4` | 3000 | ForwardAuth middleware | ✅ |
| `infisical` | `infisical/infisical:latest` | 8080 | Secrets vault | ✅ |
| `infisical-db` | `postgres:16-alpine` | 5432 | Infisical data store | ❌ |
| `infisical-redis` | `redis:7-alpine` | 6379 | Infisical cache | ❌ |
| `traefik` | `traefik:v3.6.0` | 80/443 | TLS terminator | ❌ |

## Architecture

```
                          [Traefik :443 TLS]
                                │
       ┌────────────┬────────────┼────────────┬────────────┐
       ▼            ▼            ▼            ▼            ▼
    Pangolin    Pocket ID    Komodo     Infisical    Tinyauth
       │            │            │            │            │
       │ (OIDC)     │ (OIDC)     │ (OIDC)     │ (source)  │ (SSO)
       └────────────┴────────────┴────────────┴────────────┘
                                │
                          [Locket sidecars]
                                │
                            [Infisical vault]
```

Every service has a Locket sidecar that materializes secrets from
Infisical at container startup. The Locket pattern is the canonical
bons IaC secrets-injection method (see `iac/docs/locket.md`).

## Operator handoff

### Phase 1: bunchloch (local dev/canary)

```bash
cd /Users/cianmacandeisigh/dev/cianfhoghlaim/bonneagar
bun run iac:bootstrap-control-plane-bunchloch
```

This runs all 8 phases in order:
1. locket binary (downloads to `~/.local/bin/locket`)
2. Pulumi IaC (no-op on bunchloch)
3. bundled stack deploy (`docker compose up -d`)
4. Infisical bootstrap (first admin + 8 machine identities via API/Chrome-MCP)
5. Pocket ID OIDC wire (creates `komodo` OIDC client + wires Komodo + Pangolin)
6. Komodo Periphery (provisions the agent on bunchloch)
7. Newt (provisions the Pangolin tunnel on bunchloch)
8. health verify (7-way check)

### Phase 2: arm1-oci (production)

```bash
cd /Users/cianmacandeisigh/dev/cianfhoghlaim/bonneagar
bun run iac:bootstrap-control-plane-arm1-oci
```

Same 8 phases, but:
- Phase 2 (Pulumi IaC) actually provisions the arm1-oci VM
- Phase 6 + 7 deploy to arm1-oci instead of bunchloch

### Verify

```bash
bun run iac:health
# expect: ✓ komodo + ✓ pangolin + ✓ infisical + ✓ newt + ✓ pocket-id + ✓ tinyauth
```

## Public endpoints (post-deploy)

| Service | URL | Purpose |
|:--|:--|:--|
| Pangolin | https://pangolin.cianfhoghlaim.ie | Reverse proxy UI + API |
| Pocket ID | https://auth.cianfhoghlaim.ie | OIDC login (passkey) |
| Komodo | https://komodo.cianfhoghlaim.ie | Orchestrator UI |
| Infisical | https://infisical.cianfhoghlaim.ie | Secrets vault |
| Tinyauth | https://tinyauth.cianfhoghlaim.ie | ForwardAuth UI (SSO) |

## 6-file GOLD_STANDARD contract

| File | Purpose |
|:--|:--|
| `compose.yaml` | 11 services + 5 locket sidecars + 5 volumes + 1 network |
| `sidecar.yaml` | Locket Infisical provider config (used by every service) |
| `secrets.env` | `{{ infisical:///... }}` refs for each service's secrets |
| `pangolin.yaml` | Traefik routes for the 5 public services |
| `blueprint.yaml` | Komodo Resource Sync manifest |
| `.env.example` | Bootstrap-mode env vars (placeholder for first deploy) |
| `README.md` | This file |

## Troubleshooting

### Locket sidecar keeps restarting

- Check that `INFISICAL_CLIENT_ID` + `INFISICAL_CLIENT_SECRET` are set in `.env`
- Run `locket inject --provider=infisical ... --mode=one-shot` locally to test the auth

### Komodo OIDC login fails

- Check the `POCKETID_KOMODO_CLIENT_ID` + `POCKETID_KOMODO_CLIENT_SECRET` are populated
- Verify the Pocket ID OIDC client `komodo` has the correct callback URL: `https://komodo.cianfhoghlaim.ie/auth/oidc/callback`

### Pangolin can reach Pocket ID but no IDP visible

- Run `bun run iac:wire-pocketid-as-oidc` to ensure the Identity Provider is created in Pangolin
- Check the Pangolin UI → Server Admin → Identity Providers → PocketID is enabled

## Cross-references

- `iac/docs/locket.md` — the Locket provider patterns
- `iac/clients/infisical-rest.ts` — the direct-REST Infisical client
- `iac/clients/komodo-client.ts` — the Komodo REST client
- `iac/clients/pangolin-client.ts` — the Pangolin Integrations API client
- `iac/commands/bootstrap-control-plane.ts` — the operator's one-shot
- `iac/commands/bootstrap-infisical.ts` — first admin + 8 machine identities
- `iac/commands/wire-pocketid-as-oidc.ts` — OIDC wiring
- `iac/commands/deploy-periphery.ts` — Komodo Periphery
- `iac/commands/deploy-newt.ts` — Newt tunnel
