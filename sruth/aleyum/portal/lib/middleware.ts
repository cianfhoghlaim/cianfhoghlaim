import { auth } from "./auth";

export interface AuthContext {
  session: Awaited<ReturnType<typeof auth.api.getSession>> | null;
  request: Request;
}

/**
 * Authentication middleware for TanStack Start server routes
 * Checks for valid session and redirects to login if not authenticated
 */
export const authMiddleware = async ({ request }: { request: Request }) => {
  const session = await auth.api.getSession({
    headers: request.headers,
  });

  // Public routes that don't require authentication
  const publicRoutes = ["/login", "/api/auth", "/api/health"];

  const isPublicRoute = publicRoutes.some((route) =>
    request.url.includes(route)
  );

  // Allow public routes
  if (isPublicRoute) {
    return {
      session,
      request,
    };
  }

  // Redirect to login if no session
  if (!session) {
    const url = new URL(request.url);
    const loginUrl = new URL("/login", url.origin);
    loginUrl.searchParams.set("redirect", url.pathname + url.search);
    throw Response.redirect(loginUrl.toString(), 302);
  }

  return {
    session,
    request,
  };
};
