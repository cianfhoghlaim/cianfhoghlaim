import { query } from "../_generated/server";
import { v } from "convex/values";
import { isValidPersonaSlug } from "./helpers";

export const getPage = query({
  args: { personaSlug: v.string(), route: v.string() },
  handler: async (ctx, args) => {
    if (!isValidPersonaSlug(args.personaSlug)) return null;
    return await ctx.db
      .query("portfolioPages")
      .withIndex("by_persona_route", (q) =>
        q.eq("personaSlug", args.personaSlug).eq("route", args.route),
      )
      .first();
  },
});

export const listPages = query({
  args: { personaSlug: v.string() },
  handler: async (ctx, args) => {
    if (!isValidPersonaSlug(args.personaSlug)) return [];
    return await ctx.db
      .query("portfolioPages")
      .withIndex("by_persona_route", (q) => q.eq("personaSlug", args.personaSlug))
      .collect();
  },
});
