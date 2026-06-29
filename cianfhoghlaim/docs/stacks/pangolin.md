# pangolin

## Purpose for the Cianfhoghlaim project

Pangolin is an open-source identity-aware reverse proxy built by Fosrl that combines WireGuard VPN tunnels, Traefik reverse proxy, Pocket ID OIDC authentication, and CrowdSec intrusion detection into a single stack. It provides zero-trust access to private services — no open ports, no public IPs, every request authenticated before it reaches the backend.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on arm1-oci as part of the zero-trust mesh backbone (Pangolin + Pocket ID + Komodo). All credentials come from Infisical; all ports bind to the cianchoghlaim bridge network; no public exposure without a Pangolin route.

## Cross-references

- **Ops**: `bonneagar/stacks/pangolin/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:arm1-oci` + `tier:infrastructure`
- - **Pangolin**: not exposed (internal-only service)

## Tags

- `host:arm1-oci`
- `tier:infrastructure`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
