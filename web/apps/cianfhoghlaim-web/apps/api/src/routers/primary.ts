// Hono oRPC router: primary — Cianfhoghlaim Oideachais
import { os, z } from "@orpc/server";

export const primary = os.$context<Context>().router({
  getCurriculumArea: os
    .input(z.object({ area: z.string(), stage: z.string().optional() }))
    .handler(async ({ input }) => {
      return {
        area: input.area,
        stage: input.stage,
        strands: [],
        message: "Stub: real implementation queries primary_knowledge_graph LanceDB table.",
      };
    }),

  getStrand: os
    .input(z.object({ area: z.string(), strand_name: z.string() }))
    .handler(async ({ input }) => {
      return {
        area: input.area,
        strand: input.strand_name,
        outcomes: [],
      };
    }),
});
