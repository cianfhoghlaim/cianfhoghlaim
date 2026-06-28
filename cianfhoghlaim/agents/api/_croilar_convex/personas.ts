import { query } from "../_generated/server";
import { v } from "convex/values";
import { PERSONAS, isValidPersonaSlug } from "./helpers";

export const list = query({
  args: {},
  handler: async (ctx) => {
    const personas = await ctx.db.query("personas").collect();
    return personas.filter((p) => p.isActive);
  },
});

export const listSeeds = query({
  args: {},
  handler: async () => {
    return PERSONAS;
  },
});

export const getBySlug = query({
  args: { slug: v.string() },
  handler: async (ctx, args) => {
    if (!isValidPersonaSlug(args.slug)) {
      return null;
    }
    return await ctx.db
      .query("personas")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .first();
  },
});

export const getDataSources = query({
  args: { slug: v.string() },
  handler: async (ctx, args) => {
    if (!isValidPersonaSlug(args.slug)) return [];
    const persona = await ctx.db
      .query("personas")
      .withIndex("by_slug", (q) => q.eq("slug", args.slug))
      .first();
    return persona?.dataSources ?? [];
  },
});
