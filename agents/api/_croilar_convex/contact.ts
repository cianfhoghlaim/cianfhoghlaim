import { mutation } from "../_generated/server";
import { v } from "convex/values";
import { isValidPersonaSlug } from "./helpers";

export const submit = mutation({
  args: {
    personaSlug: v.string(),
    name: v.string(),
    email: v.string(),
    message: v.string(),
  },
  handler: async (ctx, args) => {
    if (!isValidPersonaSlug(args.personaSlug)) {
      throw new Error("Invalid persona slug");
    }
    if (args.message.length < 10) {
      throw new Error("Message too short (min 10 chars)");
    }
    if (!args.email.includes("@")) {
      throw new Error("Invalid email");
    }

    const id = await ctx.db.insert("contactSubmissions", {
      personaSlug: args.personaSlug,
      name: args.name,
      email: args.email,
      message: args.message,
      createdAt: Date.now(),
      isRead: false,
    });

    return { id };
  },
});

export const list = mutation({
  args: { personaSlug: v.string() },
  handler: async (ctx, args) => {
    if (!isValidPersonaSlug(args.personaSlug)) return [];
    return await ctx.db
      .query("contactSubmissions")
      .withIndex("by_persona", (q) => q.eq("personaSlug", args.personaSlug))
      .order("desc")
      .collect();
  },
});

export const markRead = mutation({
  args: { id: v.id("contactSubmissions") },
  handler: async (ctx, args) => {
    await ctx.db.patch(args.id, { isRead: true });
  },
});
