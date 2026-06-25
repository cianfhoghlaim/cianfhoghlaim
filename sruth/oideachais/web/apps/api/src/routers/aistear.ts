// Hono oRPC router: aistear — Cianfhoghlaim Oideachais
// Read from the oideachais.aistear Cognee dataset + aistear_knowledge_graph LanceDB table.
import { os, z } from "@orpc/server";

export const aistear = os.$context<Context>().router({
  getThemes: os
    .input(z.object({ language: z.enum(["en", "ga"]).default("en") }))
    .handler(async ({ input }) => {
      return {
        themes: [
          { slug: "WELL_BEING", name_en: "Well-being", name_ga: "Biú Folláine" },
          { slug: "IDENTITY_BELONGING", name_en: "Identity & Belonging", name_ga: "Céannacht agus Muintearas" },
          { slug: "COMMUNICATING", name_en: "Communicating", name_ga: "Cumarsáid" },
          { slug: "EXPLORING_THINKING", name_en: "Exploring & Thinking", name_ga: "Taiscéalaíocht agus Smaointeoireacht" },
        ],
        language: input.language,
      };
    }),

  getLearningGoals: os
    .input(z.object({ theme: z.string(), age_band: z.string().optional() }))
    .handler(async ({ input }) => {
      return {
        theme: input.theme,
        age_band: input.age_band,
        goals: [],
        message: "Stub: real implementation queries aistear_knowledge_graph LanceDB table.",
      };
    }),

  getNaionra: os
    .input(z.object({ county: z.string().optional(), bbox: z.tuple([z.number(), z.number(), z.number(), z.number()]).optional() }))
    .handler(async ({ input }) => {
      return {
        naionra: [],
        message: "Stub: real implementation reads from naionra_listings DLT source.",
      };
    }),
});
