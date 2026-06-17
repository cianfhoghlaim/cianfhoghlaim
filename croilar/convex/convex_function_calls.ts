import { v } from "convex/values";
import { query } from "../_generated/server";

export const tail = query({
  args: {
    limit: v.optional(v.number()),
    function: v.optional(v.string()),
    project: v.optional(v.string()),
    ok: v.optional(v.boolean()),
  },
  handler: async (ctx, args) => {
    const lim = args.limit ?? 200;
    let rows;
    if (args.function) {
      rows = await ctx.db
        .query("convexFunctionCalls")
        .withIndex("by_function_calledAt", (q) =>
          q.eq("function", args.function!),
        )
        .order("desc")
        .take(lim);
    } else {
      rows = await ctx.db
        .query("convexFunctionCalls")
        .withIndex("by_calledAt")
        .order("desc")
        .take(lim);
    }
    if (args.project !== undefined) {
      rows = rows.filter((r) => r.project === args.project);
    }
    if (args.ok !== undefined) {
      rows = rows.filter((r) => r.ok === args.ok);
    }
    return rows;
  },
});

export const getRecent = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("convexFunctionCalls")
      .withIndex("by_calledAt")
      .order("desc")
      .take(args.limit ?? 100);
  },
});

export const getStats = query({
  args: { windowMs: v.optional(v.number()) },
  handler: async (ctx, args) => {
    const windowMs = args.windowMs ?? 5 * 60 * 1000;
    const since = Date.now() - windowMs;
    const rows = await ctx.db
      .query("convexFunctionCalls")
      .withIndex("by_calledAt", (q) => q.gte("calledAt", since))
      .collect();
    const byFunction: Record<
      string,
      { count: number; ok: number; durations: number[] }
    > = {};
    for (const r of rows) {
      const slot = byFunction[r.function] ?? { count: 0, ok: 0, durations: [] };
      slot.count += 1;
      if (r.ok) slot.ok += 1;
      slot.durations.push(r.durationMs);
      byFunction[r.function] = slot;
    }
    const stats: Record<
      string,
      { count: number; errorRate: number; p50: number; p95: number; p99: number }
    > = {};
    for (const [fn, s] of Object.entries(byFunction)) {
      const sorted = s.durations.slice().sort((a, b) => a - b);
      const pct = (p: number) => sorted[Math.min(sorted.length - 1, Math.floor(sorted.length * p))] ?? 0;
      stats[fn] = {
        count: s.count,
        errorRate: s.count === 0 ? 0 : (s.count - s.ok) / s.count,
        p50: pct(0.5),
        p95: pct(0.95),
        p99: pct(0.99),
      };
    }
    return stats;
  },
});
