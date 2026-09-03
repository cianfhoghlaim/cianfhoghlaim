# infisical

## Purpose for the Cianfhoghlaim project

Self-hosted Infisical instance at `https://infisical.cianfhoghlaim.ie`
(private, Member role via Pocket ID SSO).

## Why it stays in komodo/pangolin/infisical GitOps

Runs on arm1-oci as part of the zero-trust mesh backbone (Pangolin + Pocket ID + Komodo). All credentials come from Infisical; all ports bind to the cianfhoghlaim bridge network; no public exposure without a Pangolin route.

## Cross-references

- **Ops**: `bonneagar/stacks/infisical/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:arm1-oci` + `tier:infrastructure`
- - **Pangolin**: `https://infisical.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:arm1-oci`
- `tier:infrastructure`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
