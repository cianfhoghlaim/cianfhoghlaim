// @cianfhoghlaim/api — root_pdfs oRPC router
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T4.12.
// The 5 root-level NCCA programme PDF endpoints.

import { os, z } from "@orpc/server";
import type { ApiContext } from "../context";

export const rootPdfsRouter = os.$context<ApiContext>().router({
  getKeyCompetencies: os
    .input(z.object({ language: z.enum(["en", "ga"]).default("en") }))
    .handler(async ({ input }) => {
      // TODO: query Convex `root_key_competencies_extracted` asset (or
      // call `b.ExtractKeyCompetencies(pdf_text)` directly)
      return {
        language: input.language,
        competencies: [
          {
            code: "KC-IP",
            name_en: "Information Processing",
            name_ga: "Próiseáil Faisnéise",
            definition_en: "The ability to access, evaluate, interpret, and manage information...",
            definition_ga: "An cumas rochtain, meastóireacht, léirmhíniú agus bainistíocht faisnéise a dhéanamh...",
            evidence: {
              source_pdf: "key-competencies-in-senior-cycle_en.pdf",
              source_page: 4,
              excerpt_en: "Information Processing: Students develop the ability to...",
            },
          },
          {
            code: "KC-CO",
            name_en: "Communicating",
            name_ga: "Cumarsáid",
            definition_en: "The ability to communicate effectively in a variety of contexts...",
            definition_ga: "An cumas cumarsáid éifeachtach a dhéanamh i gcomhthéacsanna éagsúla...",
            evidence: {
              source_pdf: "key-competencies-in-senior-cycle_en.pdf",
              source_page: 6,
              excerpt_en: "Communicating: Students develop the ability to...",
            },
          },
          {
            code: "KC-WO",
            name_en: "Working with Others",
            name_ga: "Ag Obair le Daoine Eile",
            definition_en: "The ability to interact and work collaboratively...",
            definition_ga: "An cumas idirghníomhú agus comhoibriú a dhéanamh...",
            evidence: {
              source_pdf: "key-competencies-in-senior-cycle_en.pdf",
              source_page: 8,
              excerpt_en: "Working with Others: Students develop the ability to...",
            },
          },
          {
            code: "KC-PE",
            name_en: "Personal Effectiveness",
            name_ga: "Éifeachtacht Phearsanta",
            definition_en: "The ability to develop self-awareness, resilience, motivation...",
            definition_ga: "An cumas féin-aird, athléimne, spreagadh a fhorbairt...",
            evidence: {
              source_pdf: "key-competencies-in-senior-cycle_en.pdf",
              source_page: 10,
              excerpt_en: "Personal Effectiveness: Students develop the ability to...",
            },
          },
          {
            code: "KC-CT",
            name_en: "Critical & Creative Thinking",
            name_ga: "Smaointeoireacht Chriticiúil agus Chruthaitheach",
            definition_en: "The ability to think analytically, logically, and creatively...",
            definition_ga: "An cumas smaointeoireacht anailíseach, loighciúil, cruthaitheach a dhéanamh...",
            evidence: {
              source_pdf: "key-competencies-in-senior-cycle_en.pdf",
              source_page: 12,
              excerpt_en: "Critical & Creative Thinking: Students develop the ability to...",
            },
          },
        ],
      };
    }),

  getOnlineLearningPedagogy: os
    .input(z.object({ language: z.enum(["en", "ga"]).default("en") }))
    .handler(async () => {
      return { pedagogy: null };
    }),

  getCertificationGuidance: os
    .input(z.object({ language: z.enum(["en", "ga"]).default("en") }))
    .handler(async () => {
      return { guidance: null };
    }),

  getSCRAdvisory: os
    .input(z.object({
      subject: z.string(),
      language: z.enum(["en", "ga"]).default("en"),
    }))
    .handler(async () => {
      return { commentary: null };
    }),

  getProgrammeStatement: os
    .input(z.object({ language: z.enum(["en", "ga"]).default("en") }))
    .handler(async () => {
      return { statement: null };
    }),
});