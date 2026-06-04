import { createFileRoute } from "@tanstack/react-router";

/**
 * Códeolas API - Code analysis and semantic search.
 *
 * Provides access to the códeolas code analysis system:
 * - Semantic code search via LanceDB embeddings
 * - Multi-hop retrieval through code relationships
 * - Code structure analysis via Tree-sitter
 * - Graph-based code navigation via Memgraph
 *
 * Routes through the LiteLLM MCP gateway to access the codeolas MCP server.
 */

// LiteLLM base URL for MCP calls
const LITELLM_BASE_URL = process.env.LITELLM_BASE_URL || "http://litellm:4000";

interface CodeolasSearchRequest {
  query: string;
  options?: {
    limit?: number;
    language?: string;
    repository?: string;
    include_context?: boolean;
    rerank?: boolean;
  };
}

interface CodeolasSearchResult {
  file_path: string;
  content: string;
  language: string;
  score: number;
  line_start?: number;
  line_end?: number;
  context?: string;
}

interface CodeolasAnalyzeRequest {
  file_path: string;
  analysis_type?: "structure" | "dependencies" | "symbols" | "all";
}

interface CodeolasRelationshipsRequest {
  entity: string;
  entity_type?: "file" | "function" | "class" | "module";
  depth?: number;
}

export const Route = createFileRoute("/api/codeolas")({
  server: {
    handlers: {
      // POST: Execute codeolas operations
      POST: async ({ request }) => {
        try {
          const body = await request.json();
          const { action, ...params } = body as { action: string } & Record<string, unknown>;

          // Map action to MCP tool name
          const toolMapping: Record<string, string> = {
            search: "search",
            analyze: "analyze",
            relationships: "get_relationships",
            index: "index_repository",
          };

          const toolName = toolMapping[action];
          if (!toolName) {
            return Response.json(
              {
                error: `Unknown action: ${action}. Available: ${Object.keys(toolMapping).join(", ")}`,
              },
              { status: 400 }
            );
          }

          // Call códeolas MCP server via LiteLLM gateway
          const mcpRequest = {
            jsonrpc: "2.0",
            id: 1,
            method: "tools/call",
            params: {
              name: toolName,
              arguments: params,
            },
          };

          const response = await fetch(`${LITELLM_BASE_URL}/mcp/codeolas`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(mcpRequest),
          });

          if (!response.ok) {
            return Response.json(
              {
                error: `Códeolas MCP error: ${response.status}`,
                details: await response.text(),
              },
              { status: response.status }
            );
          }

          const result = await response.json();

          // Unwrap JSON-RPC response
          if (result.error) {
            return Response.json(
              {
                error: result.error.message,
                code: result.error.code,
              },
              { status: 400 }
            );
          }

          return Response.json({
            success: true,
            action,
            data: result.result,
          });
        } catch (error) {
          return Response.json(
            {
              error: `Internal error: ${error instanceof Error ? error.message : String(error)}`,
            },
            { status: 500 }
          );
        }
      },

      // GET: Quick search via query parameter
      GET: async ({ request }) => {
        const url = new URL(request.url);
        const query = url.searchParams.get("q") || url.searchParams.get("query");
        const limit = parseInt(url.searchParams.get("limit") || "10");
        const language = url.searchParams.get("lang") || url.searchParams.get("language");

        if (!query) {
          return Response.json({
            status: "ok",
            endpoints: {
              "GET /api/codeolas?q=<query>": "Quick semantic code search",
              "POST /api/codeolas": "Full API with action parameter",
            },
            actions: ["search", "analyze", "relationships", "index"],
          });
        }

        // Execute search
        const mcpRequest = {
          jsonrpc: "2.0",
          id: 1,
          method: "tools/call",
          params: {
            name: "search",
            arguments: {
              query,
              limit,
              ...(language ? { language } : {}),
            },
          },
        };

        try {
          const response = await fetch(`${LITELLM_BASE_URL}/mcp/codeolas`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(mcpRequest),
          });

          const result = await response.json();

          if (result.error) {
            return Response.json(
              { error: result.error.message },
              { status: 400 }
            );
          }

          return Response.json({
            query,
            results: result.result,
            count: Array.isArray(result.result) ? result.result.length : 0,
          });
        } catch (error) {
          return Response.json(
            { error: String(error) },
            { status: 500 }
          );
        }
      },
    },
  },
});
