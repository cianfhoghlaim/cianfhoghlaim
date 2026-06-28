import { QueryCtx, MutationCtx, ActionCtx } from "../_generated/server";
import { Id } from "../_generated/dataModel";

export const PERSONAS = ["aleyum", "cianfhoghlaim"] as const;
export type PersonaSlug = (typeof PERSONAS)[number];

export const ORG_SLUGS = ["aleyum", "cianfhoghlaim", "croilar-admin", "croilar-collab"] as const;
export type OrgSlug = (typeof ORG_SLUGS)[number];

export const ORG_ROLES = [
  "owner",
  "admin",
  "developer",
  "member",
  "viewer",
] as const;
export type OrgRole = (typeof ORG_ROLES)[number];

export type Ctx = QueryCtx | MutationCtx | ActionCtx;

export type AuthIdentity = {
  userId: string;
  orgId: string | null;
  role: OrgRole | null;
};

export async function getIdentity(ctx: Ctx): Promise<AuthIdentity | null> {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) return null;
  const orgId = (identity as { orgId?: string }).orgId ?? null;
  const role = ((identity as { role?: string }).role ?? null) as OrgRole | null;
  if (role !== null && !ORG_ROLES.includes(role)) {
    return { userId: identity.subject, orgId, role: null };
  }
  return { userId: identity.subject, orgId, role };
}

export async function requireAuth(ctx: Ctx): Promise<AuthIdentity> {
  const id = await getIdentity(ctx);
  if (!id) throw new Error("Authentication required");
  return id;
}

export async function requireOrgRole(
  ctx: Ctx,
  orgSlug: OrgSlug,
  allowedRoles: OrgRole[] = ["owner", "admin", "developer", "member", "viewer"],
): Promise<AuthIdentity> {
  const id = await requireAuth(ctx);
  const org = await ctx.db
    .query("organizations")
    .withIndex("by_slug", (q) => q.eq("slug", orgSlug))
    .first();
  if (!org) throw new Error(`Organization ${orgSlug} not found`);

  if (id.orgId !== org._id) {
    throw new Error(`Membership in ${orgSlug} required`);
  }

  const membership = await ctx.db
    .query("memberships")
    .withIndex("by_user_org", (q) => q.eq("userId", id.userId).eq("orgId", org._id))
    .first();

  if (!membership || !allowedRoles.includes(membership.role)) {
    throw new Error(`Role ${allowedRoles.join("/")} required in ${orgSlug}`);
  }

  return id;
}

export async function isPersonaPublicReadOnly(_ctx: Ctx, slug: string): Promise<boolean> {
  return PERSONAS.includes(slug as PersonaSlug);
}

export function isValidPersonaSlug(slug: string): slug is PersonaSlug {
  return PERSONAS.includes(slug as PersonaSlug);
}

/**
 * Convenience: the set of roles that can read the devtools hub.
 * Developers + admins can read; members and viewers cannot.
 */
export const DEVTOOLS_READ_ROLES: OrgRole[] = ["owner", "admin", "developer"];

/**
 * Convenience: only owners + admins can mutate the devtables.
 * (Developers can read but not write.)
 */
export const DEVTOOLS_WRITE_ROLES: OrgRole[] = ["owner", "admin"];

/**
 * Convenience: gate a Convex query behind the `croilar-admin` org and a
 * developer-or-higher role.
 */
export async function requireDevtoolsRead(ctx: Ctx): Promise<AuthIdentity> {
  return await requireOrgRole(ctx, "croilar-admin", DEVTOOLS_READ_ROLES);
}
