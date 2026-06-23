---
name: copilotkit
description: Expert assistance for building AI agent UIs with CopilotKit. Use when users need AI chat interfaces, agent UI components, or integrating AI agents into React applications.
---

# CopilotKit - AI Agent UI Framework

**Version:** >=0.1.0 | **Last Updated:** 2025-04

## Overview

CopilotKit is a framework for building AI-powered user interfaces:

- **React Components**: Pre-built UI components for AI interactions
- **Agent Integration**: Easy integration with various AI agents
- **State Management**: Built-in state management for AI conversations
- **Customizable**: Fully customizable components and themes
- **Multi-Agent Support**: Support for multiple AI agents

**Documentation**: https://copilotkit.ai/docs

## When to Use This Skill

Activate when users need:

- "Build an AI chat interface"
- "Create an AI agent UI"
- "Integrate AI agents into React"
- "Add AI-powered features to an app"
- "Build multi-agent interfaces"

## Core Concepts

### 1. Basic Setup

```bash
npm install @copilotkit/react-core @copilotkit/react-ui
```

### 2. Provider Setup

```tsx
// app/layout.tsx
import { CopilotKit } from '@copilotkit/react-core'
import '@copilotkit/react-ui/styles.css'

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <CopilotKit runtimeUrl="/api/copilotkit">
          {children}
        </CopilotKit>
      </body>
    </html>
  )
}
```

### 3. Chat Component

```tsx
import { CopilotChat } from '@copilotkit/react-ui'

export default function ChatPage() {
  return (
    <div className="h-screen">
      <CopilotChat
        instructions="You are a helpful assistant for the education platform."
        labels={{
          initial: "How can I help you today?",
          placeholder: "Ask me anything...",
        }}
      />
    </div>
  )
}
```

### 4. Agent Integration

```tsx
import { useCopilotAction, useCopilotReadable } from '@copilotkit/react-core'

function CurriculumExplorer() {
  // Provide context to the agent
  useCopilotReadable({
    description: "Current curriculum data",
    value: curriculumData,
  })

  // Define agent actions
  useCopilotAction({
    name: "search_curriculum",
    description: "Search the curriculum for specific topics",
    parameters: [
      {
        name: "query",
        type: "string",
        description: "Search query",
        required: true,
      },
    ],
    handler: async ({ query }) => {
      return await searchCurriculum(query)
    },
  })

  return <div>Curriculum Explorer</div>
}
```

### 5. Custom Components

```tsx
import { useCopilotChat } from '@copilotkit/react-core'

function CustomChat() {
  const { visibleMessages, appendMessage, isLoading } = useCopilotChat()

  return (
    <div className="chat-container">
      <div className="messages">
        {visibleMessages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      {isLoading && <div className="typing">Agent is typing...</div>}
    </div>
  )
}
```

### 6. Multi-Agent Setup

```tsx
import { CopilotKit } from '@copilotkit/react-core'

export default function MultiAgentApp() {
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agentDefinitions={[
        {
          name: "curriculum",
          description: "Expert in curriculum content",
          instructions: "You are a curriculum expert.",
        },
        {
          name: "assessment",
          description: "Expert in assessment creation",
          instructions: "You are an assessment specialist.",
        },
        {
          name: "tutor",
          description: "Expert in personalized tutoring",
          instructions: "You are a personalized tutor.",
        },
      ]}
    >
      <App />
    </CopilotKit>
  )
}
```

## Advanced Features

### Side Panel

```tsx
import { CopilotSidebar } from '@copilotkit/react-ui'

export default function Dashboard() {
  return (
    <div className="flex">
      <div className="main-content">
        {/* Main application */}
      </div>
      <CopilotSidebar
        defaultOpen={true}
        instructions="Help users navigate the dashboard and answer questions."
      />
    </div>
  )
}
```

### Text Area Integration

```tsx
import { CopilotTextarea } from '@copilotkit/react-ui'

function DocumentEditor() {
  return (
    <div>
      <CopilotTextarea
        placeholder="Write your document here..."
        instructions="Help the user write and improve their document."
        className="w-full h-96"
      />
    </div>
  )
}
```

