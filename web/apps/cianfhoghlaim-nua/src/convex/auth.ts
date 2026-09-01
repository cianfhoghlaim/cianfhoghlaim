/**
 * Convex auth integration for the consolidated cianfhoghlaim-nua app.
 *
 * Per the 2026-09-01-cianfhoghlaim-nua-web-consolidation-v1 change
 * (Phase 3 §B.6). The BetterAuth trigger syncs Better Auth users
 * → Convex `users` table.
 *
 * Lifted + simplified from the oideachais-dashboard
 * `convex/auth.ts`. Uses the canonical Convex auth pattern.
 */

import type { MutationCtx } from "../_generated/server";

export async function syncBetterAuthUser(
  ctx: MutationCtx,
  args: {
    better_auth_id: string;
    email: string;
    name?: string;
    image?: string;
  },
) {
  // Check if user already exists
  const existing = await ctx.db
    .query("users")
    .withIndex("by_better_auth_id", (q) => q.eq("better_auth_id", args.better_auth_id))
    .first();
  if (existing) {
    return existing._id;
  }
  // Create new user
  return await ctx.db.insert("users", {
    better_auth_id: args.better_auth_id,
    email: args.email,
    name: args.name,
    image: args.image,
    role: "user",
    aud: "convex_backend",
    created_at: Date.now(),
    updated_at: Date.now(),
  });
}
