import { createMiddleware } from "hono/factory";
import { HTTPException } from "hono/http-exception";
import { auth } from "./auth";

export type AuthVariables = {
  user: { id: string; email: string; name: string };
  session: { id: string; userId: string; expiresAt: Date };
  org: { id: string; slug: string; role: string };
};

export const requireAuth = createMiddleware<{ Variables: AuthVariables }>(async (c, next) => {
  const session = await auth.api.getSession({ headers: c.req.raw.headers });
  if (!session) {
    throw new HTTPException(401, { message: "Authentication required" });
  }
  c.set("user", {
    id: session.user.id,
    email: session.user.email,
    name: session.user.name,
  });
  c.set("session", {
    id: session.session.id,
    userId: session.session.userId,
    expiresAt: session.session.expiresAt,
  });
  await next();
});

export const requireOrg = (allowedSlug: "admin" | "aleyum" | "cianfhoghlaim" | "collab") =>
  createMiddleware<{ Variables: AuthVariables }>(async (c, next) => {
    const user = c.get("user");
    if (!user) {
      throw new HTTPException(401, { message: "Authentication required" });
    }
    const orgs = await auth.api.listOrganizations({ headers: c.req.raw.headers });
    const org = orgs?.find((o: { slug: string }) => {
      if (allowedSlug === "admin") return o.slug === "croilar-admin";
      if (allowedSlug === "collab") return o.slug === "croilar-collab";
      return o.slug === allowedSlug;
    });
    if (!org) {
      throw new HTTPException(403, { message: `Membership in ${allowedSlug} required` });
    }
    c.set("org", { id: org.id, slug: org.slug, role: "member" });
    await next();
  });
