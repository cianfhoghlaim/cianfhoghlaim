import { ORPCError, os } from "@orpc/server";
import type { Context } from "./context";

export const o = os.$context<Context>();

export const publicProcedure = o;

const requireAuth = o.middleware(async ({ context, next }) => {
  // Context.session is resolved by createContext() in context.ts
  // which calls auth.api.getSession() with the actual request headers.
  if (!context.session?.user) {
    throw new ORPCError("UNAUTHORIZED", {
      message: "Authentication required. Sign in at /api/auth.",
    });
  }
  return next({
    context: {
      session: context.session,
    },
  });
});

export const protectedProcedure = publicProcedure.use(requireAuth);

// ---------------------------------------------------------------------------
// Langfuse tracing middleware
//
// Emits a trace for every oRPC procedure call. The trace includes the
// procedure name, latency, status, and (on error) stack trace.
//
// Configure Langfuse via env: LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY,
// LANGFUSE_HOST (set in .env.example). When LANGFUSE_PUBLIC_KEY is unset,
// tracing is a no-op (dev mode).

interface LangfuseTrace {
  createSpan: (name: string) {
    end: (metadata?: Record<string, unknown>) => void;
  };
}

let langfuseClient: LangfuseTrace | null = null;
async function getLangfuse(): Promise<LangfuseTrace | null> {
  if (langfuseClient) return langfuseClient;
  if (!process.env.LANGFUSE_PUBLIC_KEY || !process.env.LANGFUSE_SECRET_KEY) {
    return null;
  }
  try {
    const { Langfuse } = await import("langfuse");
    langfuseClient = new Langfuse({
      publicKey: process.env.LANGFUSE_PUBLIC_KEY,
      secretKey: process.env.LANGFUSE_SECRET_KEY,
      baseUrl: process.env.LANGFUSE_HOST,
    }) as unknown as LangfuseTrace;
    return langfuseClient;
  } catch {
    return null;
  }
}

export const withLangfuse = o.middleware(async ({ path, next }) => {
  const start = Date.now();
  const lf = await getLangfuse();
  const span = lf?.createSpan(`orpc:${path.join(".")}`);
  try {
    const result = await next();
    span?.end({
      duration_ms: Date.now() - start,
      path: path.join("."),
      status: "ok",
    });
    return result;
  } catch (err) {
    span?.end({
      duration_ms: Date.now() - start,
      path: path.join("."),
      status: "error",
      error: err instanceof Error ? err.message : String(err),
    });
    throw err;
  }
});

/**
 * Traced procedure — wraps a procedure with Langfuse tracing.
 * Use this in router definitions: `o.procedure.use(withLangfuse).handler(...)`
 */
export const tracedProcedure = publicProcedure.use(withLangfuse);
