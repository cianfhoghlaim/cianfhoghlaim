# nimtable

## Purpose for the Cianfhoghlaim project

Nimtable is a web-based table explorer for Apache Iceberg catalogs. It provides a browser UI for discovering, inspecting, and querying Iceberg tables — showing schemas, partition specs, snapshots, and data previews.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the LLM inference + observability surface. LiteLLM is the unified gateway; MLX-Omni is the local Apple Silicon backend; Langfuse + mlflow + logfire provide the observability tier.

## Cross-references

- **Ops**: `bonneagar/stacks/nimtable/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:language-model`
- - **Pangolin**: `https://nimtable.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:language-model`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
