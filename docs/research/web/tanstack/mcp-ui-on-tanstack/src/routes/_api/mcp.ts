import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createServerFileRoute } from "@tanstack/react-start/server";
import z from "zod";
import { createUIResource } from "@mcp-ui/server";

import { handleMcpRequest } from "@/utils/mcp-handler";

import guitars from "@/data/example-guitars";

const server = new McpServer({
  name: "guitar-server",
  version: "1.0.0",
});

server.registerTool(
  "getGuitars",
  {
    title: "Returns the guitars from the database",
    description: "Get guitars",
  },
  () => ({
    content: [{ type: "text", text: JSON.stringify(guitars) }],
  })
);

server.registerTool(
  "recommendGuitar",
  {
    title: "Tool to visually recommend a guitar to the user",
    description: "Recommend a guitar to the user",
    inputSchema: {
      guitarId: z.string().describe("The id of the guitar to recommend"),
    },
  },
  ({ guitarId }) => ({
    content: [
      createUIResource({
        uri: `ui://guitar-server/iframe-guitar/${guitarId}`,
        content: {
          type: "externalUrl",
          iframeUrl: `http://localhost:3000/iframe-guitar/${guitarId}`,
        },
        encoding: "text",
      }),
    ],
  })
);

export const ServerRoute = createServerFileRoute("/_api/mcp").methods({
  POST: async ({ request }) => handleMcpRequest(request, server),
});
