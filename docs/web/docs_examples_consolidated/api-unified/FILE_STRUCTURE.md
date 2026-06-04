# File Structure Reference

Complete file structure for the API Unified project with descriptions.

```
api-unified/
│
├── 📄 package.json              # Dependencies and scripts
├── 📄 tsconfig.json            # TypeScript configuration
├── 📄 .env.example             # Environment variable template
├── 📄 .gitignore               # Git ignore patterns
│
├── 📚 Documentation
│   ├── 📄 README.md            # Main documentation (comprehensive)
│   ├── 📄 QUICKSTART.md        # Get started in 5 minutes
│   ├── 📄 ARCHITECTURE.md      # Technical deep dive
│   ├── 📄 PROJECT_SUMMARY.md   # High-level overview
│   └── 📄 FILE_STRUCTURE.md    # This file
│
├── 📁 contracts/               # Shared data schemas (SINGLE SOURCE OF TRUTH)
│   └── 📄 schemas.ts           # All Zod schemas
│       ├── UserSchema          # User data structure
│       ├── TodoSchema          # Todo data structure
│       ├── AuthSchemas         # Authentication schemas
│       ├── MCPToolSchemas      # MCP tool parameter schemas
│       └── ChatSchemas         # AI chat message schemas
│
├── 📁 src/                     # Source code
│   │
│   ├── 📄 index.ts             # Main application entry point
│   │   ├── Hono app setup
│   │   ├── Middleware (CORS, logging, pretty JSON)
│   │   ├── MCP endpoint configuration
│   │   ├── oRPC handler setup
│   │   ├── OpenAPI handler setup
│   │   ├── AI chat endpoints
│   │   └── Server startup
│   │
│   ├── 📁 mcp/                 # Model Context Protocol (AI tools)
│   │   │
│   │   ├── 📄 server.ts        # MCP server configuration
│   │   │   ├── Create McpServer instance
│   │   │   ├── Register tools
│   │   │   └── Register resources
│   │   │
│   │   ├── 📁 tools/
│   │   │   └── 📄 index.ts     # MCP tool definitions
│   │   │       ├── add - Add two numbers
│   │   │       ├── search - Search knowledge base
│   │   │       ├── analyzeText - Text analysis
│   │   │       ├── getCurrentTime - Get server time
│   │   │       └── listResources - List available resources
│   │   │
│   │   └── 📁 handlers/
│   │       └── 📄 streamable-http.ts  # MCP request handler
│   │           └── Handle Streamable-HTTP protocol
│   │
│   ├── 📁 rpc/                 # oRPC (Type-safe RPC)
│   │   │
│   │   ├── 📄 router.ts        # Main router definition
│   │   │   ├── Export AppRouter type
│   │   │   ├── todo.* procedures
│   │   │   ├── auth.* procedures
│   │   │   └── public.* procedures
│   │   │
│   │   └── 📁 procedures/
│   │       └── 📄 index.ts     # All procedure implementations
│   │           ├── Base procedures (public, authed)
│   │           ├── Todo procedures (create, list, update, delete)
│   │           ├── Auth procedures (signup, signin, me)
│   │           └── Public procedures (health, info)
│   │
│   └── 📁 ai/                  # AI streaming chat
│       └── 📄 chat.ts          # Chat handler implementations
│           ├── handleChatStream - Basic streaming
│           └── handleChatWithTools - Chat + tool calling
│
└── 📁 examples/                # Usage examples and tests
    │
    ├── 📄 client.ts            # TypeScript client examples
    │   ├── oRPC client usage
    │   ├── MCP client usage
    │   ├── AI chat streaming
    │   └── REST API via fetch
    │
    ├── 📄 curl-examples.sh     # cURL command examples
    │   ├── Root endpoint
    │   ├── OpenAPI endpoints
    │   ├── Authentication
    │   ├── Todo operations
    │   ├── MCP tool calling
    │   └── AI chat
    │
    └── 📄 test-all-endpoints.ts  # Comprehensive test suite
        ├── Test root endpoints
        ├── Test public endpoints
        ├── Test auth endpoints
        ├── Test todo endpoints
        ├── Test MCP tools
        ├── Test documentation
        └── Test AI chat (optional)
```

## File Descriptions

### Root Files

| File | Purpose |
|------|---------|
| `package.json` | Project dependencies, scripts, and metadata |
| `tsconfig.json` | TypeScript compiler configuration |
| `.env.example` | Template for environment variables |
| `.gitignore` | Git ignore patterns (node_modules, dist, .env) |

### Documentation Files

| File | Purpose | When to Read |
|------|---------|--------------|
| `README.md` | Complete documentation | First-time setup, reference |
| `QUICKSTART.md` | Get started quickly | Just want to run it |
| `ARCHITECTURE.md` | Technical deep dive | Understanding internals |
| `PROJECT_SUMMARY.md` | High-level overview | Understanding the "why" |
| `FILE_STRUCTURE.md` | This file | Understanding organization |

### Source Code

#### `contracts/schemas.ts`
- **Single source of truth** for all data structures
- Used by MCP, oRPC, OpenAPI, and TypeScript
- Zod schemas with full validation rules

#### `src/index.ts`
- Main application entry point
- Configures all endpoints and middleware
- Exports server instance

