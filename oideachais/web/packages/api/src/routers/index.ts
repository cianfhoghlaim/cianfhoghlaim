import type { RouterClient } from "@orpc/server";
import { publicProcedure, protectedProcedure } from "../index";
import { lakehouseRouter } from "./lakehouse";
import { examsRouter } from "./exams";
import { motherduckRouter } from "./motherduck";

export const appRouter = {
  health: publicProcedure.handler(() => "OK"),

  me: protectedProcedure.handler(({ context }) => ({
    user: context.session?.user ?? null,
  })),

  lakehouse: lakehouseRouter,
  exams: examsRouter,
  motherduck: motherduckRouter,
};

export type AppRouter = typeof appRouter;
export type AppRouterClient = RouterClient<typeof appRouter>;
