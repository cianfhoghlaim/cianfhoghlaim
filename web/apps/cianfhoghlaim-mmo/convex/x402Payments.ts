// Convex functions for the x402Payments table.
//
// Backs agents/api/routes/routes/payments.py's `_ConvexPaymentStore` —
// the durable replacement for that module's in-memory
// `_payment_requests`/`_completed_payments` dicts (which lost all
// state on every process restart). Per
// 2026-08-08-learn-to-earn-x402-credential-pipeline-v1 Phase 4.

import { v } from "convex/values";
import { mutation, query } from "./_generated/server";

// Create a new pending payment request. `paymentId` is the x402
// route's own UUID (not the Convex `_id`), so lookups from Python can
// use it directly without round-tripping a Convex document ID.
export const create = mutation({
  args: {
    paymentId: v.string(),
    resourceType: v.string(),
    priceUsd: v.number(),
    priceCrypto: v.string(),
    token: v.string(),
    createdAt: v.string(),
    expiresAt: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("x402Payments", { ...args, status: "pending" });
  },
});

// `_ConvexPaymentStore.get()`'s sole lookup.
export const getByPaymentId = query({
  args: { paymentId: v.string() },
  handler: async (ctx, { paymentId }) => {
    return await ctx.db
      .query("x402Payments")
      .withIndex("by_payment_id", (q) => q.eq("paymentId", paymentId))
      .first();
  },
});

// Mark a payment verified after on-chain confirmation
// (agents/api/routes/routes/payments.py's `verify_payment` route).
export const markVerified = mutation({
  args: {
    paymentId: v.string(),
    transactionHash: v.string(),
    verifiedAt: v.string(),
  },
  handler: async (ctx, { paymentId, transactionHash, verifiedAt }) => {
    const row = await ctx.db
      .query("x402Payments")
      .withIndex("by_payment_id", (q) => q.eq("paymentId", paymentId))
      .first();
    if (!row) return;
    await ctx.db.patch(row._id, {
      status: "verified",
      transactionHash,
      verifiedAt,
    });
  },
});

// Mark a payment failed or expired.
export const markFailed = mutation({
  args: {
    paymentId: v.string(),
    status: v.string(), // 'failed' | 'expired'
    failureReason: v.optional(v.string()),
  },
  handler: async (ctx, { paymentId, status, failureReason }) => {
    const row = await ctx.db
      .query("x402Payments")
      .withIndex("by_payment_id", (q) => q.eq("paymentId", paymentId))
      .first();
    if (!row) return;
    await ctx.db.patch(row._id, { status, failureReason });
  },
});
