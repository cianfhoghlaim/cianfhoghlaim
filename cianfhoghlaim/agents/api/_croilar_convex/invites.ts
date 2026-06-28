import { mutation } from "../_generated/server";
import { v } from "convex/values";
import { requireOrgRole } from "./helpers";

export const create = mutation({
  args: {
    orgSlug: v.string(),
    email: v.string(),
    role: v.union(v.literal("admin"), v.literal("member"), v.literal("viewer")),
  },
  handler: async (ctx, args) => {
    const id = await requireOrgRole(ctx, "admin", ["owner", "admin"]);
    const org = await ctx.db
      .query("organizations")
      .withIndex("by_slug", (q) => q.eq("slug", args.orgSlug))
      .first();
    if (!org) throw new Error(`Organization ${args.orgSlug} not found`);

    const code = crypto.randomUUID();
    const expiresAt = Date.now() + 7 * 24 * 60 * 60 * 1000;
    const inviteId = await ctx.db.insert("invites", {
      orgId: org._id,
      email: args.email,
      role: args.role,
      code,
      status: "pending",
      createdAt: Date.now(),
      expiresAt,
    });

    await ctx.db.insert("portalAuditLog", {
      userId: id.userId,
      orgId: org._id,
      action: "create_invite",
      targetType: "invite",
      targetName: args.email,
      outcome: "success",
      timestamp: Date.now(),
    });

    return { inviteId, code };
  },
});

export const accept = mutation({
  args: { code: v.string() },
  handler: async (ctx, args) => {
    const id = await requireOrgRole(ctx, "collab", ["owner", "admin", "member", "viewer"]);
    const invite = await ctx.db
      .query("invites")
      .withIndex("by_code", (q) => q.eq("code", args.code))
      .first();
    if (!invite) throw new Error("Invite not found");
    if (invite.status !== "pending") throw new Error(`Invite already ${invite.status}`);
    if (invite.expiresAt < Date.now()) {
      await ctx.db.patch(invite._id, { status: "expired" });
      throw new Error("Invite expired");
    }

    await ctx.db.insert("memberships", {
      orgId: invite.orgId,
      userId: id.userId,
      role: invite.role as "owner" | "admin" | "member" | "viewer",
      invitedAt: invite.createdAt,
    });
    await ctx.db.patch(invite._id, { status: "accepted" });

    await ctx.db.insert("portalAuditLog", {
      userId: id.userId,
      orgId: invite.orgId,
      action: "accept_invite",
      targetType: "invite",
      targetName: invite.email,
      outcome: "success",
      timestamp: Date.now(),
    });

    return { orgId: invite.orgId };
  },
});
