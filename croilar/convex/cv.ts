import { query } from "../_generated/server";
import { v } from "convex/values";
import { isValidPersonaSlug } from "./helpers";

export const list = query({
  args: {
    personaSlug: v.string(),
    type: v.optional(v.union(
      v.literal("education"),
      v.literal("award"),
      v.literal("publication"),
      v.literal("reference"),
      v.literal("experience"),
    )),
  },
  handler: async (ctx, args) => {
    if (!isValidPersonaSlug(args.personaSlug)) return [];
    if (args.type) {
      return await ctx.db
        .query("cvEntries")
        .withIndex("by_persona_type", (q) =>
          q.eq("personaSlug", args.personaSlug).eq("type", args.type!),
        )
        .order("desc")
        .collect();
    }
    return await ctx.db
      .query("cvEntries")
      .withIndex("by_persona_date", (q) => q.eq("personaSlug", args.personaSlug))
      .order("desc")
      .collect();
  },
});
