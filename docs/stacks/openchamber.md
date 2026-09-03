# openchamber

## Purpose for the Cianfhoghlaim project

OpenChamber is a browser-based OpenCode UI built on Bun + React. It bundles the `opencode-ai` runtime inside its own container, so
there is no need to run a separate OpenCode daemon.

## Why it stays in komodo/pangolin/infisical GitOps

Runs on bunchloch as part of the agent runtime (Agno + Google ADK + OpenClaw). All agent tools + prompts are versioned in cianfhoghlaim/agents/. LLM credentials from LiteLLM; tracing from Langfuse.

## Cross-references

- **Ops**: `bonneagar/stacks/openchamber/` (the 6-file GOLD_STANDARD)
- **Code**: `cianfhoghlaim/<code-path>` (if any — see the linked Dagster assets / BAML schemas / DLT sources)
- **IaC**: registered in `bonneagar/iac/komodo/deploy-stacks.ts` with tags `host:bunchloch` + `tier:agent-platform`
- - **Pangolin**: `https://openchamber.cianfhoghlaim.ie` (if exposed)

## Tags

- `host:bunchloch`
- `tier:agent-platform`
- `project:cianfhoghlaim` (if cianfhoghlaim-relevant)
