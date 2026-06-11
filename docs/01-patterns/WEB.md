---
title: 'Pattern: Web Frameworks (TanStack, AG-UI, MCP-UI)'
domain: 'patterns'
status: 'stable'
description: '| Constraint | Description | Violation Consequence | |------------|-------------|----------------------| | **AG-UI: Handle all 17 events** | Implement complete event protocol | Dropped agent state, broken UI | | **SSE for streaming** | Use Server-Sent Events for agent output | Bu'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/WEB.md
ccc_query_hints:
  - pattern: web frameworks (tanstack, ag-ui
---

# Pattern: Web Frameworks (TanStack, AG-UI, MCP-UI)

## Critical Constraints

| Constraint | Description | Violation Consequence |
|------------|-------------|----------------------|
| **AG-UI: Handle all 17 events** | Implement complete event protocol | Dropped agent state, broken UI |
| **SSE for streaming** | Use Server-Sent Events for agent output | Buffered responses, poor UX |
| **Auth middleware** | Protect routes server-side | Security vulnerabilities |
| **Type-safe forms** | Use Zod + TanStack Form | Runtime validation errors |

---

## Architecture Overview

```
Agent Backend (FastAPI/Hono)
        ↓
Protocol Adapter
├── AG-UI (17 events)
├── MCP-UI (JSON-RPC)
└── TanStack AI (SSE)
        ↓
Frontend (React/TanStack Start)
        ↓
User Interface
```

---

## TanStack Patterns

### Pattern 1: Full-Stack App with Better Auth

**When to use**: Production applications with authentication.

**Project Structure**:
```
app/
├── routes/
│   ├── __root.tsx          # Root layout
│   ├── index.tsx           # Home page
│   ├── login.tsx           # Auth pages
│   ├── signup.tsx
│   └── protected/          # Auth-required routes
│       ├── dashboard.tsx
│       └── settings.tsx
├── components/
│   ├── auth/
│   │   ├── LoginForm.tsx
│   │   └── SignupForm.tsx
│   └── ui/                 # shadcn/ui components
├── lib/
│   ├── auth.ts             # Better Auth client
│   └── auth-client.ts      # React client hooks
└── server/
    └── auth.ts             # Server auth config
```

**Auth Configuration** (`lib/auth.ts`):
```typescript
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { db } from "./db";

export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg",
  }),
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false,
  },
  socialProviders: {
    google: {
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    },
    github: {
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    },
  },
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },
});
```

**Protected Route** (`routes/protected/dashboard.tsx`):
```typescript
import { createFileRoute, redirect } from "@tanstack/react-router";
import { authClient } from "@/lib/auth-client";

export const Route = createFileRoute("/protected/dashboard")({
  component: DashboardPage,
  beforeLoad: async ({ context }) => {
    const session = await authClient.getSession();
    if (!session.data) {
      throw redirect({ to: "/login" });
    }
    return { session: session.data };
  },
});

function DashboardPage() {
  const { session } = Route.useRouteContext();
  return (
    <div>
      <h1>Welcome, {session.user.name}</h1>
    </div>
  );
}
```

### Pattern 2: Type-Safe Forms with Zod

**When to use**: Any form input validation.

**Implementation**:
```typescript
import { useForm } from "@tanstack/react-form";
import { zodValidator } from "@tanstack/zod-form-adapter";
import { z } from "zod";

const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
});

type LoginFormData = z.infer<typeof loginSchema>;

function LoginForm() {
  const form = useForm({
    defaultValues: { email: "", password: "" } as LoginFormData,
    validatorAdapter: zodValidator(),
    validators: {
      onChange: loginSchema,
    },
    onSubmit: async ({ value }) => {
      await authClient.signIn.email({
        email: value.email,
        password: value.password,
      });
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        form.handleSubmit();
      }}
    >
      <form.Field name="email">
        {(field) => (
          <div>
            <input
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              placeholder="Email"
            />
            {field.state.meta.errors && (
              <span className="error">{field.state.meta.errors[0]}</span>
            )}
          </div>
        )}
      </form.Field>

      <form.Field name="password">
        {(field) => (
          <div>
            <input
              type="password"
              value={field.state.value}
              onChange={(e) => field.handleChange(e.target.value)}
              placeholder="Password"
            />
            {field.state.meta.errors && (
              <span className="error">{field.state.meta.errors[0]}</span>
            )}
          </div>
        )}
      </form.Field>

      <button type="submit" disabled={form.state.isSubmitting}>
        {form.state.isSubmitting ? "Signing in..." : "Sign In"}
      </button>
    </form>
  );
}
```

---

## AG-UI Protocol

### Pattern 3: AG-UI Event Handling

**When to use**: Agent-frontend communication with full state sync.

**17 Event Types**:

| Event | Direction | Purpose |
|-------|-----------|---------|
| `RUN_STARTED` | Agent→UI | Agent execution started |
| `RUN_FINISHED` | Agent→UI | Agent execution complete |
| `RUN_ERROR` | Agent→UI | Agent error occurred |
| `TEXT_MESSAGE_START` | Agent→UI | Text generation started |
| `TEXT_MESSAGE_CONTENT` | Agent→UI | Streaming text chunk |
| `TEXT_MESSAGE_END` | Agent→UI | Text generation complete |
| `TOOL_CALL_START` | Agent→UI | Tool execution started |
| `TOOL_CALL_ARGS` | Agent→UI | Tool arguments (streaming) |
| `TOOL_CALL_END` | Agent→UI | Tool execution complete |
| `STATE_SNAPSHOT` | Agent→UI | Full state snapshot |
| `STATE_DELTA` | Agent→UI | Incremental state update |
| `MESSAGES_SNAPSHOT` | Agent→UI | Full message history |
| `RAW` | Agent→UI | Raw data passthrough |
| `CUSTOM` | Agent→UI | Custom event type |
| `STEP_STARTED` | Agent→UI | Multi-step workflow step |
| `STEP_FINISHED` | Agent→UI | Step complete |
| `USER_INPUT` | UI→Agent | User provided input |

**Frontend Handler**:
```typescript
import { AGUIClient, AGUIEvent, EventType } from "@ag-ui/client";

function useAgentChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [currentText, setCurrentText] = useState("");

  const client = useMemo(() => new AGUIClient({
    endpoint: "/api/agent",
  }), []);

  const handleEvent = useCallback((event: AGUIEvent) => {
    switch (event.type) {
      case EventType.RUN_STARTED:
        setIsRunning(true);
        setCurrentText("");
        break;

      case EventType.TEXT_MESSAGE_CONTENT:
        setCurrentText((prev) => prev + event.content);
        break;

      case EventType.TEXT_MESSAGE_END:
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: currentText },
        ]);
        setCurrentText("");
        break;

      case EventType.TOOL_CALL_START:
        // Show tool execution indicator
        console.log(`Calling tool: ${event.toolName}`);
        break;

      case EventType.TOOL_CALL_END:
        // Show tool result
        console.log(`Tool result: ${event.result}`);
        break;

      case EventType.RUN_FINISHED:
        setIsRunning(false);
        break;

      case EventType.RUN_ERROR:
        setIsRunning(false);
        console.error("Agent error:", event.error);
        break;

      case EventType.STATE_DELTA:
        // Handle state updates
        break;
    }
  }, [currentText]);

  const sendMessage = useCallback(async (content: string) => {
    setMessages((prev) => [...prev, { role: "user", content }]);
    await client.run({ message: content }, handleEvent);
  }, [client, handleEvent]);

  return { messages, isRunning, currentText, sendMessage };
}
```

**Backend Adapter** (FastAPI):
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from ag_ui import AGUIProtocol, Event, EventType

app = FastAPI()

@app.post("/api/agent")
async def agent_endpoint(request: dict):
    """AG-UI compatible agent endpoint."""

    async def event_generator():
        protocol = AGUIProtocol()

        # Run started
        yield protocol.encode(Event(type=EventType.RUN_STARTED))

        try:
            # Stream text response
            yield protocol.encode(Event(
                type=EventType.TEXT_MESSAGE_START,
                message_id="msg_1",
            ))

            async for chunk in agent.stream(request["message"]):
                yield protocol.encode(Event(
                    type=EventType.TEXT_MESSAGE_CONTENT,
                    message_id="msg_1",
                    content=chunk,
                ))

            yield protocol.encode(Event(
                type=EventType.TEXT_MESSAGE_END,
                message_id="msg_1",
            ))

            # Run finished
            yield protocol.encode(Event(type=EventType.RUN_FINISHED))

        except Exception as e:
            yield protocol.encode(Event(
                type=EventType.RUN_ERROR,
                error=str(e),
            ))

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )
```

---

## MCP-UI Protocol

### Pattern 4: MCP Component Registry

**When to use**: Claude/AI assistant component installation.

**Server Configuration** (`.mcp.json`):
```json
{
  "mcpServers": {
    "shadcn": {
      "command": "npx",
      "args": ["shadcn@latest", "mcp"]
    },
    "custom-registry": {
      "command": "node",
      "args": ["./mcp-server/index.js"]
    }
  }
}
```

**Custom MCP Server**:
```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({
  name: "component-registry",
  version: "1.0.0",
});

