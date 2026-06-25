import { v } from "convex/values";
import { mutation, query } from "../_generated/server";
import { loggedAction } from "../_middleware";
import { DEVTOOLS_READ_ROLES, DEVTOOLS_WRITE_ROLES, requireDevtoolsRead, requireOrgRole } from "./helpers";

export const get = query({
  args: {
    scope: v.optional(v.string()),
    window: v.optional(v.string()),
  },
  handler: async (ctx, args) => {
    await requireDevtoolsRead(ctx);
    const scope = args.scope ?? "global";
    const window = args.window ?? "5m";
    return await ctx.db
      .query("convexMetrics")
      .withIndex("by_scope_metric", (q) =>
        q.eq("scope", scope).eq("metric", "p50").gt("sampledAt", 0),
      )
      .order("desc")
      .take(20)
      .then(async () => {
        return await ctx.db
          .query("convexMetrics")
          .withIndex("by_scope_metric", (q) =>
            q
              .eq("scope", scope)
              .gte("sampledAt", 0),
          )
          .collect()
          .then((all) =>
            all
              .filter((m) => m.window === window)
              .sort((a, b) => b.sampledAt - a.sampledAt),
          );
      });
  },
});

export const getByScope = query({
  args: { scope: v.string(), window: v.optional(v.string()) },
  handler: async (ctx, args) => {
    await requireDevtoolsRead(ctx);
    const all = await ctx.db
      .query("convexMetrics")
      .withIndex("by_scope_metric", (q) => q.eq("scope", args.scope))
      .collect();
    const filtered = args.window
      ? all.filter((m) => m.window === args.window)
      : all;
    return filtered.sort((a, b) => b.sampledAt - a.sampledAt);
  },
});

export const record = mutation({
  args: {
    scope: v.string(),
    metric: v.string(),
    value: v.number(),
    window: v.string(),
  },
  handler: async (ctx, args) => {
    await requireOrgRole(ctx, "croilar-admin", DEVTOOLS_WRITE_ROLES);
    await ctx.db.insert("convexMetrics", {
      ...args,
      sampledAt: Date.now(),
    });
  },
});

export const refresh = loggedAction(
  async (ctx, _args: { scope?: string } | undefined) => {
    const now = Date.now();
    const fiveMinAgo = now - 5 * 60 * 1000;
    const calls = await ctx.db
      .query("convexFunctionCalls")
      .withIndex("by_calledAt", (q) => q.gte("calledAt", fiveMinAgo))
      .collect();

    const durations = calls.map((c) => c.durationMs).sort((a, b) => a - b);
    const pct = (p: number) =>
      durations[Math.min(durations.length - 1, Math.floor(durations.length * p))] ?? 0;

    const ok = calls.filter((c) => c.ok).length;
    const qps = calls.length / 300;

    await ctx.runMutation("convex_metrics:record" as any, {
      scope: "global",
      metric: "p50",
      value: pct(0.5),
      window: "5m",
    });
    await ctx.runMutation("convex_metrics:record" as any, {
      scope: "global",
      metric: "p95",
      value: pct(0.95),
      window: "5m",
    });
    await ctx.runMutation("convex_metrics:record" as any, {
      scope: "global",
      metric: "p99",
      value: pct(0.99),
      window: "5m",
    });
    await ctx.runMutation("convex_metrics:record" as any, {
      scope: "global",
      metric: "qps",
      value: qps,
      window: "5m",
    });
    await ctx.runMutation("convex_metrics:record" as any, {
      scope: "global",
      metric: "error_rate",
      value: calls.length === 0 ? 0 : (calls.length - ok) / calls.length,
      window: "5m",
    });

    return { calls: calls.length };
  },
  { function: "convex_metrics.refresh", project: "croilar" },
);
