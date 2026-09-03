# backrest

## Purpose for the Cianfhoghlaim project

Backrest is a web-based management interface for Restic, the fast and secure backup program. It provides a graphical dashboard for configuring backup schedules, monitoring backup health, browsing snapshots, and restoring files — all backed by Restic's deduplicated, encrypted, and versioned repository format.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on arm1-oci as part of the zero-trust mesh backbone (Pangolin + Pocket ID + Komodo). All credentials come from Infisical; all ports bind to the cianfhoghlaim bridge network; no public exposure without a Pangolin route.

## Cross-references

- **Ops**: `bonneagar/stacks/backrest/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:arm1-oci` + `tier:infrastructure`
- - **Pangolin**: `https://backrest.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:arm1-oci`
- `tier:infrastructure`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
