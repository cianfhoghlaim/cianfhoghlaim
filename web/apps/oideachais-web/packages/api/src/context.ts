import type { Context as HonoContext } from "hono";
import { auth } from "@oideachais/auth";

export interface SessionData {
  user: {
    id: string;
    name: string;
    email: string;
    emailVerified: boolean;
    image?: string | null;
    createdAt: Date;
    updatedAt: Date;
  };
  session: {
    id: string;
    expiresAt: Date;
    token: string;
    createdAt: Date;
    updatedAt: Date;
    ipAddress?: string | null;
    userAgent?: string | null;
    userId: string;
  };
}

export interface Context {
  session: SessionData | null;
}

export async function createContext(opts: {
  context: HonoContext;
}): Promise<Context> {
  try {
    const request = opts.context.req.raw;
    const rawResult: unknown = await auth.api.getSession({
      headers: request.headers,
    });
    if (!rawResult) return { session: null };
    const result = rawResult as SessionData;
    return {
      session: {
        user: result.user,
        session: result.session,
      },
    };
  } catch {
    return { session: null };
  }
}