### Context Management

```tsx
import { useCopilotReadable } from '@copilotkit/react-core'

function DataViewer({ data }) {
  // Multiple context sources
  useCopilotReadable({
    description: "User's current view",
    value: data,
  })

  useCopilotReadable({
    description: "User's permissions",
    value: userPermissions,
  })

  return <div>{/* Data visualization */}</div>
}
```

## Backend Integration

### Next.js API Route

```ts
// app/api/copilotkit/route.ts
import { CopilotRuntime, OpenAIAdapter } from '@copilotkit/runtime'
import { NextRequest } from 'next/server'

const copilotKit = new CopilotRuntime({
  adapters: [new OpenAIAdapter({ apiKey: process.env.OPENAI_API_KEY })],
})

export async function POST(req: NextRequest) {
  return await copilotKit.streamHttp(req)
}
```

### Custom Agent Handler

```ts
import { CopilotRuntime, copilotKitNextEndpoint } from '@copilotkit/runtime'

const runtime = new CopilotRuntime({
  actions: [
    {
      name: "get_curriculum",
      description: "Get curriculum information",
      parameters: {
        subject: { type: "string", description: "Subject name" },
      },
      handler: async ({ subject }) => {
        return await fetchCurriculum(subject)
      },
    },
  ],
})

export const POST = copilotKitNextEndpoint({ runtime })
```

## Best Practices

### UI Design

1. **Clear Instructions**: Provide clear instructions for each agent
2. **Context Management**: Only provide relevant context to agents
3. **Loading States**: Show loading states during agent processing

### Performance

1. **Debouncing**: Debounce user input for better performance
2. **Caching**: Cache agent responses when appropriate
3. **Lazy Loading**: Load components only when needed

### Security

1. **Input Validation**: Validate all user inputs
2. **API Key Protection**: Never expose API keys on the client
3. **Rate Limiting**: Implement rate limiting for agent calls

## Installation

```bash
npm install @copilotkit/react-core @copilotkit/react-ui
# or
yarn add @copilotkit/react-core @copilotkit/react-ui
```

## Project Integration

### Use Cases

| Scenario | Pattern |
|----------|---------|
| Education Platform | Multi-agent tutor + curriculum explorer |
| Document Editor | CopilotTextarea with AI assistance |
| Dashboard | CopilotSidebar for contextual help |
| Data Analysis | Chat interface with data context |

### Related Skills

- [`agno`](.skills/agno/SKILL.md) - Agent framework for backend
- [`google-adk`](.skills/google-adk/SKILL.md) - Google's agent framework
- [`tanstack-start`](.skills/tanstack-start/SKILL.md) - Full-stack React framework
- [`vinxi`](.skills/vinxi/SKILL.md) - Alternative full-stack framework

## Advanced context types (KCG)

CopilotKit supports rich context types for advanced UIs:

### Zustand state (client-side stores)

```typescript
import { useCoAgent } from "@copilotkit/react-core";

const { state, setState } = useCoAgent({
  name: "my_agent",
  initialState: { count: 0, items: [] },
});

// Sync the agent's state with a Zustand store
useEffect(() => {
  store.setState({ count: state.count, items: state.items });
}, [state.count, state.items]);
```

### Shared state between UI and agent

```typescript
const { state, setState } = useCoAgent({
  name: "tuatha_guide",
  initialState: {
    playerPosition: { x: 0, y: 0, z: 0 },
    inventory: [],
  },
});
// The agent can read + write `state`; the UI re-renders on changes
```

### Agent OS (Agno) integration

For the Tuatha MMO, the backend agent runs on Agno's AgentOS
(see `.agents/skills/agno/SKILL.md`). CopilotKit connects via
the `runtimeUrl` to the Agno AG-UI adapter:

```typescript
<CopilotChat runtimeUrl="https://agentos.cianfhoghlaim.ie/agui" />
```

The frontend is identical regardless of the backend agent
framework (Pydantic AI, Agno, Google ADK, BAML).
