// @cianfhoghlaim/api — i18n oRPC router
// The bilingual string tables for the EN + GA UI strings.

import { os } from "@orpc/server";
import { z } from "zod";
import type { ApiContext } from "../context";

export const i18nRouter = os.$context<ApiContext>().router({
  getStrings: os
    .input(z.object({
      language: z.enum(["en", "ga"]),
      namespace: z.string().default("common"),
    }))
    .handler(async ({ input }) => {
      // TODO: load from packages/i18n/src/{en.json,ga.json}
      return {
        language: input.language,
        namespace: input.namespace,
        strings: {
          // Common UI strings
          "header.tagline": input.language === "ga"
            ? "Aes Sedai — freastalaithe ar gach duine"
            : "Aes Sedai — servants of all",
          "nav.curriculum": input.language === "ga" ? "Curaclam" : "Curriculum",
          "nav.exams": input.language === "ga" ? "Scrúduithe" : "Exams",
          "nav.marking-schemes": input.language === "ga" ? "Scéimeanna Marcála" : "Marking Schemes",
          "nav.practice": input.language === "ga" ? "Cleachtadh" : "Practice",
          "nav.assets": input.language === "ga" ? "Sócmhainní" : "Assets",
          "nav.dagster-runs": input.language === "ga" ? "Rithanna Dagster" : "Dagster Runs",
          "nav.settings": input.language === "ga" ? "Socruithe" : "Settings",
          // Subject names
          "subject.mathematics": input.language === "ga" ? "Mata" : "Mathematics",
          "subject.applied_mathematics": input.language === "ga" ? "Mata Feidhmíoch" : "Applied Mathematics",
          "subject.chemistry": input.language === "ga" ? "Ceimic" : "Chemistry",
          "subject.geography": input.language === "ga" ? "Tíreolaíocht" : "Geography",
          "subject.history": input.language === "ga" ? "Stair" : "History",
          "subject.english": input.language === "ga" ? "Béarla" : "English",
          "subject.gaeilge": input.language === "ga" ? "Gaeilge" : "Gaeilge",
          "subject.computer_science": input.language === "ga" ? "Ríomheolaíocht" : "Computer Science",
          // Subnation names
          "subnation.eire": input.language === "ga" ? "Éire" : "Éire",
          "subnation.northern-ireland": input.language === "ga" ? "Tuaisceart Éireann" : "Northern Ireland",
          "subnation.scotland": input.language === "ga" ? "Albain" : "Scotland",
          "subnation.england": input.language === "ga" ? "Sasana" : "England",
          "subnation.wales": input.language === "ga" ? "an Bhreatain Bheag" : "Wales",
          "subnation.isle-of-man": input.language === "ga" ? "Ellan Vannin" : "Isle of Man",
        },
      };
    }),
});