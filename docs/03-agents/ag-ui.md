---
title: 'AG-UI — Agent-User Interaction Protocol (SSE)'
domain: 'agents'
status: 'stable'
description: 'AG-UI is an open protocol for agent-user interaction based on Server-Sent Events (SSE). It defines a standard format for streaming agent responses, tool calls, status updates, and structured outputs from AI agents to user interfaces — enabling any UI to connect to any agent backe'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/ag-ui.md
ccc_query_hints:
  - ag-ui — agent-user interaction protocol 
---

# AG-UI — Agent-User Interaction Protocol (SSE)

## Overview

AG-UI is an open protocol for agent-user interaction based on Server-Sent Events (SSE). It defines a standard format for streaming agent responses, tool calls, status updates, and structured outputs from AI agents to user interfaces — enabling any UI to connect to any agent backend with a common protocol.

## Why This Matters for Kings' College Galway

The curriculum platform's AI tutor needs to communicate with the CopilotKit chat UI across different layers: the web app (TanStack Start), the API layer (Hono), and the agent backend (Agno/Google ADK/BAML). AG-UI provides the SSE-based protocol that connects these layers — the agent streams partial responses as they're generated, tool call results as they complete, and structured curriculum data as it's extracted. This protocol decouples the AI backend from the UI, so the same agent can serve the web app, the mobile app, and CLI tools.

## Key Features

- **SSE-based** — Standard Server-Sent Events protocol
- **Streaming responses** — Token-by-token agent output
- **Tool call events** — Structured tool invocation and result events
- **Status updates** — Agent progress and error reporting
- **UI-agnostic** — Works with any frontend framework

## Installation

```bash
bun add @ag-ui/core  # TypeScript
# or
uv add ag-ui  # Python
```

## Integration with Our Stack

AG-UI connects the CopilotKit React components to the Hono API server, which routes to the Agno/Google ADK agent backends. The LiteLLM gateway traces all AG-UI events through Langfuse. The protocol is defined in `oideachais/web/src/lib/ag-ui/`.

## Upstream

- **Repository**: <https://github.com/ag-ui-protocol/ag-ui>
- **Documentation**: <https://ag-ui.com>
- **Latest**: Active development — multi-agent event routing, structured output support, CopilotKit integration

## Screenshot

AG-UI is a protocol, not a UI. SSE events appear in browser DevTools under the Network tab as a persistent EventStream. The CopilotKit chat UI renders AG-UI events as streaming text with tool call indicators. The Langfuse trace view shows AG-UI events as nested spans.
