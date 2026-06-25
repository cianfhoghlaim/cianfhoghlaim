import { cron } from "../_generated/server";
import { api } from "../_generated/api";

export const syncStacks = cron("sync-stacks", { interval: "*/5 * * * *" }, async (ctx) => {
  await ctx.runAction(api.stacks.refreshAll, {});
});

export const syncPipelines = cron("sync-pipelines", { interval: "*/30 * * * *" }, async (ctx) => {
  await ctx.runAction(api.pipelines.refreshAll, {});
});

export const syncMcpServers = cron("sync-mcp", { interval: "0 * * * *" }, async (ctx) => {
  await ctx.runAction(api.mcp.refreshAll, {});
});

export const syncContainerImages = cron("sync-images", { interval: "0 */6 * * *" }, async (ctx) => {
  await ctx.runAction(api.registry.refreshAll, {});
});

// ── Web stack observability (croilar-devtools-hub) ────────────────────
export const syncTanstackRoutes = cron("sync-tanstack-routes", { interval: "0 */6 * * *" }, async (ctx) => {
  await ctx.runAction(api.tanstack_routes.refreshAll, {});
});

export const syncConvexFunctions = cron("sync-convex-functions", { interval: "0 */12 * * *" }, async (ctx) => {
  await ctx.runAction(api.convex_functions.refreshAll, {});
});

export const syncCloudflareResources = cron("sync-cloudflare", { interval: "0 */6 * * *" }, async (ctx) => {
  await ctx.runAction(api.cloudflare_resources.refreshAll, {});
});

export const syncBamlSchemas = cron("sync-baml", { interval: "0 0 * * *" }, async (ctx) => {
  await ctx.runAction(api.baml_schemas.refreshAll, {});
});

export const syncMarimoNotebooks = cron("sync-marimo", { interval: "0 */12 * * *" }, async (ctx) => {
  await ctx.runAction(api.marimo_notebooks.refreshAll, {});
});

export const refreshConvexMetrics = cron("refresh-convex-metrics", { interval: "*/5 * * * *" }, async (ctx) => {
  await ctx.runAction(api.convex_metrics.refresh, {});
});
