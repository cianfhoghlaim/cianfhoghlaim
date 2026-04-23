# Frontend Frameworks Capability

## Overview

Full-stack React frameworks, AI agent UI components, and modern frontend development with server-side rendering, streaming, and multi-agent support.

## Requirements

### Requirement: File-Based Routing
The system SHALL support automatic route generation from file structure.

#### Scenario: Basic Routes
- **GIVEN** a file-based routing system
- **WHEN** files are created in routes directory
- **THEN** routes are automatically generated

#### Scenario: Dynamic Routes
- **GIVEN** a route with dynamic parameters
- **WHEN** accessing a URL with parameters
- **THEN** parameters are extracted and available to the component

### Requirement: Server Functions
The system SHALL support type-safe server-side functions.

#### Scenario: RPC-Style Calls
- **GIVEN** a server function defined on the server
- **WHEN** called from the client
- **THEN** function executes on the server with type safety

#### Scenario: Input Validation
- **GIVEN** a server function with validators
- **WHEN** called with invalid input
- **THEN** validation fails with clear error messages

### Requirement: Server-Side Rendering
The system SHALL support SSR with streaming.

#### Scenario: Full SSR
- **GIVEN** a page with SSR enabled
- **WHEN** requested by a client
- **THEN** page is rendered on the server and sent as HTML

#### Scenario: Streaming Suspense
- **GIVEN** a page with async components
- **WHEN** loading data
- **THEN** UI progressively renders as data becomes available

### Requirement: AI Agent UI Integration
The system SHALL provide components for AI agent interfaces.

#### Scenario: Chat Interface
- **GIVEN** an AI chat component
- **WHEN** user sends messages
- **THEN** messages are displayed and agent responses are streamed

#### Scenario: Multi-Agent Support
- **GIVEN** multiple AI agents configured
- **WHEN** user interacts with the interface
- **THEN** appropriate agent is selected based on context

#### Scenario: Context Management
- **GIVEN** an AI agent with context needs
- **WHEN** user navigates the application
- **THEN** relevant context is provided to the agent

## Supported Frameworks

### TanStack Start (^1.94.0)

**Key Features:**
- File-based routing with automatic route tree generation
- Server functions with type-safe RPC-style calls
- SSR/Streaming with progressive UI rendering
- End-to-end TypeScript integration
- React Server Components for optimal performance
- Edge runtime support (Vercel, Cloudflare)
- Streaming Suspense boundaries
- TanStack Query, Store, and Router integration

**Documentation:** https://tanstack.com/start

**Skill:** [`.skills/tanstack-start/SKILL.md`](.skills/tanstack-start/SKILL.md)

### Vinxi (^0.5.1)

**Key Features:**
- Vite-powered for fast development
- File-based routing with automatic generation
- Server functions with type safety
- SSR/Streaming support
- Modular plugin-based architecture
- Multi-platform deployment (Vercel, Netlify, Cloudflare)

**Documentation:** https://vinxi.dev

**Skill:** [`.skills/vinxi/SKILL.md`](.skills/vinxi/SKILL.md)

### CopilotKit (>=0.1.0)

**Key Features:**
- Pre-built React components for AI interactions
- Easy integration with various AI agents
- Built-in state management for AI conversations
- Fully customizable components and themes
- Multi-agent support
- Side panel and text area components
- Context management for agents

**Documentation:** https://copilotkit.ai/docs

**Skill:** [`.skills/copilotkit/SKILL.md`](.skills/copilotkit/SKILL.md)

## File-Based Routing Patterns

### Basic Route

```typescript
// TanStack Start
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
  component: HomePage,
})

function HomePage() {
  return <div>Welcome</div>
}
```

### Dynamic Route

```typescript
// TanStack Start
export const Route = createFileRoute('/users/$userId')({
  component: UserPage,
  loader: async ({ params }) => {
    const user = await fetchUser(params.userId)
    return user
  },
})

function UserPage() {
  const user = Route.useLoaderData()
  return <h1>{user.name}</h1>
}
```

### Route File Naming

| Pattern | Route Path |
|---------|------------|
| `index.tsx` | `/` |
| `about.tsx` | `/about` |
| `users.tsx` | `/users` |
| `users/$userId.tsx` | `/users/:userId` |
| `posts.$postId.tsx` | `/posts/:postId` |
| `api.$.ts` | `/api/*` (catch-all) |

## Server Function Patterns

### Basic Server Function

```typescript
// TanStack Start
import { createServerFn } from '@tanstack/react-start'

const getTodos = createServerFn({
  method: 'GET',
}).handler(async () => {
  return await db.query.todos.findMany()
})
```

### Server Function with Validation

