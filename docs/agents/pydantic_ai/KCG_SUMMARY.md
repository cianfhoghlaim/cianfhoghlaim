# Pydantic AI — KCG Summary

## What It Is
Documentation clippings and patterns covering the **Pydantic AI stack**: Pydantic AI Gateway (unified multi-provider LLM access with built-in observability and failover), Agent-User Interaction (AG-UI) protocol integration for React frontends, MCP instrumentation via Pydantic Logfire, and DBOS durable execution integration. Also includes a DBOS integration demo showing how Pydantic AI agents compose with durable backends.

## Why This Matters for Kings' College Galway
The Pydantic AI Gateway offers a unified API layer for the multiple LLM providers used across Cianfhoghlaim (OpenCode, Hugging Face, Gemini), with built-in observability via OpenTelemetry that integrates with the existing Langfuse tracing infrastructure. The AG-UI protocol documentation provides the integration pattern for connecting the CopilotKit-powered frontend to agent backends using the same open standard the project already targets. The MCP + Logfire instrumentation guide shows how to add distributed tracing to the filesystem MCP server and future curriculum tool servers.

## Key Patterns Preserved
- `Pydantic AI Gateway - Pydantic AI.md` — Comprehensive guide to the Pydantic AI Gateway: setup, BYOK, inference purchasing, OpenTelemetry, failover, provider configuration
- `AG-UI - Pydantic AI.md` — AG-UI protocol integration guide: installation, streaming, frontend tools, shared state, custom events, CopilotKit compatibility
- `MCP - Pydantic Logfire Documentation.md` — MCP SDK instrumentation guide: client/server-side tracing, distributed traces, Logfire integration
- `dbos/README.md` — Demo of the Pydantic stack with DBOS durable execution

## Source Files
Full source removed (2026-06-06). Content originally clipped from:
- Pydantic AI docs: https://ai.pydantic.dev/
- Pydantic Logfire docs: https://logfire.pydantic.dev/
- AG-UI protocol: https://docs.ag-ui.com/

## What Was Removed
All non-markdown files were already absent (this subdir contained only 4 `.md` files and no source code).
