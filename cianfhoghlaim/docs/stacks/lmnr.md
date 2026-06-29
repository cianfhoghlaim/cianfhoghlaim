# lmnr

## Purpose for the Cianfhoghlaim project

LMNR (Language Model Network Router) is an open-source LLM observability platform providing trace collection, cost tracking, and analytics. It serves as an alternative or complement to Langfuse, with a focus on real-time tracing and ClickHouse-powered analytics.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the agent runtime (Agno + Google ADK + OpenClaw). All agent tools + prompts are versioned in cianfhoghlaim/agents/. LLM credentials from LiteLLM; tracing from Langfuse.

## Cross-references

- **Ops**: `bonneagar/stacks/lmnr/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:agent-platform`
- - **Pangolin**: `https://lmnr.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:agent-platform`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
