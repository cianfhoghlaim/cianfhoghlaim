import { v } from "convex/values";
import { mutation, query } from "../_generated/server";
import { DEVTOOLS_READ_ROLES, DEVTOOLS_WRITE_ROLES, requireDevtoolsRead, requireOrgRole } from "./helpers";
import { loggedAction } from "../_middleware";

export const list = query({
  args: {
    project: v.optional(v.string()),
    kind: v.optional(
      v.union(
        v.literal("worker"),
        v.literal("pages"),
        v.literal("r2"),
        v.literal("kv"),
        v.literal("d1"),
        v.literal("durable_object"),
      ),
    ),
  },
  handler: async (ctx, args) => {
    await requireDevtoolsRead(ctx);
    let q = ctx.db.query("cloudflareResources");
    if (args.project && args.kind) {
      q = q.withIndex("by_project_kind", (qq) =>
        qq.eq("project", args.project!).eq("kind", args.kind!),
      );
    } else if (args.project) {
      q = q.withIndex("by_project_kind", (qq) =>
        qq.eq("project", args.project!),
      );
    }
    return await q.collect();
  },
});

export const getByProject = query({
  args: { project: v.string() },
  handler: async (ctx, args) => {
    await requireDevtoolsRead(ctx);
    return await ctx.db
      .query("cloudflareResources")
      .withIndex("by_project_kind", (q) => q.eq("project", args.project))
      .collect();
  },
});

export const ingest = mutation({
  args: {
    project: v.string(),
    rows: v.array(
      v.object({
        kind: v.union(
          v.literal("worker"),
          v.literal("pages"),
          v.literal("r2"),
          v.literal("kv"),
          v.literal("d1"),
          v.literal("durable_object"),
        ),
        name: v.string(),
        account: v.optional(v.string()),
        wranglerConfig: v.optional(v.string()),
        lastDeployed: v.optional(v.number()),
        version: v.optional(v.string()),
      }),
    ),
  },
  handler: async (ctx, args) => {
    await requireOrgRole(ctx, "croilar-admin", DEVTOOLS_WRITE_ROLES);
    const existing = await ctx.db
      .query("cloudflareResources")
      .withIndex("by_project_kind", (q) => q.eq("project", args.project))
      .collect();
    for (const row of existing) {
      await ctx.db.delete(row._id);
    }
    for (const row of args.rows) {
      await ctx.db.insert("cloudflareResources", { project: args.project, ...row });
    }
    return { deleted: existing.length, inserted: args.rows.length };
  },
});

export const refreshAll = loggedAction(
  async (_ctx, _args: { project?: string } | undefined) => {
    const httpUrl = process.env.CROILAR_CONVEX_HTTP_URL;
    const deployKey = process.env.CROILAR_CONVEX_DEPLOY_KEY;
    if (!httpUrl || !deployKey) {
      throw new Error(
        "CROILAR_CONVEX_HTTP_URL and CROILAR_CONVEX_DEPLOY_KEY must be set",
      );
    }
    const resp = await fetch(`${httpUrl}/api/run/analyze-web-stack`, {
      method: "POST",
      headers: {
        Authorization: `Convex ${deployKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ kind: "cloudflare" }),
    });
    if (!resp.ok) {
      throw new Error(`analyzer failed: ${resp.status} ${await resp.text()}`);
    }
    return (await resp.json()) as { rows: number };
  },
  { function: "cloudflare_resources.refreshAll", project: "croilar" },
);
