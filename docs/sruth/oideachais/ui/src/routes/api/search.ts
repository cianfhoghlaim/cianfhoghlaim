import { createAPIFileRoute } from "@tanstack/start/api";

/**
 * Search API endpoint.
 *
 * Provides curriculum document search using CocoIndex MCP backend.
 */

const COCOINDEX_MCP_URL =
  process.env.COCOINDEX_MCP_URL || "http://127.0.0.1:3000/mcp";

interface SearchRequest {
  query: string;
  filters?: {
    documentType?: string;
    educationLevel?: string;
    subject?: string;
  };
  topK?: number;
}

interface SearchResult {
  id: string;
  title: string;
  excerpt: string;
  documentType: string;
  educationLevel: string;
  subject: string;
  score: number;
  source: string;
  url?: string;
}

export const ServerRoute = createAPIFileRoute("/api/search")({
  POST: async ({ request }) => {
    try {
      const body = (await request.json()) as SearchRequest;
      const { query, filters = {}, topK = 10 } = body;

      if (!query || query.trim() === "") {
        return new Response(
          JSON.stringify({ error: "Query is required", results: [] }),
          {
            status: 400,
            headers: { "Content-Type": "application/json" },
          }
        );
      }

      // Build keyword query from filters
      const keywordParts: string[] = [];
      if (filters.documentType) {
        keywordParts.push(`document_type:${filters.documentType}`);
      }
      if (filters.educationLevel) {
        keywordParts.push(`level:${filters.educationLevel}`);
      }
      if (filters.subject) {
        keywordParts.push(`subject:${filters.subject}`);
      }
      const keywordQuery = keywordParts.join(" ");

      // Call CocoIndex MCP hybrid search
      const mcpResponse = await fetch(COCOINDEX_MCP_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          jsonrpc: "2.0",
          id: Date.now(),
          method: "tools/call",
          params: {
            name: "search-hybrid",
            arguments: {
              vector_query: query,
              keyword_query: keywordQuery,
              top_k: topK,
              vector_weight: 0.7,
              keyword_weight: 0.3,
            },
          },
        }),
      });

      if (!mcpResponse.ok) {
        throw new Error(`MCP request failed: ${mcpResponse.statusText}`);
      }

      const mcpResult = await mcpResponse.json();

      if (mcpResult.error) {
        throw new Error(mcpResult.error.message);
      }

      // Transform MCP results to search results
      const rawResults = mcpResult.result?.content?.[0]?.text || "[]";
      const parsedResults = JSON.parse(rawResults);

      const results: SearchResult[] = (parsedResults.results || []).map(
        (r: Record<string, unknown>) => ({
          id: r.id || r.filename || crypto.randomUUID(),
          title: r.title || r.filename || "Untitled Document",
          excerpt:
            r.text?.substring(0, 200) ||
            r.content?.substring(0, 200) ||
            "No preview available",
          documentType: r.document_type || r.type || "unknown",
          educationLevel: r.education_level || r.level || "unknown",
          subject: r.subject || "unknown",
          score: r.score || 0,
          source: r.source || "unknown",
          url: r.url || r.source_url,
        })
      );

      return new Response(
        JSON.stringify({
          query,
          filters,
          results,
          total: results.length,
        }),
        {
          headers: { "Content-Type": "application/json" },
        }
      );
    } catch (error) {
      console.error("Search error:", error);
      return new Response(
        JSON.stringify({
          error: error instanceof Error ? error.message : "Search failed",
          results: [],
        }),
        {
          status: 500,
          headers: { "Content-Type": "application/json" },
        }
      );
    }
  },
});
