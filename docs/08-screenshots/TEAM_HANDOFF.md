# Cianfhoghlaim Convergence Architecture — Team Handoff

> **Status (as of 2026-06-06)**: All 5 private resources live and accessible via Pangolin + WireGuard tunnel.

## What We Built

A two-tier zero-trust network for the **Cianfhoghlaim** stack:

```
┌─────────────────────────────────────────────────────────────────┐
│  Public Internet                                                 │
│  ↓ Lets Encrypt TLS                                             │
│  ↓ Traefik v3.6 (reverse proxy + WAF)                           │
│  ↓ Pangolin EE (identity-aware proxy + licence active)          │
└────────────┬────────────────────────────────────────────────────┘
             │  WireGuard (WireGuard mesh via Gerbil)
             │  PocketID OIDC SSO + TinyAuth forward auth
             │
   ┌─────────┴──────────┐
   │  arm1-oci (Oracle) │ ← Newt v1.12.5 connected
   │  24GB RAM, 4 CPU  │   5 private resources
   │  194GB disk       │
   └────────────────────┘

   ┌────────────────────┐
   │  bunchloch (Mac M4)│ ← Newt (user-installed)
   │  Workload host     │   Future: VM/ML resources
   └────────────────────┘
```

## Live Private Resources

| Resource | Domain | Port | Status |
|---|---|---|---|
| **Pangolin Admin** | `pangolin.cianfhoghlaim.ie` | 443 | ✅ Online |
| **PocketID** (OIDC) | `auth.cianfhoghlaim.ie` | 443 | ✅ Online |
| **TinyAuth** (forward auth) | `tinyauth.cianfhoghlaim.ie` | 443 | ✅ Online |
| **Infisical Vault** | `infisical.cianfhoghlaim.ie` | 8080→443 | ✅ Online |
| **n8n Workflow Automation** | `n8n.cianfhoghlaim.ie` | 5678 | ✅ Online |
| **Vikunja Team Workspace** | `vikunja.cianfhoghlaim.ie` | 3456 | ✅ Online |
| **ChangeDetection.io** | `changedetection.cianfhoghlaim.ie` | 5000 | ✅ Online |
| **Glance Dashboard** | `glance.cianfhoghlaim.ie` | 8080 | ✅ Online |

## Access (Team Member Onboarding)

1. **Install Olm** (Pangolin client for macOS):
   - Download from `pangolin.cianfhoghlaim.ie` admin → "Install Site Connector" → macOS
   - Olm gives your Mac a routable IP in the Pangolin WireGuard mesh (e.g., `100.64.0.X`)

2. **Set up PocketID passkey**:
   - Browse to `https://auth.cianfhoghlaim.ie`
   - Create account using a passkey (Touch ID, YubiKey, etc.)
   - No passwords — passkey-only authentication

3. **Access private resources**:
   - With Olm running, browse directly to `https://n8n.cianfhoghlaim.ie` etc.
   - Pangolin's PocketID SSO layer handles auth
   - All services behind the tunnel are private — no public exposure

## Stack Architecture

### Identity Plane
- **PocketID** — OIDC provider, passkey-only (`auth.cianfhoghlaim.ie`)
- **TinyAuth** — forward auth proxy, backed by PocketID OIDC
- **Pangolin** — auth-aware reverse proxy + WireGuard mesh coordinator

### Secrets Plane
- **Infisical** — vault of record (`infisical.cianfhoghlaim.ie`)
- **Locket** — sidecar pattern; resolves `infisical://` refs at container boot
- **`.infisical.env`** — committed template (no plaintext); `.env` is gitignored runtime

### Routing Plane
- **Traefik v3.6** — terminates TLS, routes by host
- **Gerbil** — manages WireGuard peers + tunnels
- **Newt** — per-site tunnel agent (Docker blueprint enabled)

### Sites
- **arm1-oci** — primary control plane (Oracle Cloud ARM)
- **bunchloch** — workload host (MacBook M4)

