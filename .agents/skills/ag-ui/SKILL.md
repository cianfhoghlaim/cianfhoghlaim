---
name: ag-ui
description: AG-UI — the open SSE-based protocol for agent↔UI streaming. Use when wiring any UI (CopilotKit, custom React) to any agent backend (Pydantic AI, Agno, Google ADK, BAML), decoding agent event streams, or defining custom events / shared state across the UI↔agent boundary.
---

# AG-UI — Agent-User Interaction Protocol

## When to use this skill

Use when you need to:

- "Wire a CopilotKit UI to my Pydantic AI / Agno / Google ADK
  / BAML agent"
- "Stream partial agent results (tokens, tool calls) to the
  UI as they're produced"
- "Define a custom event type that the UI subscribes to"
- "Sync shared state between the UI and the agent (form
  values, user preferences, in-flight data)"

## Overview

[AG-UI](https://ag-ui.com/) is an open protocol (CopilotKit
authored) that defines a standard wire format for agent↔UI
communication. It uses **Server-Sent Events (SSE)** as the
transport and a JSON event schema for the payload.

The key insight: agents and UIs are decoupled. The same agent
can be served to CopilotKit, a custom React UI, a Slack bot,
or a CLI — all via the same AG-UI event stream.

## Install

```bash
# TypeScript
bun add @ag-ui/core

# Python
uv add ag-ui

# Pydantic AI (built-in adapter)
uv add 'pydantic-ai-slim[ag-ui]'
```

## Wire format

AG-UI events are JSON-encoded SSE messages. The canonical event
types:

| Event | Payload | When |
|:--|:--|:--|
| `token` | `{ delta: str }` | Streaming a partial token |
| `tool_call` | `{ name, args }` | Agent is calling a tool |
| `tool_result` | `{ name, result }` | Tool returned a result |
| `state` | `{ key, value }` | Shared state update (form values, etc.) |
| `message` | `{ role, content }` | Complete message from agent |
| `done` | `{}` | Stream complete |

The full schema is at <https://ag-ui.com/spec>.

## Stack integration

The KCG stack uses AG-UI as the bridge between the UI (CopilotKit)
and the agent backends (Pydantic AI, Agno, Google ADK, BAML):

```
   ┌──────────────────┐
   │  CopilotKit      │  ← UI (oideachais/web, tuatha/ui,
   │  (React)         │    croilar/apps/portal)
   └────────┬─────────┘
            │ consumes SSE
            ▼
   ┌──────────────────┐
   │  Hono (oRPC)     │  ← API gateway
   │  /api/agent/...  │
   └────────┬─────────┘
            │ proxies SSE
            ▼
   ┌──────────────────┐
   │  AG-UI adapter   │  ← server-side adapter
   │  (per backend)   │
   └────────┬─────────┘
            │ calls
            ▼
   ┌──────────────────┐
   │  Agent           │  ← Pydantic AI / Agno / Google
   │                  │    ADK / BAML
   └──────────────────┘
```

The AG-UI server-side adapter is per-backend:

- **Pydantic AI** — `pydantic_ai.ui.ag_ui.AGUIAdapter`
- **Agno** — `agno.os.AGUIInterface` (AgentOS)
- **Google ADK** — `google.adk.ag_ui.adapter`
- **BAML** — hand-rolled (BAML functions stream via
  `b.stream.<Function>(...)`)

## Server side — Starlette / FastAPI handler

```python
from pydantic_ai import Agent
from pydantic_ai.ui.ag_ui import AGUIAdapter
from pydantic_ai.models.openai import OpenAIModel

agent = Agent(
    model=OpenAIModel("gpt-4o-mini"),
    system_prompt="You are a curriculum extraction agent.",
)
app = AGUIAdapter(agent).as_starlette_app()
```

Mount under any FastAPI app:

```python
from fastapi import FastAPI
app = FastAPI()
app.mount("/api/agent", app)
```

The SSE stream is now served at `POST /api/agent/...` and
compatible with any AG-UI client.

## Client side — CopilotKit

```typescript
import { CopilotChat } from "@copilotkit/react";

export function AgentChat() {
  return (
    <CopilotChat
      runtimeUrl="/api/agent"
      // CopilotKit auto-detects the AG-UI protocol
      // and handles SSE, tool calls, and shared state
    />
  );
}
```

CopilotKit auto-detects the AG-UI protocol from the response
headers and uses the appropriate transport.

## When to use AG-UI vs raw SSE / WebSockets

- **AG-UI**: any time the UI is CopilotKit, or you want
  standard agent events (tokens, tool calls, state)
- **Raw SSE**: custom protocols (e.g. streaming a video
  transcoding job)
- **WebSockets**: bidirectional, long-lived connections
  (e.g. live cursor sync, multiplayer)

For agent↔UI streaming, **always use AG-UI** unless you have
a strong reason not to. The CopilotKit integration is
first-class; rolling your own SSE handler duplicates effort.

## Custom events

AG-UI supports custom event types via a registry. The agent
backend emits them; the UI subscribes:

```python
# Server
from ag_ui import CustomEvent

@app.post("/api/agent/custom")
async def custom_event(request):
    yield CustomEvent(
        type="rag_chunk",
        payload={"doc_id": "...", "score": 0.92},
    )
```

```typescript
// Client (CopilotKit)
useAgUiEvent("rag_chunk", (payload) => {
  console.log("RAG chunk received:", payload);
});
```

Use custom events for: RAG chunk streaming, progress
indicators, intermediate tool results, multimodal artifacts
(images, audio), etc.

## KCG integration

- **oideachais/web** — `oideachais/web/src/lib/ag-ui/` (the
  canonical AG-UI client wrappers)
- **CopilotKit UI** — `oideachais/web/src/components/copilot/`
- **Hono (oRPC) proxy** — `oideachais/web/src/server/router.py`
- **Langfuse** — every AG-UI event is traced (token, tool_call,
  state, done) for full observability

## Resources

- AG-UI protocol spec: <https://ag-ui.com/spec>
- AG-UI docs: <https://ag-ui.com/>
- CopilotKit: <https://docs.copilotkit.ai/>
- Pydantic AI AG-UI adapter: <https://ai.pydantic.dev/ui/ag-ui>
- KCG AG-UI client: `oideachais/web/src/lib/ag-ui/`
