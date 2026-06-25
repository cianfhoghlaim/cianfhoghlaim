import { action, query } from "../_generated/server";
import { v } from "convex/values";

const MCP_SERVERS = [
  "browser", "firecrawl", "motherduck", "infisical", "chrome",
  "cocoindex-code", "cognee", "graphiti", "langfuse", "lancedb",
  "memgraph", "chunkhound", "pulumi",
];

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("mcpServers").collect();
  },
});

export const refreshAll = action({
  args: {},
  handler: async (ctx) => {
    for (const name of MCP_SERVERS) {
      const existing = await ctx.runQuery(
        (await import("../_generated/api")).internal.mcp.getByName,
        { name },
      );
      if (existing) {
        await ctx.runMutation(
          (await import("../_generated/api")).internal.mcp.updateByName,
          { name, status: "online", lastChecked: Date.now() },
        );
      } else {
        await ctx.runMutation(
          (await import("../_generated/api")).internal.mcp.insert,
          { name, status: "online", errorCount: 0, lastChecked: Date.now() },
        );
      }
    }
    return { count: MCP_SERVERS.length };
  },
});
