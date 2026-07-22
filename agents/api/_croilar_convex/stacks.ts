import { action, mutation, query } from "../_generated/server";
import { v } from "convex/values";
import { requireOrgRole } from "./helpers";

const KOMODO_URL = process.env.KOMODO_URL ?? "http://komodo:9120";
const KOMODO_API_KEY = process.env.KOMODO_API_KEY ?? "";

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("stackHealth").collect();
  },
});

export const getByName = query({
  args: { stackName: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("stackHealth")
      .withIndex("by_name", (q) => q.eq("stackName", args.stackName))
      .first();
  },
});

export const refreshAll = action({
  args: {},
  handler: async (ctx) => {
    const response = await fetch(`${KOMODO_URL}/stacks?api_key=${KOMODO_API_KEY}`);
    if (!response.ok) {
      throw new Error(`Komodo API ${response.status}: ${await response.text()}`);
    }
    const stacks = (await response.json()) as Array<{
      name: string;
      status: "running" | "stopped" | "error" | "unknown";
      container_count?: number;
      uptime_seconds?: number;
    }>;

    for (const stack of stacks) {
      const existing = await ctx.runQuery(
        // @ts-expect-error — generated
        (await import("../_generated/api")).internal.stacks.getByName,
        { stackName: stack.name },
      );
      if (existing) {
        await ctx.runMutation(
          // @ts-expect-error — generated
          (await import("../_generated/api")).internal.stacks.updateByName,
          {
            stackName: stack.name,
            status: stack.status,
            containerCount: stack.container_count ?? 0,
            uptime: stack.uptime_seconds,
            lastChecked: Date.now(),
          },
        );
      } else {
        await ctx.runMutation(
          // @ts-expect-error — generated
          (await import("../_generated/api")).internal.stacks.insert,
          {
            stackName: stack.name,
            status: stack.status,
            containerCount: stack.container_count ?? 0,
            uptime: stack.uptime_seconds,
            lastChecked: Date.now(),
          },
        );
      }
    }

    return { count: stacks.length };
  },
});

export const restartStack = mutation({
  args: { stackName: v.string() },
  handler: async (ctx, args) => {
    const id = await requireOrgRole(ctx, "admin", ["owner", "admin"]);
    const org = await ctx.db
      .query("organizations")
      .withIndex("by_slug", (q) => q.eq("slug", "croilar-admin"))
      .first();
    if (!org) throw new Error("croilar-admin org not found");

    await ctx.db.insert("portalAuditLog", {
      userId: id.userId,
      orgId: org._id,
      action: "restart_stack",
      targetType: "stack",
      targetName: args.stackName,
      outcome: "success",
      timestamp: Date.now(),
    });

    return { ok: true };
  },
});
