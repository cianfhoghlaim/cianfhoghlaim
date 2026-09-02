import { redirect } from "@tanstack/react-router";
import { createMiddleware } from "@tanstack/react-start";
import { auth } from "./auth";

export const authMiddleware = createMiddleware().server(
  async ({ next, request }) => {
    const session = await auth.api.getSession({ headers: request.headers });

    if (!session) {
      throw redirect({ to: "/login" });
    }

    return await next({
      context: {
        session,
        user: session.user,
      },
    });
  }
);

export const optionalAuthMiddleware = createMiddleware().server(
  async ({ next, request }) => {
    const session = await auth.api.getSession({ headers: request.headers });

    return await next({
      context: {
        session: session || null,
        user: session?.user || null,
      },
    });
  }
);
