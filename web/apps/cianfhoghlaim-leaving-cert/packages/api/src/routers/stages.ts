// @cianfhoghlaim/api — stages oRPC router
// The 5 NCCA education stages (aistear + primary + junior_cycle + senior_cycle + tertiary).

import { os } from "@orpc/server";
import { z } from "zod";
import type { ApiContext } from "../context";

const StageSchema = z.enum([
  "aistear",
  "primary",
  "junior_cycle",
  "senior_cycle",
  "tertiary",
]);

const STAGE_INFO: Record<z.infer<typeof StageSchema>, {
  name_en: string;
  name_ga: string;
  age_range: string;
  description_en: string;
  mythological_invasions: readonly string[];
}> = {
  aistear: {
    name_en: "Aistear (Early Childhood)",
    name_ga: "Aistear (Luath-Óige)",
    age_range: "0-6",
    description_en: "The 4 Aistear themes (Well-being, Identity & Belonging, Communicating, Exploring & Thinking).",
    mythological_invasions: ["cessair"],
  },
  primary: {
    name_en: "Primary",
    name_ga: "Bunscoil",
    age_range: "4-12",
    description_en: "The 12 Primary curriculum areas.",
    mythological_invasions: ["partholon"],
  },
  junior_cycle: {
    name_en: "Junior Cycle",
    name_ga: "Iar-Bhunscoil",
    age_range: "12-15",
    description_en: "The 18 Junior Cycle subjects + 16 short courses, 2 CBAs each.",
    mythological_invasions: ["nemedians"],
  },
  senior_cycle: {
    name_en: "Senior Cycle",
    name_ga: "Scoil Daraigh",
    age_range: "15-18",
    description_en: "The 50+ Leaving Cert subjects.",
    mythological_invasions: ["fomorians"],
  },
  tertiary: {
    name_en: "Tertiary + Enduring Learning",
    name_ga: "Ardleibhéal + Foghlaim Bhuan",
    age_range: "18+",
    description_en: "The 5 NCCA Key Competencies as the culminating end-of-secondary mastery.",
    mythological_invasions: ["tuatha_de_danann"],
  },
};

export const stagesRouter = os.$context<ApiContext>().router({
  list: os
    .input(z.object({ language: z.enum(["en", "ga"]).default("en") }))
    .handler(async ({ input }) => {
      const stages = Object.entries(STAGE_INFO).map(([slug, info]) => ({
        slug,
        name: input.language === "ga" ? info.name_ga : info.name_en,
        age_range: info.age_range,
        description: info.description_en,
        mythological_invasions: info.mythological_invasions,
      }));
      return { language: input.language, stages };
    }),

  get: os
    .input(z.object({
      stage: StageSchema,
      language: z.enum(["en", "ga"]).default("en"),
    }))
    .handler(async ({ input }) => {
      const info = STAGE_INFO[input.stage];
      return {
        slug: input.stage,
        name: input.language === "ga" ? info.name_ga : info.name_en,
        age_range: info.age_range,
        description: info.description_en,
        mythological_invasions: info.mythological_invasions,
      };
    }),
});