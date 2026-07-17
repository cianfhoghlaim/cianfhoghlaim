// Hono oRPC router: junior_cycle — Cianfhoghlaim Oideachais
import { os, z } from "@orpc/server";

export const junior_cycle = os.$context<Context>().router({
  getSpecs: os
    .input(z.object({ subject: z.string().optional(), short_course: z.boolean().default(false) }))
    .handler(async ({ input }) => {
      return {
        subject: input.subject,
        specs: [],
        message: "Stub: real implementation queries junior_cycle_knowledge_graph.",
      };
    }),

  getCBATasks: os
    .input(z.object({ subject: z.string() }))
    .handler(async ({ input }) => {
      return {
        subject: input.subject,
        cba_1: { name: "CBA 1", descriptors: [] },
        cba_2: { name: "CBA 2", descriptors: [] },
      };
    }),
});
