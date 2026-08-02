# API Unified

A comprehensive example demonstrating how to build a unified API server that combines:

- **MCP (Model Context Protocol)** - AI tool calling interface
- **oRPC** - Type-safe RPC with auto-generated clients
- **OpenAPI** - Auto-generated REST API with Swagger documentation
- **AI Streaming** - Chat endpoints with streaming support

All running in a single Hono application.

## 📚 Documentation

- **[QUICKSTART.md](./QUICKSTART.md)** - Get started in 5 minutes
- **[PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)** - High-level overview and key concepts
- **[ARCHITECTURE.md](./ARCHITECTURE.md)** - Deep technical dive into the architecture
- **[FILE_STRUCTURE.md](./FILE_STRUCTURE.md)** - Complete file structure reference
- **[README.md](./README.md)** - This file (comprehensive usage guide)

## Features

### 🤖 MCP - Model Context Protocol

Server endpoint: `POST /mcp`

**Available Tools:**
- `add` - Add two numbers together
- `search` - Search the knowledge base
- `analyzeText` - Text analysis with entities and sentiment
- `getCurrentTime` - Get current server time
- `listResources` - List available resources

**Available Resources:**
- `resource://todos` - Access to todos list

### 🔌 oRPC - Type-safe RPC

Base endpoint: `/rpc/*`

**Procedures:**
```typescript
router = {
  todo: {
    create: (input: CreateTodo) => Todo
    list: (input: { limit: number, completed?: boolean }) => Todo[]
    update: (input: UpdateTodo) => Todo
    delete: (input: { id: string }) => { success: boolean }
  },
  auth: {
    signup: (input: NewUser) => Token
    signin: (input: Credential) => Token
    me: () => User
  },
  public: {
    health: () => HealthStatus
    info: () => ServerInfo
  }
}
```

### 📚 OpenAPI - REST API + Docs

Base endpoint: `/api/*`

- OpenAPI Spec: `/api/~openapi.json`
- Swagger UI: `/api/~docs`

All oRPC procedures are automatically exposed as REST endpoints with:
- Smart parameter coercion
- Type-safe validation
- Auto-generated documentation
- Interactive API explorer

### 💬 AI Chat - Streaming Responses

**Endpoints:**
- `POST /ai/chat` - Basic streaming chat
- `POST /ai/chat-with-tools` - Chat with tool calling support

**Request Format:**
```json
{
  "messages": [
    { "role": "user", "content": "Hello!" }
  ],
  "model": "claude-3-5-sonnet-20241022",
  "temperature": 0.7
}
```

## Project Structure

```
api-unified/
├── contracts/
│   └── schemas.ts              # Shared Zod schemas for validation
├── src/
│   ├── index.ts                # Main Hono app with all endpoints
│   ├── mcp/
│   │   ├── server.ts           # MCP server configuration
│   │   ├── tools/
│   │   │   └── index.ts        # MCP tool definitions
│   │   └── handlers/
│   │       └── streamable-http.ts  # MCP request handler
│   ├── rpc/
│   │   ├── router.ts           # oRPC router definition
│   │   └── procedures/
│   │       └── index.ts        # Typed RPC procedures
│   └── ai/
│       └── chat.ts             # AI streaming chat handlers
├── package.json
├── tsconfig.json
└── README.md
```

## Installation

```bash
npm install
```

## Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Required environment variables:
- `ANTHROPIC_API_KEY` - Your Anthropic API key for AI chat endpoints

## Usage

### Development

```bash
npm run dev
```

Server will start on `http://localhost:3000`

### Production

```bash
npm run build
npm start
```

## Example Requests

### MCP - Call a Tool

```bash
curl -X POST http://localhost:3000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "add",
      "arguments": { "a": 5, "b": 3 }
    }
  }'
```

### oRPC - Create Todo

```bash
curl -X POST http://localhost:3000/rpc/todo/create \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer token-1" \
  -d '{
    "title": "Build awesome app",
    "description": "Using MCP and oRPC together"
  }'
```

### OpenAPI - Get Health

```bash
curl http://localhost:3000/api/public/health
```

### AI Chat - Stream Response

```bash
curl -X POST http://localhost:3000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      { "role": "user", "content": "Explain MCP in one sentence" }
    ]
  }'
```

## Pattern Highlights

### 1. Shared Schemas with Zod

All data validation uses Zod schemas in `contracts/schemas.ts`, shared between:
- MCP tool parameters
- oRPC procedure inputs/outputs
- AI chat requests
- OpenAPI definitions

### 2. Type-Safe RPC with Auto-Generated REST

oRPC procedures are defined once and exposed as both:
- Type-safe RPC endpoints at `/rpc/*`
- Auto-generated REST endpoints at `/api/*`

### 3. Modern MCP Protocol

Uses the new Streamable-HTTP protocol (replaced SSE in summer 2025):
- Better performance
- Simpler implementation
- Native HTTP support

### 4. AI Streaming with Tool Calling

AI chat endpoints support:
- Streaming responses for better UX
- Optional tool calling integration
- Conversation history
- Multiple model support

## Client Usage

### TypeScript Client (oRPC)

```typescript
import { createClient } from '@orpc/client';
import type { AppRouter } from './src/rpc/router';

const client = createClient<AppRouter>({
  baseURL: 'http://localhost:3000/rpc',
  headers: {
    Authorization: 'Bearer token-1'
  }
});

// Fully typed!
const todo = await client.todo.create({
  title: 'Type-safe todo',
  description: 'With auto-complete!'
});

const todos = await client.todo.list({ limit: 10 });
```

### MCP Client

```typescript
import { McpClient } from '@modelcontextprotocol/sdk/client/mcp.js';

const client = new McpClient({
  endpoint: 'http://localhost:3000/mcp'
});

await client.connect();

const result = await client.callTool('add', { a: 5, b: 3 });
```

### AI Chat Client

```typescript
const response = await fetch('http://localhost:3000/ai/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Hello!' }]
  })
});

const reader = response.body.getReader();
// Stream the response
```

## Technologies Used

- **[Hono](https://hono.dev/)** - Fast, lightweight web framework
- **[@modelcontextprotocol/sdk](https://github.com/modelcontextprotocol/sdk)** - MCP server implementation
- **[@orpc/server](https://orpc.unnoq.com/)** - Type-safe RPC framework
- **[@orpc/openapi](https://orpc.unnoq.com/)** - OpenAPI generation for oRPC
- **[ai](https://sdk.vercel.ai/)** - AI streaming utilities
- **[@ai-sdk/anthropic](https://sdk.vercel.ai/)** - Anthropic provider
- **[zod](https://zod.dev/)** - TypeScript-first schema validation

## Benefits of This Architecture

1. **Single Source of Truth**: Schemas defined once, used everywhere
2. **Type Safety**: End-to-end TypeScript types from server to client
3. **Multiple Interfaces**: Same logic exposed via MCP, RPC, and REST
4. **Auto-Generated Docs**: OpenAPI spec and Swagger UI created automatically
5. **Modern Protocols**: Uses latest MCP Streamable-HTTP protocol
6. **AI-Ready**: Built-in support for AI tool calling and streaming
7. **Developer Experience**: Great DX with auto-complete and type checking

## License

MIT

## Related Examples

- `/web/examples-working/mcp/mcp-ui-on-tanstack` - MCP-UI integration
- `/web/examples-working/mcp/remote-mcp-github-oauth` - OAuth with MCP
- `/web/examples-working/orpc/orpc_query` - oRPC patterns
- `/web/examples-working/orpc/learn-orpc` - OpenAPI generation
