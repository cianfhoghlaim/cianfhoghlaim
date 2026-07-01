# forgejo-runner

## Purpose for the Cianfhoghlaim project

The Forgejo Runner executes CI/CD workflows defined in `.forgejo/workflows/` using the same Actions syntax as GitHub Actions. It connects to the self-hosted Forgejo instance at `git.cianfhoghlaim.ie` and provides Docker-in-Docker container job execution.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the personal/utility fleet. Reproducible via the IaC bootstrap; no cianfhoghlaim project dependencies.

## Cross-references

- **Ops**: `bonneagar/stacks/forgejo-runner/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:personal-utility`
- - **Pangolin**: not exposed (internal-only service)

## Tags

- `host:bunchloch`
- `tier:personal-utility`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
