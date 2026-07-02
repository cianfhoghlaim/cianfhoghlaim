// @cianfhoghlaim/api — baml oRPC router
// Lazy BAML extraction (on-demand from the SPA) + SuggestUIComponents.
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md.

import { os } from "@orpc/server";
import { z } from "zod";
import type { ApiContext } from "../context";

export const bamlRouter = os.$context<ApiContext>().router({
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
      // TODO: check the Convex `extraction_budget` table for the session's
      // remaining budget + queue the BAML extraction if budget allows
      return {
        status: "queued",
        budget_remaining: 4,
        message: "Stub: real implementation checks the extraction_budget Convex table, then fires baml.LazyExtractExamPaper.",
      };
    }),

  suggestUIComponents: os
    .input(z.object({
      stage: z.string().default("all"),
      extracted_subjects: z.array(z.string()).default([]),
    }))
    .handler(async ({ input }) => {
      // TODO: call baml.SuggestUIComponents(stage, extracted_subjects)
      return {
        stage: input.stage,
        suggestions: [],
        message: "Stub: real implementation calls baml.SuggestUIComponents nightly.",
      };
    }),
});