# @cianfhoghlaim/api-client — TanStack AI + CopilotKit v2 + AG-UI

Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1**
openspec change. The canonical frontend client stack for the
Cianfhoghlaim platform. Consolidates the 3 previous CopilotKit
installs + the 3 previous TanStack Query installs into one.

## What's included

- **TanStack AI** (`@tanstack/ai`) — LLM integration via the
  `useChat` React hook
- **TanStack DB** (`@tanstack/db`) — reactive queries via `useLiveQuery`
- **TanStack Form** (`@tanstack/react-form`) — form state management
- **CopilotKit v2** (`@copilotkit/react-core`,
  `@copilotkit/runtime-client-gql`) — agent chat + generative UI
- **AG-UI client** (`@ag-ui/client`) — the Agent-User Interaction
  protocol client

## Setup

```bash
bun add @cianfhoghlaim/api-client
```

## Usage

### Canonical AG-UI agent client

```tsx
import { createCianfhoghlaimAgent } from "@cianfhoghlaim/api-client";

export function CianfhoghlaimChat() {
  const agent = createCianfhoghlaimAgent();
  return <MyChat agent={agent} />;
}
```

### TanStack AI chat

```tsx
import { useCianfhoghlaimChat } from "@cianfhoghlaim/api-client";

export function Chat() {
  const { messages, send } = useCianfhoghlaimChat();
  return <MessageList messages={messages} />;
}
```

### TanStack DB reactive queries

```tsx
import { useCianfhoghlaimLiveQuery } from "@cianfhoghlaim/api-client";

export function SubjectList() {
  const [subjects] = useCianfhoghlaimLiveQuery(() => api.subjects.list());
  return <ul>{subjects?.map(s => <li>{s}</li>)}</ul>;
}
```

### TanStack Form

```tsx
import { useCianfhoghlaimForm } from "@cianfhoghlaim/api-client";

export function SignUpForm() {
  const form = useCianfhoghlaimForm(schema, { defaultValues: { ... } });
  return <form>...</form>;
}
```
