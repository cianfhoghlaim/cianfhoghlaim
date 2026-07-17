// Hono oRPC router: i18n — Cianfhoghlaim Oideachais
// Lazy EN↔GA translation via litellm/irish (UCCIX → Qomhrá → BritLLM fallback).
import { os, z } from "@orpc/server";

export const i18n = os.$context<Context>().router({
  translate: os
    .input(z.object({
      text: z.string(),
      source_language: z.enum(["en", "ga"]).default("en"),
      target_language: z.enum(["en", "ga"]).default("ga"),
      preserve_terminology: z.boolean().default(true),
    }))
    .handler(async ({ input }) => {
      return {
        text: input.text,
        source_language: input.source_language,
        target_language: input.target_language,
        translation: input.text,
        model: "litellm/irish",
        message: "Stub: real implementation calls litellm with the `irish` model alias.",
      };
    }),
});