// List available components
server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "browse_components",
      description: "Browse available UI components",
      inputSchema: {
        type: "object",
        properties: {
          category: { type: "string" },
        },
      },
    },
    {
      name: "install_component",
      description: "Install a component to the project",
      inputSchema: {
        type: "object",
        properties: {
          name: { type: "string" },
          path: { type: "string" },
        },
        required: ["name"],
      },
    },
  ],
}));

// Handle tool calls
server.setRequestHandler("tools/call", async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "browse_components") {
    const components = await fetchComponents(args.category);
    return { content: [{ type: "text", text: JSON.stringify(components) }] };
  }

  if (name === "install_component") {
    await installComponent(args.name, args.path);
    return { content: [{ type: "text", text: `Installed ${args.name}` }] };
  }
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

---

## CopilotKit Patterns

### Pattern 5: Agent State Rendering

**When to use**: Dynamic UI based on agent state.

**Implementation**:
```typescript
import {
  useCopilotAction,
  useCopilotReadable,
  useCoAgentStateRender,
} from "@copilotkit/react-core";

function WeatherDashboard() {
  const [weather, setWeather] = useState<WeatherData | null>(null);

  // Make data readable to agent
  useCopilotReadable({
    description: "Current weather data",
    value: weather,
  });

  // Define agent action
  useCopilotAction({
    name: "updateWeather",
    description: "Update the weather display",
    parameters: [
      { name: "city", type: "string", required: true },
    ],
    handler: async ({ city }) => {
      const data = await fetchWeather(city);
      setWeather(data);
      return `Updated weather for ${city}`;
    },
  });

  // Render based on agent state
  useCoAgentStateRender({
    name: "weather_agent",
    render: ({ state }) => (
      <WeatherCard
        city={state.city}
        temperature={state.temperature}
        conditions={state.conditions}
      />
    ),
  });

  return (
    <div>
      <h1>Weather Dashboard</h1>
      {weather && <WeatherCard {...weather} />}
    </div>
  );
}
```

