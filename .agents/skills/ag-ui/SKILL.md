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

## The 17-event protocol (per the 2026-08-23 CopilotKit v2 + AG-UI protocol change)

The full AG-UI protocol defines 17 distinct event types. The KCG
canonical stack (CopilotKit v2 + `@copilotkit/react-core/v2` + `@ag-ui/core`
+ `@ag-ui/client`) implements all 17. New agents should be familiar
with these:

### Run lifecycle events (4)
- **`RunStarted`** — emitted when the agent invocation begins
- **`RunFinished`** — emitted on successful completion
- **`RunError`** — emitted on failure (carries the error message)
- **`StepStarted`** + **`StepFinished`** — emitted around each agent step (multi-step agents)

### Message events (3)
- **`TextMessageStart`** — emitted before a text message begins
- **`TextMessageContent`** — streams partial text content (replaces the legacy `token` event)
- **`TextMessageEnd`** — emitted when a text message completes

### Tool events (3)
- **`ToolCallStart`** — emitted before tool arguments are streamed
- **`ToolCallArgs`** — streams tool arguments (partial JSON)
- **`ToolCallEnd`** — emitted when tool arguments are complete

### Tool result events (1)
- **`ToolCallResult`** — emitted with the tool's return value

### State events (2)
- **`StateSnapshot`** — full state dump (initial or on demand)
- **`StateDelta`** — incremental state patch (JSON-Patch RFC 6902)

### Snapshot events (2)
- **`MessagesSnapshot`** — full messages array dump
- **`Raw`** — pass-through event (for non-standard payloads)

### Source + custom (2)
- **`Source`** — metadata about the message source (e.g., model ID)
- **`Custom`** — application-defined event (custom payload)

The 17 events replace the 6-event legacy wire format. Existing agents
that handle `token`/`tool_call` etc. should migrate to the explicit
event names. See
`.opencode/agents/copilotkit/skills/copilotkit-develop/SKILL.md` for
the v2 import patterns + the migration table.

## Stack integration

The KCG stack uses AG-UI as the bridge between the UI (CopilotKit)
and the agent backends (Pydantic AI, Agno, Google ADK, BAML):

```
   ┌──────────────────┐
   │  CopilotKit      │  ← UI (web/apps/cianfhoghlaim-web, web/apps/tuatha-ui,
   │  (React)         │    web/apps/croilar-portal)
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

- **web/apps/cianfhoghlaim-web** — `web/apps/cianfhoghlaim-web/src/lib/ag-ui/` (the
  canonical AG-UI client wrappers)
- **CopilotKit UI** — `web/apps/cianfhoghlaim-web/src/components/copilot/`
- **Hono (oRPC) proxy** — `web/apps/cianfhoghlaim-web/src/server/router.py`
- **Langfuse** — every AG-UI event is traced (token, tool_call,
  state, done) for full observability

## A2UI — sibling protocol (Google)

[A2UI](https://a2ui.org/) is Google's "native-first" alternative
to AG-UI for cross-platform generative UI. It's complementary
to AG-UI, not a replacement.

| Protocol | Transport | UI rendering | Best for |
|:--|:--|:--|:--|
| **AG-UI** | SSE | Host app renders component tree | React web (CopilotKit) |
| **A2UI** | JSON-RPC | Host app renders JSON component blueprint | Flutter / native mobile (Google SDKs) |
| **MCP-Apps** | JSON-RPC | Host app renders via MCP server | Desktop apps |

A2UI sends **JSON component blueprints** (not opaque HTML),
so the host app keeps its styling and accessibility. The host
app renders the components natively (no iframe, no script
injection).

A2UI is the canonical choice when the UI must inherit the
host app's styling on Flutter / iOS / Android — exactly
the Tuatha MMO mobile use case.

You can run A2UI *over* AG-UI / A2A as a transport, or
directly via a JSON-RPC endpoint.

## Kotlin mobile SDK (round-9 deep dive)

The **AG-UI Kotlin SDK** (community-contributed by Mark
Fogle, Nov 2025) brings the AG-UI protocol to Android, iOS,
and JVM through a single Kotlin Multiplatform SDK. For the
**Tuatha MMO mobile client** this is the canonical pattern —
the agent backend is the same regardless of whether the
client is web, native, or desktop.

The SDK is modular:

| Module | Purpose | Gradle dep |
|:--|:--|:--|
| `kotlin-client` | High-level agent clients + HTTP transport | `com.agui:kotlin-client:0.2.1` |
| `kotlin-core` | Protocol types, events, kotlinx.serialization | `com.agui:kotlin-core:0.2.1` |
| `kotlin-tools` | `ToolExecutor` + `ToolRegistry` + circuit-breaker | `com.agui:kotlin-tools:0.2.1` |

Platform support: Android API 26+, iOS 13+, JVM 11+.

**Quick start (stateful agent):**

```kotlin
val chatAgent = StatefulAgUiAgent("https://agent.tuatha.cianfhoghlaim.ie") {
    bearerToken = tuathaSession.token
    systemPrompt = "You are a Celtic mythology guide."
}

