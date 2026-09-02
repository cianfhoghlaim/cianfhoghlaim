import type { RouterClient } from "@orpc/server";
import { publicProcedure, protectedProcedure, tracedProcedure } from "../index";
import { lakehouseRouter } from "./lakehouse";
import { examsRouter } from "./exams";
import { motherduckRouter } from "./motherduck";
import { bamlRouter } from "./baml";

export const appRouter = {
  // Health checks are not traced (high frequency, low value)
  health: publicProcedure.handler(() => "OK"),

  // Traced public operations
  lakehouse: lakehouseRouter,
  exams: examsRouter,
  motherduck: motherduckRouter,
  baml: bamlRouter,

  // Protected procedures (auth + tracing)
  me: protectedProcedure.handler(({ context }) => ({
    user: context.session?.user ?? null,
  })),
};

export type AppRouter = typeof appRouter;
export type AppRouterClient = RouterClient<typeof appRouter>;
