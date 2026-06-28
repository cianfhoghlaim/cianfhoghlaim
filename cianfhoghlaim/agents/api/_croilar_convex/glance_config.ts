import { v } from "convex/values";
import { mutation, query } from "../_generated/server";
import { DEVTOOLS_READ_ROLES, DEVTOOLS_WRITE_ROLES, requireDevtoolsRead, requireOrgRole } from "./helpers";
import { loggedAction } from "../_middleware";

export const getCurrent = query({
  args: {},
  handler: async (ctx) => {
    await requireDevtoolsRead(ctx);
    return await ctx.db
      .query("glanceConfig")
      .withIndex("by_version")
      .order("desc")
      .first();
  },
});

export const getByVersion = query({
  args: { version: v.number() },
  handler: async (ctx, args) => {
    await requireDevtoolsRead(ctx);
    return await ctx.db
      .query("glanceConfig")
      .withIndex("by_version", (q) => q.eq("version", args.version))
      .first();
  },
});

export const list = query({
  args: { limit: v.optional(v.number()) },
  handler: async (ctx, args) => {
    await requireDevtoolsRead(ctx);
    return await ctx.db
      .query("glanceConfig")
      .withIndex("by_version")
      .order("desc")
      .take(args.limit ?? 10);
  },
});

export const store = mutation({
  args: {
    yaml: v.string(),
    pageCount: v.number(),
    widgetCount: v.number(),
    generatedBy: v.string(),
  },
  handler: async (ctx, args) => {
    await requireOrgRole(ctx, "croilar-admin", DEVTOOLS_WRITE_ROLES);
    const latest = await ctx.db
      .query("glanceConfig")
      .withIndex("by_version")
      .order("desc")
      .first();
    const version = (latest?.version ?? 0) + 1;
    const id = await ctx.db.insert("glanceConfig", {
      version,
      yaml: args.yaml,
      pageCount: args.pageCount,
      widgetCount: args.widgetCount,
      generatedAt: Date.now(),
      generatedBy: args.generatedBy,
    });
    return { id, version };
  },
});

export const regenerate = loggedAction(
  async (ctx, _args: { project?: string } | undefined) => {
    const regenScript = process.env.CROILAR_GLANCE_REGEN_SCRIPT;
    if (!regenScript) {
      throw new Error("CROILAR_GLANCE_REGEN_SCRIPT must be set");
    }
    const proc = Bun.spawn(["bun", "run", regenScript], {
      cwd: process.env.CROILAR_REPO_ROOT ?? process.cwd(),
      stdout: "pipe",
      stderr: "pipe",
    });
    const [stdout, stderr, exitCode] = await Promise.all([
      new Response(proc.stdout).text(),
      new Response(proc.stderr).text(),
      proc.exited,
    ]);
    if (exitCode !== 0) {
      throw new Error(`regenerate-glance-config failed: ${stderr}`);
    }
    const result = JSON.parse(stdout) as {
      yaml: string;
      pageCount: number;
      widgetCount: number;
    };
    await ctx.runMutation("glance_config:store" as any, {
      yaml: result.yaml,
      pageCount: result.pageCount,
      widgetCount: result.widgetCount,
      generatedBy: "analyzer",
    });
    return {
      pageCount: result.pageCount,
      widgetCount: result.widgetCount,
    };
  },
  { function: "glance_config.regenerate", project: "croilar" },
);
