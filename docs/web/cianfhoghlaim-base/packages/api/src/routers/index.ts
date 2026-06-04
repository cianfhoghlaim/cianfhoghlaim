import type { RouterClient } from "@orpc/server";

import { protectedProcedure, publicProcedure } from "../index";
import { pipelineRouter } from "./pipeline";
import { mcpRouter } from "./mcp";

export const appRouter = {
  healthCheck: publicProcedure.handler(() => {
    return "OK";
  }),
  privateData: protectedProcedure.handler(({ context }) => {
    return {
      message: "This is private",
      user: context.session?.user,
    };
  }),

  // Pipeline routes (FastAPI data pipelines)
  pipeline: pipelineRouter,

  // MCP routes (Model Context Protocol servers)
  mcp: mcpRouter,
};
export type AppRouter = typeof appRouter;
export type AppRouterClient = RouterClient<typeof appRouter>;