## Quick Wins For Team Adoption

### What Works Today
- ✅ All 8 services are reachable via Pangolin tunnel
- ✅ PocketID passkey SSO
- ✅ TinyAuth forward auth
- ✅ Docker blueprint auto-discovery of resources via container labels
- ✅ Locket resolves secrets from Infisical

### What's Next
- ⏳ n8n + Vikunja OIDC login (clients in PocketID pending)
- ⏳ n8n workflows connected to Infisical for credential provisioning
- ⏳ cal-diy + paperless-ngx stacks deployed (compose files ready, need compose up)
- ⏳ Beszel monitoring agent on arm1-oci (currently restarting)

## How Resources Are Declared

Every Docker service gets a `pangolin.yaml` overlay:

```yaml
# infrastructure/stacks/engineering/n8n/pangolin.yaml
services:
  n8n:
    labels:
      - "pangolin.private-resources.n8n.name=n8n Workflow Automation"
      - "pangolin.private-resources.n8n.mode=http"
      - "pangolin.private-resources.n8n.destination=n8n"
      - "pangolin.private-resources.n8n.full-domain=n8n.cianfhoghlaim.ie"
      - "pangolin.private-resources.n8n.destination-port=5678"
      - "pangolin.private-resources.n8n.protocol=http"
      - "pangolin.private-resources.n8n.roles[0]=Member"
```

Then deploy with:
```bash
cd /tmp/komodo-stacks/infrastructure/engineering/n8n
docker compose -f compose.yaml -f pangolin.yaml up -d
```

Newt's Docker socket picks up the labels and registers the resource with Pangolin within ~10s.

## Secret Hydration Pipeline

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ .infisical.env  │    │ bun run         │    │ Infisical Vault │
│ (committed      │ →  │ secrets:init    │ →  │ (dev-baile)     │
│  template)      │    │ (syncs to vault)│    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌──────────▼──────┐
│ .env            │    │ Locket sidecar  │    │ Container env  │
│ (gitignored     │ →  │ watches vault   │ →  │ at runtime     │
│  plaintext)     │    │ resolves refs   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

The `.env` file has the actual values; `.infisical.env` has the path mappings; `secrets:init` pushes the values to the vault; Locket watches and resolves on each container boot.

## Troubleshooting Common Issues

### "Cannot access service"
- Check Olm is running and connected (look for "Pangolin" tray icon)
- Check the service is registered: `https://pangolin.cianfhoghlaim.ie/.../settings/resources/...`
- Check Newt is on the service's Docker network: `docker inspect newt-arm1-oci`

### "Service in restart loop"
- Usually a missing env var from Locket (Locket resolves on watch)
- Check `docker logs <service>` for "env file not found" or auth errors
- Verify the secret exists in Infisical: `infisical secrets list`

### "Locket can't connect to Infisical"
- Locket needs the Infisical URL to be the Docker gateway: `http://172.18.0.1:8081`
- Set `INFISICAL_URL=http://172.18.0.1:8081` in the stack's `.env`
- Confirm `infisical-machine-identity` exists in vault

## Why This Architecture

1. **Zero-trust by default** — No service is publicly accessible; everything goes through Pangolin
2. **Passkey-only auth** — No passwords to phish; PocketID + YubiKey/Touch ID
3. **GitOps-friendly** — Each stack is a self-contained `compose.yaml` + `pangolin.yaml` + `secrets.env` overlay
4. **Self-hosted** — No SaaS dependencies; runs entirely on arm1-oci + bunchloch
5. **Open source** — Pangolin, PocketID, TinyAuth, Infisical, n8n, Vikunja, Glance, ChangeDetection, Locket — all FOSS

## Screenshots

- `docs/screenshots/pangolin-resources.png` — Pangolin resources page showing 5 private resources
- `docs/screenshots/pangolin-sites.png` — Pangolin sites page showing arm1-oci + bunchloch with Newt status
