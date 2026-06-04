import { ORPCError, os } from "@orpc/server";
import type { Context } from "./context";
import { auth } from "@oideachais/auth";

export const o = os.$context<Context>();

export const publicProcedure = o;

const requireAuth = o.middleware(async ({ context, next }) => {
  const session = await auth.api.getSession({
    headers: new Headers(),
  });
  if (!session?.user) {
    throw new ORPCError("UNAUTHORIZED");
  }
  return next({
    context: {
      session: {
        user: session.user,
        session: session.session,
      },
    },
  });
});

export const protectedProcedure = publicProcedure.use(requireAuth);
