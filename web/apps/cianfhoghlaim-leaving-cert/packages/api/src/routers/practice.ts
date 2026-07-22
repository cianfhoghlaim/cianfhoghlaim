// @cianfhoghlaim/api — practice oRPC router
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T4.6.

import { os } from "@orpc/server";
import { z } from "zod";
import type { ApiContext } from "../context";

const SubjectSchema = z.enum([
  "mathematics", "applied_mathematics", "chemistry", "geography",
  "history", "english", "gaeilge", "computer_science",
]);

export const practiceRouter = os.$context<ApiContext>().router({
  start: os
    .input(z.object({
      subject: SubjectSchema,
      topic: z.string(),
      language: z.enum(["en", "ga"]).default("en"),
    }))
    .handler(async ({ input }) => {
      // TODO: call BAML `qpack_<subject>.baml.GenerateFormativeItems(...)`
      // + Convex `subject_sessions` to start a new session
      return {
        session_id: `sess-${Date.now()}`,
        subject: input.subject,
        topic: input.topic,
        language: input.language,
        items: [],
        started_at: new Date().toISOString(),
      };
    }),

  submit: os
    .input(z.object({
      session_id: z.string(),
      item_id: z.string(),
      response: z.string(),
      response_format: z.enum(["text", "latex", "image", "multiple_choice"]).default("text"),
      time_taken_seconds: z.number().int().min(0).default(0),
      hints_used: z.number().int().min(0).max(4).default(0),
    }))
    .handler(async ({ input }) => {
      // TODO: call BAML `qpack_<subject>.baml.ScoreFormativeResponse(...)`
      // + Convex `practice_attempts` to record the attempt
      // + Convex `badges` to issue a SkillTreeBadge if score >= 85
      return {
        status: "scored",
        session_id: input.session_id,
        item_id: input.item_id,
        score_pct: 85,
        feedback_en: "Great work! (placeholder feedback)",
        feedback_ga: "Obair iontach! (aiseolas áitsealaíoch)",
        badge_issued: false,
        badge_id: null,
      };
    }),
});