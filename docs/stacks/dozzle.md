# dozzle

## Purpose for the Cianfhoghlaim project

Dozzle is a lightweight, real-time log viewer for Docker containers. It provides a web UI for browsing, searching, and monitoring container logs without needing to SSH into a server or use `docker logs`.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the personal/utility fleet. Reproducible via the IaC bootstrap; no cianfhoghlaim project dependencies.

## Cross-references

- **Ops**: `bonneagar/stacks/dozzle/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:personal-utility`
- - **Pangolin**: `https://dozzle.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:personal-utility`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
