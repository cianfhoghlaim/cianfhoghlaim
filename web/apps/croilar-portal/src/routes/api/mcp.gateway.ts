import { createFileRoute } from "@tanstack/react-router";

/**
 * MCP Gateway API - Proxies to LiteLLM for centralized MCP server access.
 *
 * This endpoint provides unified access to 25+ MCP servers through LiteLLM:
 * - Browser: browserbase, chrome-devtools, firecrawl-mcp
 * - Knowledge: cognee, qdrant, memgraph
 * - Data Flows: dagster-mcp, dlt-workspace, codeolas
 * - Observability: logfire, langfuse, mlflow
 *
 * Request format (JSON-RPC 2.0):
 * {
 *   "jsonrpc": "2.0",
 *   "id": 1,
 *   "method": "tools/call",
 *   "params": {
 *     "server": "codeolas",
 *     "name": "search",
 *     "arguments": { "query": "async function" }
 *   }
 * }
 */

// LiteLLM base URL (from environment or default)
const LITELLM_BASE_URL = process.env.LITELLM_BASE_URL || "http://litellm:4000";

// MCP server categories for documentation
const MCP_SERVER_CATEGORIES = {
  browser: ["browserbase", "chrome-devtools", "firecrawl-mcp"],
  knowledge: ["cognee-mcp", "qdrant", "memgraph"],
  dataflows: ["dagster-mcp", "dlt-workspace", "codeolas"],
  code: ["codeolas", "chunkhound"],
  infrastructure: ["docker-mcp", "postgres", "clickhouse"],
} as const;

interface MCPGatewayRequest {
  jsonrpc: "2.0";
  id?: string | number;
  method: string;
  params: {
    server: string;
    name: string;
    arguments?: Record<string, unknown>;
  };
}

interface MCPGatewayResponse {
  jsonrpc: "2.0";
  id?: string | number;
  result?: unknown;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

export const Route = createFileRoute("/api/mcp/gateway")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        try {
          const body = (await request.json()) as MCPGatewayRequest;

          // Validate JSON-RPC format
          if (body.jsonrpc !== "2.0" || !body.method || !body.params?.server) {
            const errorResponse: MCPGatewayResponse = {
              jsonrpc: "2.0",
              id: body.id,
              error: {
                code: -32600,
                message: "Invalid Request: Missing required fields (server, method)",
              },
            };
            return Response.json(errorResponse, { status: 400 });
          }

          const { server, name, arguments: args } = body.params;

          // Forward to LiteLLM MCP endpoint
          const litellmRequest = {
            jsonrpc: "2.0",
            id: body.id || 1,
            method: "tools/call",
            params: {
              name,
              arguments: args || {},
            },
          };

          const response = await fetch(`${LITELLM_BASE_URL}/mcp/${server}`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              // Pass through authorization if present
              ...(request.headers.get("Authorization")
                ? { Authorization: request.headers.get("Authorization")! }
                : {}),
            },
            body: JSON.stringify(litellmRequest),
          });

          if (!response.ok) {
            const errorResponse: MCPGatewayResponse = {
              jsonrpc: "2.0",
              id: body.id,
              error: {
                code: -32000,
                message: `LiteLLM error: ${response.status} ${response.statusText}`,
                data: await response.text(),
              },
            };
            return Response.json(errorResponse, { status: response.status });
          }

          const result = await response.json();
          return Response.json(result);
        } catch (error) {
          const errorResponse: MCPGatewayResponse = {
            jsonrpc: "2.0",
            error: {
              code: -32603,
              message: `Internal error: ${error instanceof Error ? error.message : String(error)}`,
            },
          };
          return Response.json(errorResponse, { status: 500 });
        }
      },

      // GET returns available servers and categories
      GET: () => {
        return Response.json({
          status: "ok",
          servers: MCP_SERVER_CATEGORIES,
          litellm_url: LITELLM_BASE_URL,
          documentation: "POST to this endpoint with JSON-RPC 2.0 format",
        });
      },
    },
  },
});