```typescript
// TanStack Start
const addTodo = createServerFn({ method: 'POST' })
  .inputValidator((d: { title: string }) => d)
  .handler(async ({ data }) => {
    await db.insert(todos).values({ title: data.title })
    return { success: true }
  })
```

### Vinxi Server Function

```typescript
// Vinxi
import { createServerFn } from 'vinxi/server'

export const hello = createServerFn({ method: 'GET' })
  .validator((name: string) => name)
  .handler(async ({ data: name }) => {
    return { message: `Hello, ${name}!` }
  })
```

## AI Agent UI Patterns

### Basic Chat Interface

```typescript
import { CopilotChat } from '@copilotkit/react-ui'

export default function ChatPage() {
  return (
    <CopilotChat
      instructions="You are a helpful assistant for education platform."
      labels={{
        initial: "How can I help you today?",
        placeholder: "Ask me anything...",
      }}
    />
  )
}
```

### Agent Integration

```typescript
import { useCopilotAction, useCopilotReadable } from '@copilotkit/react-core'

function CurriculumExplorer() {
  // Provide context to agent
  useCopilotReadable({
    description: "Current curriculum data",
    value: curriculumData,
  })

  // Define agent actions
  useCopilotAction({
    name: "search_curriculum",
    description: "Search curriculum for specific topics",
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

### Multi-Agent Setup

```typescript
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

### Side Panel

```typescript
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

## SSR and Streaming Patterns

### Full SSR

```typescript
// TanStack Start
export const Route = createFileRoute('/page')({
  component: PageComponent,
  loader: async () => await getData(),
})
```

### Data-Only SSR

```typescript
// TanStack Start
export const Route = createFileRoute('/page')({
  ssr: 'data-only',
  component: PageComponent,
  loader: async () => await getData(),
})
```

### Streaming Response

```typescript
import { createServerFn } from '@tanstack/react-start'

export const streamAI = createServerFn({
  method: 'POST',
  response: 'raw',
}).handler(async ({ data, signal }) => {
  const stream = new ReadableStream({
    async start(controller) {
      const response = await fetch('https://api.openai.com/v1/chat', {
        method: 'POST',
        body: JSON.stringify({ prompt: data.prompt }),
        signal,
      })

      const reader = response.body.getReader()
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        controller.enqueue(value)
      }
      controller.close()
    },
  })

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  })
})
```

## Best Practices

### Routing
1. **File Organization**: Use folders for related routes
2. **Index Routes**: Use `index.tsx` for directory roots
3. **Catch-All Routes**: Use `$.tsx` for 404 handling

### Server Functions
1. **Validation**: Use validators for input validation
2. **Error Handling**: Handle errors gracefully
3. **Type Safety**: Leverage TypeScript for type safety

### AI Agent UI
1. **Clear Instructions**: Provide clear instructions for each agent
2. **Context Management**: Only provide relevant context to agents
3. **Loading States**: Show loading states during agent processing

### Performance
1. **Code Splitting**: Use lazy loading for large components
2. **Streaming**: Enable streaming for slow data
3. **Caching**: Cache server function results
4. **Preloading**: Set `defaultPreload: 'intent'` for faster navigation

## Integration with Other Systems

### Agent Integration
- **Agno**: Backend agent framework for CopilotKit
- **Google ADK**: Multi-agent coordination for AI interfaces

### Data Pipeline Integration
- **Dagster**: Server functions as data pipeline assets
- **DLT**: Load data for AI-powered features

### Observability Integration
- **Langfuse**: Trace AI agent interactions in the UI
- **RAGAS**: Evaluate AI responses from the interface

## Deployment Platforms

| Platform | Framework Support | Notes |
|----------|-------------------|-------|
| Vercel | TanStack Start, Vinxi | Edge runtime support |
| Netlify | TanStack Start, Vinxi | Edge runtime support |
| Cloudflare | TanStack Start, Vinxi | Edge runtime support |
| Node.js | TanStack Start, Vinxi | Standard server runtime |

## Component Library

| Component | Purpose | Framework |
|-----------|---------|-----------|
| CopilotChat | AI chat interface | CopilotKit |
| CopilotSidebar | Side panel AI assistant | CopilotKit |
| CopilotTextarea | AI-powered text editor | CopilotKit |
| Link | Navigation | TanStack Start |
| Outlet | Route rendering | TanStack Start, Vinxi |

## Troubleshooting

### Route Not Found
- Check file naming conventions
- Run route tree generation command
- Verify route path matches file structure

### Server Function Errors
- Ensure server functions are in route files
- Check input validators match expected data shape
- Verify server-side dependencies are available

### SSR Hydration Mismatch
- Ensure server and client render same content
- Check for browser-only APIs in server code
- Use `useEffect` for client-only operations
