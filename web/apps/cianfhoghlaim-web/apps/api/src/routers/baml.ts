// Hono oRPC router: baml — Cianfhoghlaim Oideachais
// Lazy BAML extraction (on-demand from the SPA) and SuggestUIComponents.
import { os, z } from "@orpc/server";

export const baml = os.$context<Context>().router({
  lazyExtract: os
    .input(z.object({
      stage: z.enum(["aistear", "primary", "junior_cycle", "senior_cycle", "tertiary"]),
      subject: z.string(),
      year: z.number(),
      level: z.string().default("higher"),
      paper_number: z.number().default(1),
      session_id: z.string(),
    }))
    .handler(async ({ input }) => {
      return {
        status: "queued",
        budget_remaining: 4,
        message: "Stub: real implementation checks the extraction_budget Convex table, then fires baml.LazyExtractExamPaper.",
      };
    }),

  suggestUIComponents: os
    .input(z.object({ stage: z.string().default("all"), extracted_subjects: z.array(z.string()).default([]) }))
    .handler(async ({ input }) => {
      return {
        stage: input.stage,
        suggestions: [],
        message: "Stub: real implementation calls baml.SuggestUIComponents nightly.",
      };
    }),
});
