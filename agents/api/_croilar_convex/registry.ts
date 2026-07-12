import { action, mutation, query } from "../_generated/server";
import { v } from "convex/values";
import { requireOrgRole } from "./helpers";

const GHCR_API = "https://ghcr.io/v2/cianfhoghlaim";
const IMAGES = [
  "croilar-web", "croilar-portal", "croilar-dagster", "croilar-marimo", "croilar-image-pipeline",
  "browser-grid", "cal-diy", "stagehand-local", "n8n-init", "vikunja-seed",
  "croilar-hono-api",
];

export const list = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("containerImages").collect();
  },
});

export const refreshAll = action({
  args: {},
  handler: async (ctx) => {
    for (const name of IMAGES) {
      try {
        const response = await fetch(`${GHCR_API}/${name}/tags/list`);
        if (!response.ok) continue;
        const data = (await response.json()) as { tags?: string[] };
        const tags = data.tags ?? [];
        const latestTag = tags.filter((t) => t !== "latest" && t !== "edge").sort().pop() ?? "latest";

        const existing = await ctx.runQuery(
          (await import("../_generated/api")).internal.registry.getByName,
          { name },
        );
        if (existing) {
          await ctx.runMutation(
            (await import("../_generated/api")).internal.registry.updateByName,
            { name, latestTag, lastBuilt: Date.now(), multiArch: true },
          );
        } else {
          await ctx.runMutation(
            (await import("../_generated/api")).internal.registry.insert,
            { name, latestTag, lastBuilt: Date.now(), multiArch: true },
          );
        }
      } catch {
        // skip offline images
      }
    }
    return { count: IMAGES.length };
  },
});
