# oideachais

## Purpose for the Cianfhoghlaim project

The Celtic Education Lakehouse Engine — the production deployment
of the `cianfhoghlaim/` uv workspace member. This stack wires the
5 application services (Dagster, FastAPI, TanStack Start, Agno
AgentOS, Google ADK) to the shared LLM gateway (LiteLLM), the
lakehouse (Garage S3 + Postgres + Lakekeeper + Lance Namespace),
and the LLM observability sink (Langfuse).

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the personal/utility fleet. Reproducible via the IaC bootstrap; no cianfhoghlaim project dependencies.

## Cross-references

- **Ops**: `bonneagar/stacks/cianfhoghlaim/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:personal-utility`
- - **Pangolin**: not exposed (internal-only service)

## Tags

- `host:bunchloch`
- `tier:personal-utility`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
