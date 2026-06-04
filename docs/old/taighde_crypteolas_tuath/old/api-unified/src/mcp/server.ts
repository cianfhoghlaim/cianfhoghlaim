import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerTools } from "./tools/index.js";

/**
 * Create and configure the MCP server
 */
export function createMcpServer() {
  const server = new McpServer({
    name: "api-unified-mcp",
    version: "1.0.0",
  });

  // Register all tools
  registerTools(server);

  // Register resources
  server.resource(
    "todos",
    "resource://todos",
    "List of all todos",
    "application/json",
    async () => ({
      content: [
        {
          type: "text",
          text: JSON.stringify([
            {
              id: "1",
              title: "Example Todo",
              completed: false,
              createdAt: new Date().toISOString(),
            },
          ]),
        },
      ],
    })
  );

  return server;
}