#### `src/mcp/`
- **MCP server configuration** (`server.ts`)
- **Tool definitions** (`tools/index.ts`)
- **HTTP handler** (`handlers/streamable-http.ts`)

#### `src/rpc/`
- **Router definition** (`router.ts`)
- **Procedure implementations** (`procedures/index.ts`)
- Includes auth middleware and error handling

#### `src/ai/`
- **Chat handlers** (`chat.ts`)
- Streaming support
- Tool calling integration

### Examples

#### `examples/client.ts`
Demonstrates:
- oRPC client with full types
- MCP client for tool calling
- AI chat streaming
- REST API usage

#### `examples/curl-examples.sh`
Provides:
- Ready-to-run cURL commands
- Examples for all endpoints
- Authentication examples
- Output formatting with jq

#### `examples/test-all-endpoints.ts`
Features:
- Automated endpoint testing
- Success/failure tracking
- Comprehensive coverage
- Summary reporting

## Import Patterns

### Within Source Code

```typescript
// Import shared schemas (from contracts/)
import { TodoSchema, UserSchema } from '../contracts/schemas.js';

// Import from same directory
import { createMcpServer } from './mcp/server.js';

// Import from subdirectory
import { registerTools } from './mcp/tools/index.js';
```

### From Examples

```typescript
// Import type from router (for oRPC client)
import type { AppRouter } from '../src/rpc/router.js';

// Import schemas (for validation)
import { ChatRequestSchema } from '../contracts/schemas.js';
```

## Script Commands

Defined in `package.json`:

| Command | Purpose |
|---------|---------|
| `npm run dev` | Start development server with watch mode |
| `npm run build` | Build TypeScript to JavaScript |
| `npm start` | Run built JavaScript in production |
| `npm run type-check` | Check types without building |
| `npm run test:endpoints` | Run comprehensive endpoint tests |
| `npm run examples:client` | Run TypeScript client examples |
| `npm run examples:curl` | Run cURL examples script |

## Environment Variables

Configured in `.env` (copy from `.env.example`):

| Variable | Required | Purpose |
|----------|----------|---------|
| `PORT` | No | Server port (default: 3000) |
| `ANTHROPIC_API_KEY` | Yes* | Anthropic API key for AI chat |
| `DEFAULT_MODEL` | No | Default Claude model |
| `DEBUG` | No | Enable debug logging |

*Required for AI chat endpoints only

## Build Output

After running `npm run build`:

```
api-unified/
├── dist/                    # Compiled JavaScript
│   ├── src/
│   │   ├── index.js
│   │   ├── mcp/
│   │   ├── rpc/
│   │   └── ai/
│   └── contracts/
│       └── schemas.js
```

## Generated at Runtime

When server is running:

- **OpenAPI Spec**: Available at `GET /api/~openapi.json`
- **Swagger UI**: Available at `GET /api/~docs`
- **In-Memory Data**: Users and Todos stored in Maps

## Key Patterns

### 1. Schema-First Design
```
contracts/schemas.ts (define once)
           ↓
Used by: MCP + oRPC + OpenAPI + TypeScript
```

### 2. Layered Architecture
```
HTTP Request
    ↓
Hono Middleware
    ↓
Protocol Handler (MCP/oRPC/OpenAPI)
    ↓
Business Logic (Procedures/Tools)
    ↓
Data Layer (Maps/Database)
```

### 3. Type Flow
```
Zod Schema
    ↓
TypeScript Type (inferred)
    ↓
oRPC Router
    ↓
Client Type (generated)
```

## Extension Points

### Adding a New MCP Tool
1. Add schema to `contracts/schemas.ts`
2. Register tool in `src/mcp/tools/index.ts`

### Adding a New oRPC Procedure
1. Add schemas to `contracts/schemas.ts`
2. Implement in `src/rpc/procedures/index.ts`
3. Export from `src/rpc/router.ts`

### Adding a New Endpoint
1. Add route in `src/index.ts`
2. Create handler function
3. Add documentation

## Dependencies

### Production
- `hono` - Web framework
- `@modelcontextprotocol/sdk` - MCP server
- `@orpc/server` - oRPC server
- `@orpc/openapi` - OpenAPI generation
- `ai` - AI SDK
- `@ai-sdk/anthropic` - Anthropic provider
- `zod` - Schema validation

### Development
- `typescript` - Type checking
- `tsx` - TypeScript execution
- `@types/node` - Node.js types

## File Sizes (Approximate)

| Category | Lines of Code | Files |
|----------|---------------|-------|
| Source Code | ~800 | 8 |
| Schemas | ~200 | 1 |
| Examples | ~600 | 3 |
| Documentation | ~2000 | 5 |
| Config | ~100 | 3 |
| **Total** | **~3700** | **20** |

## Quick Reference

### Core Files to Understand
1. `contracts/schemas.ts` - Data structures
2. `src/index.ts` - App configuration
3. `src/rpc/router.ts` - API structure
4. `README.md` - Full documentation

### Files to Customize
1. `contracts/schemas.ts` - Your data models
2. `src/rpc/procedures/index.ts` - Your business logic
3. `src/mcp/tools/index.ts` - Your AI tools
4. `.env` - Your configuration

### Files to Reference
1. `examples/client.ts` - How to use the API
2. `examples/curl-examples.sh` - How to test
3. `ARCHITECTURE.md` - How it works
4. `QUICKSTART.md` - How to get started
