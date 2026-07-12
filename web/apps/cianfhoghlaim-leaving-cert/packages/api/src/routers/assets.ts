// @cianfhoghlaim/api — assets oRPC router
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T4.4.
// 3D + 2D asset list + get + generate.

import { os } from "@orpc/server";
import { z } from "zod";
import type { ApiContext } from "../context";

const SubjectSchema = z.enum([
  "mathematics", "applied_mathematics", "chemistry", "geography",
  "history", "english", "gaeilge", "computer_science",
]);

export const assetsRouter = os.$context<ApiContext>().router({
  list: os
    .input(z.object({
      subject: SubjectSchema,
      format: z.enum(["all", "3d-mesh", "2d-sprite"]).default("all"),
      page: z.number().int().min(1).default(1),
      perPage: z.number().int().min(1).max(50).default(12),
    }))
    .handler(async ({ input }) => {
      // TODO: list the assets from s3://cianfhoghlaim-asset-v2/{3d,2d}/{subject}/
      return {
        subject: input.subject,
        format: input.format,
        page: input.page,
        perPage: input.perPage,
        total: 0,
        assets: [],
      };
    }),

  get3D: os
    .input(z.object({
      subject: SubjectSchema,
      slug: z.string(),
    }))
    .handler(async ({ input }) => {
      // TODO: return the signed R2 URL for the GLB file
      return {
        subject: input.subject,
        slug: input.slug,
        format: "glb",
        url: `https://r2.cianfhoghlaim.ie/cianfhoghlaim-asset-v2/3d/${input.subject}/${input.slug}.glb`,
        signed_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 3600_000).toISOString(),
      };
    }),

  generate3D: os
    .input(z.object({
      subject: SubjectSchema,
      prompt: z.string(),
      tier: z.number().int().min(1).max(13).default(3),
    }))
    .handler(async ({ input }) => {
      // TODO: call baml.qpack_<subject>.baml `Generate3DAssetPrompt(prompt, subject)`
      // then TRELLIS.2 + SAM-3D-Objects + R2 upload
      return {
        status: "queued",
        subject: input.subject,
        prompt: input.prompt,
        tier: input.tier,
        estimated_minutes: 8,
        job_id: `gen-${Date.now()}`,
      };
    }),
});