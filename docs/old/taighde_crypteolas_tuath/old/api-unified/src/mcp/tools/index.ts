import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { AddNumbersInputSchema, SearchInputSchema, AnalyzeTextInputSchema } from "../../../contracts/schemas.js";

/**
 * Register all MCP tools on the server
 */
export function registerTools(server: McpServer) {
  // Basic math tool
  server.tool(
    "add",
    "Add two numbers together",
    AddNumbersInputSchema.shape,
    async ({ a, b }) => ({
      content: [
        {
          type: "text",
          text: `The sum of ${a} and ${b} is ${a + b}`,
        },
      ],
    })
  );

  // Search tool (simulated)
  server.tool(
    "search",
    "Search for information in the knowledge base",
    SearchInputSchema.shape,
    async ({ query, limit }) => {
      // Simulated search results
      const results = Array.from({ length: Math.min(limit, 3) }, (_, i) => ({
        id: `result-${i + 1}`,
        title: `Search result ${i + 1} for "${query}"`,
        snippet: `This is a snippet from result ${i + 1} that matches your query.`,
        relevance: 1 - i * 0.2,
      }));

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(results, null, 2),
          },
        ],
      };
    }
  );

  // Text analysis tool
  server.tool(
    "analyzeText",
    "Analyze text for entities, sentiment, and other features",
    AnalyzeTextInputSchema.shape,
    async ({ text, includeEntities, includeSentiment }) => {
      const analysis: Record<string, any> = {
        text,
        wordCount: text.split(/\s+/).length,
        characterCount: text.length,
      };

      if (includeEntities) {
        // Simulated entity extraction
        analysis.entities = [
          { text: "example", type: "KEYWORD", confidence: 0.95 },
        ];
      }

      if (includeSentiment) {
        // Simulated sentiment analysis
        analysis.sentiment = {
          score: 0.75,
          label: "positive",
          confidence: 0.89,
        };
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(analysis, null, 2),
          },
        ],
      };
    }
  );

  // Get current time tool
  server.tool(
    "getCurrentTime",
    "Get the current server time in ISO format",
    {},
    async () => ({
      content: [
        {
          type: "text",
          text: new Date().toISOString(),
        },
      ],
    })
  );

  // List available resources tool
  server.tool(
    "listResources",
    "List all available resources in the system",
    {},
    async () => {
      const resources = [
        {
          uri: "resource://todos",
          name: "Todos List",
          description: "Access to all todos",
          mimeType: "application/json",
        },
        {
          uri: "resource://users",
          name: "Users List",
          description: "Access to all users",
          mimeType: "application/json",
        },
      ];

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(resources, null, 2),
          },
        ],
      };
    }
  );
}
