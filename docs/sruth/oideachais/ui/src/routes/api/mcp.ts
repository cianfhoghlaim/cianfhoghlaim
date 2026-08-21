import { createAPIFileRoute } from "@tanstack/start/api";

/**
 * MCP (Model Context Protocol) Server Endpoint.
 *
 * Proxies MCP requests to the CocoIndex MCP server for:
 * - search-hybrid: Combined vector + keyword search
 * - search-semantic: Pure vector search
 * - search-keyword: Full-text keyword search
 */

const COCOINDEX_MCP_URL =
  process.env.COCOINDEX_MCP_URL || "http://127.0.0.1:3000/mcp";

interface MCPRequest {
  jsonrpc: "2.0";
  id: string | number;
  method: string;
  params?: Record<string, unknown>;
}

interface MCPResponse {
  jsonrpc: "2.0";
  id: string | number;
  result?: unknown;
  error?: {
    code: number;
    message: string;
    data?: unknown;
  };
}

export const ServerRoute = createAPIFileRoute("/api/mcp")({
  // Handle MCP JSON-RPC requests
  POST: async ({ request }) => {
    try {
      const body = (await request.json()) as MCPRequest;

      // Validate JSON-RPC format
      if (body.jsonrpc !== "2.0") {
        return new Response(
          JSON.stringify({
            jsonrpc: "2.0",
            id: body.id,
            error: {
              code: -32600,
              message: "Invalid Request: jsonrpc must be '2.0'",
            },
          }),
          {
            status: 400,
            headers: { "Content-Type": "application/json" },
          }
        );
      }

      // Handle capability discovery
      if (body.method === "initialize") {
        return new Response(
          JSON.stringify({
            jsonrpc: "2.0",
            id: body.id,
            result: {
              protocolVersion: "2024-11-05",
              capabilities: {
                tools: {},
              },
              serverInfo: {
                name: "oideachas-mcp-proxy",
                version: "0.1.0",
              },
            },
          }),
          {
            headers: { "Content-Type": "application/json" },
          }
        );
      }

      // Handle tool listing
      if (body.method === "tools/list") {
        return new Response(
          JSON.stringify({
            jsonrpc: "2.0",
            id: body.id,
            result: {
              tools: [
                {
                  name: "search-hybrid",
                  description:
                    "Hybrid search combining vector and keyword search for Irish curriculum documents",
                  inputSchema: {
                    type: "object",
                    properties: {
                      vector_query: {
                        type: "string",
                        description: "Natural language query for semantic search",
                      },
                      keyword_query: {
                        type: "string",
                        description:
                          "Keyword query for full-text search (e.g., 'subject:Mathematics level:JUNIOR_CYCLE')",
                      },
                      top_k: {
                        type: "number",
                        description: "Number of results to return (default: 10)",
                      },
                      vector_weight: {
                        type: "number",
                        description: "Weight for vector search (0-1, default: 0.7)",
                      },
                      keyword_weight: {
                        type: "number",
                        description: "Weight for keyword search (0-1, default: 0.3)",
                      },
                    },
                    required: ["vector_query"],
                  },
                },
                {
                  name: "search-semantic",
                  description:
                    "Pure vector/embedding search for semantic similarity",
                  inputSchema: {
                    type: "object",
                    properties: {
                      query: {
                        type: "string",
                        description: "Natural language query",
                      },
                      top_k: {
                        type: "number",
                        description: "Number of results (default: 10)",
                      },
                    },
                    required: ["query"],
                  },
                },
                {
                  name: "search-keyword",
                  description: "Full-text keyword search",
                  inputSchema: {
                    type: "object",
                    properties: {
                      query: {
                        type: "string",
                        description: "Keyword query with optional filters",
                      },
                      top_k: {
                        type: "number",
                        description: "Number of results (default: 10)",
                      },
                    },
                    required: ["query"],
                  },
                },
              ],
            },
          }),
          {
            headers: { "Content-Type": "application/json" },
          }
        );
      }

      // Proxy tool calls to CocoIndex MCP server
      if (body.method === "tools/call") {
        const response = await fetch(COCOINDEX_MCP_URL, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(body),
        });

        if (!response.ok) {
          return new Response(
            JSON.stringify({
              jsonrpc: "2.0",
              id: body.id,
              error: {
                code: -32603,
                message: `CocoIndex MCP error: ${response.statusText}`,
              },
            }),
            {
              status: 502,
              headers: { "Content-Type": "application/json" },
            }
          );
        }

        const result = await response.json();
        return new Response(JSON.stringify(result), {
          headers: { "Content-Type": "application/json" },
        });
      }

      // Unknown method
      return new Response(
        JSON.stringify({
          jsonrpc: "2.0",
          id: body.id,
          error: {
            code: -32601,
            message: `Method not found: ${body.method}`,
          },
        }),
        {
          status: 404,
          headers: { "Content-Type": "application/json" },
        }
      );
    } catch (error) {
      console.error("MCP request error:", error);
      return new Response(
        JSON.stringify({
          jsonrpc: "2.0",
          id: null,
          error: {
            code: -32603,
            message: `Internal error: ${error instanceof Error ? error.message : "Unknown"}`,
          },
        }),
        {
          status: 500,
          headers: { "Content-Type": "application/json" },
        }
      );
    }
  },

  // SSE endpoint for streaming MCP responses
  GET: async ({ request }) => {
    const url = new URL(request.url);
    const subscribe = url.searchParams.get("subscribe");

    if (subscribe !== "true") {
      return new Response("Use POST for MCP requests or GET with ?subscribe=true for SSE", {
        status: 400,
      });
    }

    // Create SSE stream for progress updates
    const encoder = new TextEncoder();
    const stream = new ReadableStream({
      start(controller) {
        // Send initial connection message
        controller.enqueue(
          encoder.encode(`data: ${JSON.stringify({ type: "connected" })}\n\n`)
        );

        // Keep connection alive with periodic pings
        const pingInterval = setInterval(() => {
          try {
            controller.enqueue(
              encoder.encode(`data: ${JSON.stringify({ type: "ping" })}\n\n`)
            );
          } catch {
            clearInterval(pingInterval);
          }
        }, 30000);

        // Clean up on close
        request.signal.addEventListener("abort", () => {
          clearInterval(pingInterval);
          controller.close();
        });
      },
    });

    return new Response(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    });
  },
});
