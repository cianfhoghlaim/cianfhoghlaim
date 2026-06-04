/**
 * MCP Router
 *
 * oRPC procedures for interacting with MCP (Model Context Protocol) servers.
 * Provides shortcuts for common MCP tool calls via the FastAPI agent system.
 */

import { z } from "zod";
import { protectedProcedure, publicProcedure } from "../index";
import { getFastAPIClient } from "../clients/fastapi-client";

// =============================================================================
// Input Schemas
// =============================================================================

const toolCallInputSchema = z.object({
  server: z.string().min(1),
  tool: z.string().min(1),
  args: z.record(z.string(), z.unknown()).optional(),
});

const searchCodeInputSchema = z.object({
  query: z.string().min(1).max(500),
  repository: z.string().optional(),
  language: z.string().optional(),
  limit: z.number().min(1).max(50).default(10),
});

const memoryQueryInputSchema = z.object({
  query: z.string().min(1).max(500),
  userId: z.string().optional(),
  limit: z.number().min(1).max(50).default(10),
});

const knowledgeGraphInputSchema = z.object({
  query: z.string().min(1).max(500),
  graphType: z.enum(["cognee", "graphiti", "falkordb"]).default("cognee"),
  limit: z.number().min(1).max(100).default(20),
});

// =============================================================================
// MCP Router
// =============================================================================

export const mcpRouter = {
  /**
   * List available MCP servers
   */
  listServers: publicProcedure.handler(() => {
    // Return configured MCP servers
    return {
      servers: [
        {
          name: "oideachas",
          description: "Irish education curriculum pipeline",
          transport: "stdio",
          tools: ["search_curriculum", "chat_education", "get_syllabus"],
        },
        {
          name: "codeolas",
          description: "Code analysis and search",
          transport: "stdio",
          tools: ["search_code", "analyze_file", "get_symbols"],
        },
        {
          name: "cognee",
          description: "AI memory and knowledge graphs",
          transport: "http",
          tools: ["add_memory", "search_memory", "get_graph"],
        },
        {
          name: "letta",
          description: "Persistent agent memory",
          transport: "http",
          tools: ["create_agent", "send_message", "get_memory"],
        },
        {
          name: "chunkhound",
          description: "Semantic code search",
          transport: "stdio",
          tools: ["search", "index", "explore"],
        },
        {
          name: "qdrant",
          description: "Vector similarity search",
          transport: "stdio",
          tools: ["search", "upsert", "delete"],
        },
        {
          name: "memgraph",
          description: "Graph database queries",
          transport: "stdio",
          tools: ["query", "create_node", "create_edge"],
        },
      ],
    };
  }),

  /**
   * Call an MCP tool directly
   *
   * This is a generic tool caller that proxies to the agent system
   * which has access to all configured MCP servers.
   */
  callTool: protectedProcedure
    .input(toolCallInputSchema)
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();

      // Use the agent chat to execute the tool call
      // The agent has access to all MCP tools
      const toolCallMessage = `Use the ${input.server} MCP server to call the ${input.tool} tool with arguments: ${JSON.stringify(input.args || {})}`;

      const response = await client.chat(
        {
          message: toolCallMessage,
          agents: ["tool_executor"],
        },
        context.session
      );

      return {
        result: response.message,
        agentsUsed: response.agents_used,
        sources: response.sources,
      };
    }),

  /**
   * Search code using chunkhound/codeolas
   */
  searchCode: protectedProcedure
    .input(searchCodeInputSchema)
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();

      const response = await client.chat(
        {
          message: `Search for code: "${input.query}"${input.repository ? ` in repository ${input.repository}` : ""}${input.language ? ` (${input.language} files)` : ""}. Return the top ${input.limit} results.`,
          agents: ["code_search"],
        },
        context.session
      );

      return {
        results: response.message,
        sources: response.sources,
        agentsUsed: response.agents_used,
      };
    }),

  /**
   * Query agent memory (Letta/Cognee)
   */
  queryMemory: protectedProcedure
    .input(memoryQueryInputSchema)
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();

      const response = await client.chat(
        {
          message: `Search my memories for: "${input.query}". Return the ${input.limit} most relevant memories.`,
          agents: ["memory"],
        },
        context.session
      );

      return {
        memories: response.message,
        sources: response.sources,
        agentsUsed: response.agents_used,
      };
    }),

  /**
   * Query knowledge graph
   */
  queryKnowledgeGraph: protectedProcedure
    .input(knowledgeGraphInputSchema)
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();

      const graphAgent =
        input.graphType === "cognee"
          ? "cognee"
          : input.graphType === "graphiti"
            ? "graphiti"
            : "graph";

      const response = await client.chat(
        {
          message: `Query the knowledge graph for: "${input.query}". Return up to ${input.limit} related entities and relationships.`,
          agents: [graphAgent],
        },
        context.session
      );

      return {
        entities: response.message,
        sources: response.sources,
        agentsUsed: response.agents_used,
      };
    }),

  /**
   * Shortcut: Search Irish curriculum
   */
  searchIrishCurriculum: protectedProcedure
    .input(
      z.object({
        query: z.string().min(1),
        subject: z.string().optional(),
        level: z.enum(["primary", "junior_cert", "leaving_cert"]).optional(),
      })
    )
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();

      let prompt = `Search the Irish curriculum for: "${input.query}"`;
      if (input.subject) {
        prompt += ` in ${input.subject}`;
      }
      if (input.level) {
        prompt += ` at ${input.level.replace("_", " ")} level`;
      }

      const response = await client.chat(
        {
          message: prompt,
          language: "ga",
          agents: ["curriculum"],
        },
        context.session
      );

      return {
        results: response.message,
        sources: response.sources,
        agentsUsed: response.agents_used,
      };
    }),

  /**
   * Shortcut: Get terminology translation
   */
  getTerminology: protectedProcedure
    .input(
      z.object({
        term: z.string().min(1),
        domain: z.string().optional(),
        targetLanguage: z.enum(["en", "ga"]).default("ga"),
      })
    )
    .handler(async ({ input, context }) => {
      const client = getFastAPIClient();

      const response = await client.searchTerminology(
        {
          query: input.term,
          language: input.targetLanguage,
          limit: 5,
        },
        context.session
      );

      return {
        term: input.term,
        translations: response.results.map((r) => ({
          translation: r.title,
          definition: r.content,
          domain: r.metadata.domain as string | undefined,
          source: r.metadata.source as string | undefined,
        })),
      };
    }),
};
