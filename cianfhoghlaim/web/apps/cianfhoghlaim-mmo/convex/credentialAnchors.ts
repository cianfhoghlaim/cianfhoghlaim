// Convex functions for the credentialAnchors table.

import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

// Create a new credential anchor row.
export const create = mutation({
  args: {
    batchId: v.string(),
    batchDate: v.string(),
    merkleRoot: v.string(),
    leafCount: v.number(),
    badgeIds: v.array(v.string()),
    publishedBy: v.string(),
  },
  handler: async (ctx, args) => {
    const id = await ctx.db.insert("credentialAnchors", {
      ...args,
      publishedAt: undefined,
      txHash: undefined,
    });
    return id;
  },
});

// Set the on-chain tx_hash after publishing to Base L2.
export const setTxHash = mutation({
  args: {
    id: v.id("credentialAnchors"),
    txHash: v.string(),
  },
  handler: async (ctx, { id, txHash }) => {
    await ctx.db.patch(id, { txHash, publishedAt: Date.now() });
  },
});

// Look up an anchor by date (YYYY-MM-DD).
export const byDate = query({
  args: { batchDate: v.string() },
  handler: async (ctx, { batchDate }) => {
    return await ctx.db
      .query("credentialAnchors")
      .withIndex("by_date", (q) => q.eq("batchDate", batchDate))
      .first();
  },
});