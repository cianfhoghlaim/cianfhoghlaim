import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";

/**
 * Handle MCP requests using the Streamable-HTTP protocol
 * This is the modern protocol that replaced SSE in summer 2025
 */
export async function handleMcpRequest(
  request: Request,
  server: McpServer
): Promise<Response> {
  try {
    // Create a new transport for this request
    const transport = new StreamableHTTPServerTransport({
      endpoint: "/mcp",
    });

    // Connect the server to the transport
    await server.connect(transport);

    // Handle the request
    const response = await transport.handleRequest(request);

    return response;
  } catch (error) {
    console.error("MCP request error:", error);
    return new Response(
      JSON.stringify({
        error: "Internal server error",
        message: error instanceof Error ? error.message : "Unknown error",
      }),
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      }
    );
  }
}
