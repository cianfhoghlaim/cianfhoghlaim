# Durable — KCG Summary

## What It Is
Collection of production-grade examples for **durable execution and orchestration** using two complementary platforms: **Restate** (durable agent workflows with crash-safe LLM calls, idempotent retries, human-in-the-loop, stateful virtual objects, multi-agent RPC) and **DBOS** (durable backend OS with built-in workflow reliability). Both solve the same core problem — keeping long-running agentic workflows alive across crashes, restarts, and waiting periods without bespoke state machinery.

## Why This Matters for Kings' College Galway
Durable execution patterns are critical for the oideachais education platform, where scraping pipelines, curriculum embedding jobs, and multi-agent orchestration run for minutes to hours. Restate's suspend/resume and human-in-the-loop primitives directly map to approval workflows for curriculum content QA. DBOS's transactional workflow model (guaranteed exactly-once execution) aligns with the data platform's need for reliable ingestion and transformation pipelines. The Vercel AI SDK and OpenAI Agents SDK integration examples provide reusable patterns for the TanStack Start frontend's agent backends.

## Key Patterns Preserved
- `restate/README.md` — Catalog of AI workflow examples: Vercel AI SDK, OpenAI Agents, A2A protocol, MCP, Python patterns, TypeScript patterns
- `restate/ai-examples/README.md` — Overview of agentic AI examples across SDKs
- `restate/ai-examples/a2a/README.md` — Agent-to-Agent protocol integration with Restate
- `restate/ai-examples/mcp/README.md` — Model Context Protocol tool servers with durable execution
- `restate/ai-examples/vercel-ai/template/README.md` — Minimal Vercel AI SDK + Restate template
- `restate/ai-examples/vercel-ai/template_nextjs/README.md` — Next.js frontend + Restate backend
- `restate/ai-examples/vercel-ai/tour-of-agents/README.md` — Multi-agent tour using Vercel AI SDK
- `restate/ai-examples/vercel-ai/examples/README.md` — Additional Vercel AI SDK examples
- `restate/ai-examples/openai-agents/template/README.md` — OpenAI Agents SDK + Restate template
- `restate/ai-examples/openai-agents/tour-of-agents/README.md` — Multi-agent tour using OpenAI Agents SDK
- `restate/ai-examples/python-patterns/README.md` — Python-only durable execution patterns (no SDK)
- `restate/mcp/README.md` — Restate MCP server example
- `restate/agent47/README.md` — Full-stack agent with UI, pubsub, and Restate backend
- `restate/agent47/packages/ui/README.md` — Agent47 React frontend
- `restate/agent47/packages/pubsub/README.md` — Agent47 pubsub messaging
- `restate/typescript-patterns/README.md` — TypeScript durable execution patterns
- `dbos/hacker-news-agent/README.md` — Autonomous research agent with React frontend and DBOS backend
- `dbos/hacker-news-agent/frontend/README.md` — Hacker News agent React frontend
- `dbos/widget-store/README.md` — E-commerce workflow with DBOS durable transactions
- `dbos/s3mirror/README.md` — S3 mirror agent with DBOS
- `dbos/dbos-toolbox/README.md` — DBOS Python toolbox utilities
- `dbos/reliable-refunds-langchain/README.md` — LangChain + DBOS for reliable payment workflows
- `dbos/dbos-node-toolbox/README.md` — DBOS Node.js toolbox utilities
- `dbos/dbos-node-starter/README.md` — DBOS Node.js starter template
- `dbos/queue-worker/README.md` — DBOS queue-based worker pattern
- `dbos/document-detective/README.md` — Document processing agent with DBOS

## Source Files
Full source removed (2026-06-06), available at:
- Restate: https://github.com/restatedev/examples
- DBOS: https://github.com/dbos-inc

## What Was Removed
TypeScript source (`.ts`, `.tsx`), Python source (`.py`), JSON configs (`package.json`, `tsconfig.json`, `pyproject.toml`), lock files, Dockerfiles, YAML configs, shell scripts, `.cursor/rules/`, `.claude/` files, images, SVGs, and all non-markdown assets.
