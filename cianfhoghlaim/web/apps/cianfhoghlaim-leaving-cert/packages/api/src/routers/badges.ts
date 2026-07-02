// @cianfhoghlaim/api — badges oRPC router
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T4.5.
// Wired to cianfhoghlaim/tuatha/badges/ledger.py + cianfhoghlaim/tuatha/badges/anchor.py

import { os, z } from "@orpc/server";
import type { ApiContext } from "../context";

const EiraicTierSchema = z.number().int().min(1).max(13);

export const badgesRouter = os.$context<ApiContext>().router({
  issue: os
    .input(z.object({
      student_id: z.string(),
      framework: z.string(),
      level: z.string(),
      subject: z.string(),
      competency_code: z.string(),
      competency_text_en: z.string(),
      competency_text_ga: z.string().optional(),
      eiraic_tier: EiraicTierSchema,
      agent_issuer: z.string(),
      evidence: z.object({
        item_id: z.string(),
        response: z.string(),
        score_pct: z.number().min(0).max(100),
        feedback_en: z.string(),
        feedback_ga: z.string().optional(),
      }),
    }))
    .handler(async ({ input }) => {
      // TODO: call cianfhoghlaim.tuatha.badges.ledger.issue_badge(...)
      return {
        status: "queued",
        student_id: input.student_id,
        eiraic_tier: input.eiraic_tier,
        evidence_hash: "placeholder-sha256",
        message: "Badge will be issued in the next batch run",
      };
    }),

  fetch: os
    .input(z.object({
      student_id: z.string(),
      eiraic_tier: EiraicTierSchema.optional(),
      subject: z.string().optional(),
    }))
    .handler(async ({ input }) => {
      // TODO: query Convex `badge_ledger` for the student's badges
      return {
        student_id: input.student_id,
        badges: [],
      };
    }),

  anchorDaily: os
    .input(z.object({
      date: z.string().optional(), // ISO date (default = today UTC)
    }))
    .handler(async ({ input }) => {
      // TODO: call cianfhoghlaim.tuatha.badges.anchor.publish_anchor(...)
      // + post the Merkle root to Base L2 via CredAnchor.sol
      return {
        status: "queued",
        date: input.date ?? new Date().toISOString().split("T")[0],
        estimated_minutes: 3,
        message: "Daily Merkle anchor will be published within 3 minutes",
      };
    }),
});