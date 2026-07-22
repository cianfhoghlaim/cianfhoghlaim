// Hono oRPC router: tertiary — Cianfhoghlaim Oideachais
import { os, z } from "@orpc/server";

export const tertiary = os.$context<Context>().router({
  getCAOCourses: os
    .input(z.object({ hei: z.string().optional(), nfq_level: z.string().optional(), year: z.number().default(2024) }))
    .handler(async ({ input }) => {
      return {
        year: input.year,
        hei: input.hei,
        nfq_level: input.nfq_level,
        courses: [],
        message: "Stub: real implementation calls baml.ExtractCAOCourseList.",
      };
    }),

  getMatriculationRules: os
    .input(z.object({ institution: z.string(), pathway: z.enum(["leaving_certificate", "qqi_fet", "mature_student", "dare", "hear", "international", "graduate", "apprenticeship"]).default("leaving_certificate") }))
    .handler(async ({ input }) => {
      return {
        institution: input.institution,
        pathway: input.pathway,
        rules: [],
        message: "Stub: real implementation calls baml.ExtractMatriculationRules.",
      };
    }),

  getApplicationTimeline: os
    .input(z.object({ year: z.number().default(2026) }))
    .handler(async ({ input }) => {
      return {
        year: input.year,
        cao_open_date: "2025-11-05",
        cao_close_date: "2026-02-01",
        late_application_close: "2026-03-01",
        offer_round_1: "2026-08-21",
        offer_round_2: "2026-08-28",
        registration_open: "2026-08-25",
        message: "Stub: real implementation calls baml.ExtractApplicationTimeline.",
      };
    }),

  auditMatriculation: os
    .input(z.object({ institution: z.string(), applicant_grades: z.record(z.string()), pathway: z.enum(["leaving_certificate", "qqi_fet", "mature_student", "dare", "hear", "international", "graduate", "apprenticeship"]).default("leaving_certificate") }))
    .handler(async ({ input }) => {
      return {
        institution: input.institution,
        pathway: input.pathway,
        passed: true,
        failed_requirements: [],
        near_misses: [],
        summary_en: "Stub: real implementation calls baml.AuditMatriculation (uses Claude Sonnet 4).",
        summary_ga: "Stub: feidhmíocht iarbhír a ghlaonn baml.AuditMatriculation (Úsáideann Claude Sonnet 4).",
      };
    }),

  predictPoints: os
    .input(z.object({ course_code: z.string(), applicant_grades: z.record(z.string()) }))
    .handler(async ({ input }) => {
      return {
        course_code: input.course_code,
        predicted_cutoff: 0,
        confidence: 0.0,
        message: "Stub: real implementation calls baml.EstimateCoursePoints.",
      };
    }),
});
