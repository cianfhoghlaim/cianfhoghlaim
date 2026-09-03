# frontend

## Purpose for the Cianfhoghlaim project

The 5 TypeScript frontend workspaces in the Cianfhoghlaim monorepo, packaged as
independent services and routed through Pangolin + Traefik.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the personal/utility fleet. Reproducible via the IaC bootstrap; no cianfhoghlaim project dependencies.

## Cross-references

- **Ops**: `bonneagar/stacks/frontend/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:personal-utility`
- - **Pangolin**: not exposed (internal-only service)

## Tags

- `host:bunchloch`
- `tier:personal-utility`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
