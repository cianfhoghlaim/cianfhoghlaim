# langfuse

## Purpose for the Cianfhoghlaim project

Langfuse is an open-source LLM observability platform that traces every LLM call, scores outputs, manages prompts, and provides analytics dashboards. Think of it as Datadog for LLMs — it captures the full trace from user request through model invocation to final response, with cost tracking, latency measurement, and quality evaluation.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the lakehouse data plane (Dagster + DuckLake + Lance). State persists to Garage S3; embeddings to LanceDB; code lives in cianfhoghlaim/ as Python modules. Reproducible via the IaC bootstrap.

## Cross-references

- **Ops**: `bonneagar/stacks/langfuse/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:data-engineering`
- - **Pangolin**: `https://langfuse.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:data-engineering`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