chatAgent.chat("Tell me about the Tuatha Dé Danann.").collect { state ->
    // state.messages updates as the SSE stream emits events
    // state.thinking surfaces THINKING_* events
    // state.errors contains any parse / network failures
}
```

**Client-side tools** (e.g. opening a quest log, showing
inventory) execute **on the device, not the server** — this
is the key privacy property:

```kotlin
val agent = agentWithTools(
    url = "https://agent.tuatha.cianfhoghlaim.ie",
    toolRegistry = toolRegistry {
        addTool(QuestLogToolExecutor())   // runs locally
        addTool(InventoryToolExecutor())  // runs locally
    }
) { bearerToken = tuathaSession.token }

agent.sendMessage("What quests do I have?").collect { state ->
    // Agent requested the local quest-log tool;
    // it ran on the device, not the server
}
```

**Authentication** is per-client: `bearerToken(...)`,
`apiKey(...)`, or `basicAuth(...)`. For the KCG stack, the
token is the SIWE session JWT from BetterAuth
(`agents/tuatha/auth/siwe.py`).

**Streamed events** are auto-rewritten: chunked
`TEXT_MESSAGE_CHUNK` / `TOOL_CALL_CHUNK` are expanded into
start/content/end sequences, and `THINKING_*` events are
surfaced alongside normal messages (so the UI can show a
"reasoning" indicator before the response).

## AG-UI vs A2UI vs MCP-UI vs Open-JSON-UI

AG-UI is **not** a generative UI specification — it is the
**bi-directional runtime connection** between an agent and
any UI. The generative UI specs (A2UI, MCP-UI, Open-JSON-UI)
sit on top of it:

| Spec | Origin | Purpose | Transport |
|:--|:--|:--|:--|
| **AG-UI** | CopilotKit | Agent↔UI runtime connection | SSE / WebSocket |
| **A2UI** | Google | JSON component blueprints (declarative) | JSONL streaming |
| **MCP-UI / MCP Apps** | Microsoft + Shopify | iframe-based, sandboxed UI | over MCP |
| **Open-JSON-UI** | OpenAI | OpenAI's internal declarative spec | JSON Schema |

The flow:

1. Agent generates a UI using a generative UI spec
   (e.g. A2UI), describing the components it wants
2. AG-UI transports that spec from the agent to the app
   over the bi-directional runtime
3. The app renders the components natively (no iframe, no
   script injection — host styling is preserved)
4. User interactions flow back through AG-UI to the agent

For the **Tuatha MMO mobile client**, A2UI is the canonical
choice when the UI must inherit the host's Celtic design
language on Flutter / iOS / Android. For web frontends,
CopilotKit's React renderer consumes AG-UI directly.

See `references/kotlin-mobile-sdk.md` for the blog
announcement and `references/kotlin-sdk-overview.md`
for the 191-line official Kotlin SDK reference.

## Resources

- AG-UI protocol spec: <https://ag-ui.com/spec>
- AG- docs: <https://ag-ui.com/>
- A2UI: <https://a2ui.org/>
- CopilotKit: <https://docs.copilotkit.ai/>
- Pydantic AI AG-UI adapter: <https://ai.pydantic.dev/ui/ag-ui>
- KCG AG-UI client: `web/apps/cianfhoghlaim-web/src/lib/ag-ui/`
- AG-UI Kotlin SDK: <https://github.com/ag-ui-protocol/ag-ui/tree/main/sdks/community/kotlin>
