import { cron } from "../_generated/server";

export const syncStacks = cron("sync-stacks", { interval: "*/5 * * * *" }, async (ctx) => {
  await ctx.runAction((await import("../_generated/api")).stacks.refreshAll, {});
});

export const syncPipelines = cron("sync-pipelines", { interval: "*/30 * * * *" }, async (ctx) => {
  await ctx.runAction((await import("../_generated/api")).pipelines.refreshAll, {});
});

export const syncMcpServers = cron("sync-mcp", { interval: "0 * * * *" }, async (ctx) => {
  await ctx.runAction((await import("../_generated/api")).mcp.refreshAll, {});
});

export const syncContainerImages = cron("sync-images", { interval: "0 */6 * * *" }, async (ctx) => {
  await ctx.runAction((await import("../_generated/api")).registry.refreshAll, {});
});
