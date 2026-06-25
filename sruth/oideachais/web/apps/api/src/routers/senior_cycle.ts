// Hono oRPC router: senior_cycle — Cianfhoghlaim Oideachais
// Extends the existing exams router with the new per-subject rubric + essay scoring.
import { os, z } from "@orpc/server";

export const senior_cycle = os.$context<Context>().router({
  getExamPaper: os
    .input(z.object({ subject: z.string(), year: z.number(), level: z.string(), paper_number: z.number().default(1) }))
    .handler(async ({ input }) => {
      return {
        subject: input.subject,
        year: input.year,
        level: input.level,
        paper_number: input.paper_number,
        sections: [],
        message: "Stub: real implementation calls baml.LazyExtractExamPaper (memoised in LanceDB).",
      };
    }),

  getMarkingScheme: os
    .input(z.object({ subject: z.string(), year: z.number(), level: z.string() }))
    .handler(async ({ input }) => {
      return {
        subject: input.subject,
        year: input.year,
        level: input.level,
        sections: [],
        message: "Stub: real implementation calls baml.ExtractMarkingScheme.",
      };
    }),

  getSubjectRubric: os
    .input(z.object({ subject: z.string() }))
    .handler(async ({ input }) => {
      return {
        subject: input.subject,
        style: "PCLM",
        descriptors: [],
        message: "Stub: real implementation calls baml.ExtractSubjectRubric.",
      };
    }),

  scoreEssay: os
    .input(z.object({ subject: z.string(), essay: z.string(), question_id: z.string().optional() }))
    .handler(async ({ input }) => {
      return {
        subject: input.subject,
        score: 0,
        descriptor_scores: {},
        strengths: [],
        improvements: [],
        message: "Stub: real implementation calls baml.ScoreEssayAgainstRubric (uses Claude Sonnet 4).",
      };
    }),

  compareMarkingSchemes: os
    .input(z.object({ subject: z.string(), year_a: z.number(), year_b: z.number() }))
    .handler(async ({ input }) => {
      return {
        subject: input.subject,
        year_a: input.year_a,
        year_b: input.year_b,
        added_questions: [],
        removed_questions: [],
        changed_marks: {},
        message: "Stub: real implementation calls baml.CompareMarkingSchemes.",
      };
    }),
});
