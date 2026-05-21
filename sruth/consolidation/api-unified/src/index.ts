import { Hono } from "hono";
import { cors } from "hono/cors";
import { logger } from "hono/logger";
import { prettyJSON } from "hono/pretty-json";
import { RPCHandler } from "@orpc/server/fetch";
import { OpenAPIHandler } from "@orpc/openapi/fetch";
import { ZodToJsonSchemaConverter } from "@orpc/zod/zod4";
import { experimental_SmartCoercionPlugin as SmartCoercionPlugin } from "@orpc/json-schema";
import { OpenAPIReferencePlugin } from "@orpc/openapi/plugins";
import { onError } from "@orpc/server";
import { createMcpServer } from "./mcp/server.js";
import { handleMcpRequest } from "./mcp/handlers/streamable-http.js";
import { router } from "./rpc/router.js";
import { handleChatStream, handleChatWithTools } from "./ai/chat.js";
import { ChatRequestSchema } from "../contracts/schemas.js";

// ============================================================================
// Initialize Hono app
// ============================================================================

const app = new Hono();

// Middleware
app.use("*", logger());
app.use("*", cors());
app.use("*", prettyJSON());

// ============================================================================
// MCP Endpoints - Model Context Protocol for AI tool calling
// ============================================================================

const mcpServer = createMcpServer();

app.post("/mcp", async (c) => {
  const response = await handleMcpRequest(c.req.raw, mcpServer);
  return response;
});

// Legacy SSE endpoint (deprecated but kept for compatibility)
app.get("/mcp/sse", async (c) => {
  return c.json({
    error: "SSE transport is deprecated",
    message: "Please use the Streamable-HTTP protocol at POST /mcp",
  }, 410);
});

// ============================================================================
// oRPC Endpoints - Type-safe RPC with client generation
// ============================================================================

// RPC handler for type-safe communication
const rpcHandler = new RPCHandler(router);

app.all("/rpc/*", async (c) => {
  const { response } = await rpcHandler.handle(c.req.raw, {
    prefix: "/rpc",
    context: {
      // Extract userId from Authorization header
      userId: c.req.header("Authorization")?.replace("Bearer ", "").replace("token-", ""),
      headers: c.req.raw.headers,
    },
  });

  return response ?? new Response("Not found", { status: 404 });
});

// ============================================================================
// OpenAPI Endpoints - Auto-generated REST API with Swagger docs
// ============================================================================

const openAPIHandler = new OpenAPIHandler(router, {
  interceptors: [
    onError((error) => {
      console.error("OpenAPI error:", error);
    }),
  ],
  plugins: [
    new SmartCoercionPlugin({
      schemaConverters: [new ZodToJsonSchemaConverter()],
    }),
    new OpenAPIReferencePlugin({
      schemaConverters: [new ZodToJsonSchemaConverter()],
      specGenerateOptions: {
        info: {
          title: "API Unified - MCP + oRPC + AI",
          version: "1.0.0",
          description: `
# API Unified

A unified API demonstrating:
- **MCP (Model Context Protocol)**: AI tool calling interface at \`/mcp\`
- **oRPC**: Type-safe RPC endpoints at \`/rpc/*\`
- **AI Streaming**: Chat endpoints with streaming support at \`/ai/chat\`
- **OpenAPI**: Auto-generated REST API with docs at \`/api/*\`

## Features

### MCP Tools
- \`add\`: Add two numbers
- \`search\`: Search knowledge base
- \`analyzeText\`: Text analysis with entities and sentiment
- \`getCurrentTime\`: Get server time
- \`listResources\`: List available resources

### oRPC Procedures
- \`todo.*\`: CRUD operations for todos
- \`auth.*\`: User authentication and registration
- \`public.*\`: Health checks and server info

### AI Chat
- Streaming responses with Anthropic models
- Optional tool calling integration
- Support for conversation history
          `.trim(),
        },
        security: [{ bearerAuth: [] }],
        components: {
          securitySchemes: {
            bearerAuth: {
              type: "http",
              scheme: "bearer",
              description: "Use format: `token-{userId}` (e.g., `token-1`)",
            },
          },
        },
      },
      docsConfig: {
        authentication: {
          securitySchemes: {
            bearerAuth: {
              token: "token-1",
            },
          },
        },
      },
    }),
  ],
});

app.all("/api/*", async (c) => {
  const { response } = await openAPIHandler.handle(c.req.raw, {
    prefix: "/api",
    context: {
      userId: c.req.header("Authorization")?.replace("Bearer ", "").replace("token-", ""),
      headers: c.req.raw.headers,
    },
  });

  return response ?? new Response("Not found", { status: 404 });
});

// ============================================================================
// AI Chat Endpoints - Streaming chat with optional tool calling
// ============================================================================

app.post("/ai/chat", async (c) => {
  try {
    const body = await c.req.json();
    const request = ChatRequestSchema.parse(body);
    const response = await handleChatStream(request);
    return response;
  } catch (error) {
    return c.json(
      {
        error: "Invalid request",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      400
    );
  }
});

app.post("/ai/chat-with-tools", async (c) => {
  try {
    const body = await c.req.json();
    const request = ChatRequestSchema.parse(body);
    const response = await handleChatWithTools(request);
    return response;
  } catch (error) {
    return c.json(
      {
        error: "Invalid request",
        message: error instanceof Error ? error.message : "Unknown error",
      },
      400
    );
  }
});

// ============================================================================
// Root & Documentation
// ============================================================================

app.get("/", (c) => {
  return c.json({
    name: "API Unified",
    version: "1.0.0",
    description: "Unified API with MCP, oRPC, and AI streaming",
    endpoints: {
      mcp: {
        streamableHttp: "POST /mcp",
        description: "Model Context Protocol for AI tool calling",
      },
      rpc: {
        base: "/rpc/*",
        description: "Type-safe RPC endpoints",
        example: "POST /rpc/todo/create",
      },
      api: {
        base: "/api/*",
        docs: "/api/~openapi.json",
        ui: "/api/~docs",
        description: "OpenAPI REST endpoints with Swagger docs",
        example: "GET /api/public/health",
      },
      ai: {
        chat: "POST /ai/chat",
        chatWithTools: "POST /ai/chat-with-tools",
        description: "AI streaming chat endpoints",
      },
    },
    documentation: {
      openapi: "/api/~openapi.json",
      swaggerUI: "/api/~docs",
    },
  });
});

// ============================================================================
// Start Server
// ============================================================================

const port = parseInt(process.env.PORT || "3000");

console.log(`
🚀 API Unified Server Starting...

Server running on: http://localhost:${port}

📚 Endpoints:
  - Root:              http://localhost:${port}/
  - MCP:               http://localhost:${port}/mcp
  - oRPC:              http://localhost:${port}/rpc/*
  - OpenAPI:           http://localhost:${port}/api/*
  - OpenAPI Spec:      http://localhost:${port}/api/~openapi.json
  - Swagger UI:        http://localhost:${port}/api/~docs
  - AI Chat:           http://localhost:${port}/ai/chat
  - AI Chat + Tools:   http://localhost:${port}/ai/chat-with-tools

🔧 Features:
  ✅ MCP - Model Context Protocol for AI tools
  ✅ oRPC - Type-safe RPC with auto-generated clients
  ✅ OpenAPI - Auto-generated REST API + Swagger docs
  ✅ AI Streaming - Chat with Anthropic Claude
`);

export default {
  port,
  fetch: app.fetch,
};
