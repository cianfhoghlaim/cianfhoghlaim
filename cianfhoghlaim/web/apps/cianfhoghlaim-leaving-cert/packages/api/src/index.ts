// @cianfhoghlaim/api — Shared oRPC router + context + schemas
// The root oRPC router exposed to both apps/web (typed client) and apps/api (RPC handler).

import { os } from "@orpc/server";
import { z } from "zod";

import { leavingCertRouter } from "./routers/leaving-cert";
import { diagramsRouter } from "./routers/diagrams";
import { assetsRouter } from "./routers/assets";
import { rootPdfsRouter } from "./routers/root-pdfs";
import { badgesRouter } from "./routers/badges";
import { practiceRouter } from "./routers/practice";
import { i18nRouter } from "./routers/i18n";

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
  // TODO: read BetterAuth session from cookies (Phase 2 T2.8)
  const _ = opts;
  return { session: null };
}

// ── Root router ────────────────────────────────────────────────────────

export const appRouter = os.$context<ApiContext>().router({
  health: os.handler(async () => ({ status: "ok" })),

  leavingCert: leavingCertRouter,
  diagrams: diagramsRouter,
  assets: assetsRouter,
  rootPdfs: rootPdfsRouter,
  badges: badgesRouter,
  practice: practiceRouter,
  i18n: i18nRouter,

  // TODO Phase 4: geospatial, baml, key_competencies,
  //   aistear, primary, junior_cycle, senior_cycle, tertiary
});

export type AppRouter = typeof appRouter;
export { z };