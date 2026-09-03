# motherduck

## Purpose for the Cianfhoghlaim project

Cloud-hosted DuckDB with serverless scaling and collaboration features.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the LLM inference + observability surface. LiteLLM is the unified gateway; MLX-Omni is the local Apple Silicon backend; Langfuse + mlflow + logfire provide the observability tier.

## Cross-references

- **Ops**: `bonneagar/stacks/motherduck/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:language-model`
- - **Pangolin**: not exposed (internal-only service)

## Tags

- `host:bunchloch`
- `tier:language-model`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
