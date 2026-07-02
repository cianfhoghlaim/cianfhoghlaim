// @cianfhoghlaim/api — Shared oRPC router + context + schemas
// The root oRPC router exposed to both apps/web (typed client) and apps/api (RPC handler).

import { os } from "@orpc/server";
import { z } from "zod";

// ── Context ────────────────────────────────────────────────────────────

export interface ApiContext {
  session: {
    user: {
      id: string;
      name: string;
      email: string;
      role: "student" | "teacher" | "operator" | "public";
    } | null;
  } | null;
}

export async function createContext(opts: { context: unknown }): Promise<ApiContext> {
  // TODO: read BetterAuth session from cookies
  const ctx = opts.context as { req?: { header?: (name: string) => string } };
  const _ = ctx.req?.header?.("authorization"); // placeholder
  return { session: null };
}

// ── Root router ────────────────────────────────────────────────────────

export const appRouter = os.$context<ApiContext>().router({
  // Routers mounted here
  health: os.handler(async () => ({ status: "ok" })),
  // leaving-cert, diagrams, assets, badges, practice, geospatial, baml,
  // root_pdfs, key_competencies, aistear, primary, junior_cycle, senior_cycle,
  // tertiary, i18n are added in Phase 4 (T4.2-T4.14).
});

export type AppRouter = typeof appRouter;
export { z };