### Pattern 6: Human-in-the-Loop Actions

**When to use**: Approval gates for agent actions.

**Implementation**:
```typescript
import { useCopilotAction } from "@copilotkit/react-core";

function DataManager() {
  useCopilotAction({
    name: "deleteRecords",
    description: "Delete records from database",
    parameters: [
      { name: "ids", type: "string[]", required: true },
      { name: "reason", type: "string", required: true },
    ],
    // Require human approval
    renderAndWait: ({ args, status, handler }) => (
      <div className="approval-dialog">
        <h3>Confirm Deletion</h3>
        <p>Delete {args.ids.length} records?</p>
        <p>Reason: {args.reason}</p>
        <div className="actions">
          <button onClick={() => handler.approve()}>Approve</button>
          <button onClick={() => handler.reject("User cancelled")}>
            Cancel
          </button>
        </div>
      </div>
    ),
    handler: async ({ ids, reason }) => {
      await deleteRecords(ids, reason);
      return `Deleted ${ids.length} records`;
    },
  });

  return <div>Data Manager</div>;
}
```

---

## Streaming Patterns

### Pattern 7: Server-Sent Events (SSE)

**When to use**: Any streaming agent output.

**Backend** (FastAPI):
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import json

app = FastAPI()

@app.get("/api/stream")
async def stream_endpoint():
    async def generate():
        async for chunk in agent.stream("query"):
            # SSE format
            data = json.dumps({"content": chunk})
            yield f"data: {data}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
```

**Frontend**:
```typescript
async function* streamResponse(url: string, body: object) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const reader = response.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data === "[DONE]") return;
        yield JSON.parse(data);
      }
    }
  }
}

// Usage
for await (const chunk of streamResponse("/api/stream", { query })) {
  console.log(chunk.content);
}
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Missing AG-UI event handlers | Implement all 17 event types |
| No SSE for streaming | Use StreamingResponse + text/event-stream |
| Client-side auth checks only | Add server-side middleware |
| No form validation | Use Zod + TanStack Form |
| Blocking I/O in streams | Use async generators |
| Missing error boundaries | Wrap components with error handling |
| No loading states | Show spinners during agent runs |

---

## References

- Source: `taighde/web/tanstack/`, `taighde/web/AG-UI Overview.md`
- Skills: `.claude/skills/tanstack-start/`, `.claude/skills/copilotkit/`
- Documentation: https://tanstack.com/start, https://docs.ag-ui.com
- Examples: `sruth/browser/frontend/`, `sruth/oideachais/api/`
