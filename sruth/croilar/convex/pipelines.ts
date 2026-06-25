import { action, mutation, query } from "../_generated/server";
import { v } from "convex/values";

const DAGSTER_URL = process.env.DAGSTER_URL ?? "http://dagster:3000";
const DAGSTER_GRAPHQL = `${DAGSTER_URL}/graphql`;

export const list = query({
  args: { personaSlug: v.optional(v.string()) },
  handler: async (ctx, args) => {
    const assets = await ctx.db.query("pipelineAssets").collect();
    if (args.personaSlug) {
      return assets.filter((a) => a.assetName.startsWith(`${args.personaSlug}_`));
    }
    return assets;
  },
});

export const refreshAll = action({
  args: {},
  handler: async (ctx) => {
    const query = `
      query {
        assetNodes {
          assetKey { path }
          assetGroupName
        }
      }
    `;
    const response = await fetch(DAGSTER_GRAPHQL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });
    if (!response.ok) {
      throw new Error(`Dagster API ${response.status}`);
    }
    const { data } = (await response.json()) as {
      data: { assetNodes: Array<{ assetKey: { path: string[] }; assetGroupName: string }> };
    };
    const assets = data.assetNodes;

    for (const asset of assets) {
      const name = asset.assetKey.path.join("/");
      const existing = await ctx.runQuery(
        (await import("../_generated/api")).internal.pipelines.getByName,
        { assetName: name },
      );
      if (existing) {
        await ctx.runMutation(
          (await import("../_generated/api")).internal.pipelines.updateByName,
          { assetName: name, status: "materialized", dagsterUrl: `${DAGSTER_URL}/assets/${name}` },
        );
      } else {
        const slug = asset.assetGroupName?.startsWith("aleyum") ? "aleyum"
          : asset.assetGroupName?.startsWith("cianfhoghlaim") ? "cianfhoghlaim" : "cross_link";
        await ctx.runMutation(
          (await import("../_generated/api")).internal.pipelines.insert,
          { personaSlug: slug, assetName: name, status: "materialized", dagsterUrl: `${DAGSTER_URL}/assets/${name}` },
        );
      }
    }
    return { count: assets.length };
  },
});
