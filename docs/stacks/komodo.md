# komodo

## Purpose for the Cianfhoghlaim project

Komodo is an open-source container orchestration platform by Moghtech that provides GitOps-driven deployment management with a web UI, API, and CLI. It syncs Docker Compose stacks from a Git repository (Forgejo), manages multi-server deployments, and integrates with Pangolin for service routing.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on arm1-oci as part of the zero-trust mesh backbone (Pangolin + Pocket ID + Komodo). All credentials come from Infisical; all ports bind to the cianfhoghlaim bridge network; no public exposure without a Pangolin route.

## Cross-references

- **Ops**: `bonneagar/stacks/komodo/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:arm1-oci` + `tier:infrastructure`
- - **Pangolin**: `https://komodo.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:arm1-oci`
- `tier:infrastructure`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
