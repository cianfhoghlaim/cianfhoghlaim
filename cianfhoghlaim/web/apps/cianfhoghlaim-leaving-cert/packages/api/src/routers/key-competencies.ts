// @cianfhoghlaim/api — key_competencies oRPC router
// The 5 NCCA Key Competencies with the cross-subject reasoning.

import { os, z } from "@orpc/server";
import type { ApiContext } from "../context";

const KeyCompetencySchema = z.enum([
  "information-processing",
  "communicating",
  "working-with-others",
  "personal-effectiveness",
  "critical-creative-thinking",
]);

const SubjectSchema = z.enum([
  "mathematics", "applied_mathematics", "chemistry", "geography",
  "history", "english", "gaeilge", "computer_science",
]);

export const keyCompetenciesRouter = os.$context<ApiContext>().router({
  list: os
    .input(z.object({ language: z.enum(["en", "ga"]).default("en") }))
    .handler(async ({ input }) => {
      // TODO: query Convex `root_key_competencies_extracted` asset
      return {
        language: input.language,
        competencies: [
          {
            code: "KC-IP",
            slug: "information-processing",
            name_en: "Information Processing",
            name_ga: "Próiseáil Faisnéise",
            tuatha_de: "Ogma",
          },
          {
            code: "KC-CO",
            slug: "communicating",
            name_en: "Communicating",
            name_ga: "Cumarsáid",
            tuatha_de: "Brigid",
          },
          {
            code: "KC-WO",
            slug: "working-with-others",
            name_en: "Working with Others",
            name_ga: "Ag Obair le Daoine Eile",
            tuatha_de: "Trí Dé Dána",
          },
          {
            code: "KC-PE",
            slug: "personal-effectiveness",
            name_en: "Personal Effectiveness",
            name_ga: "Éifeachtacht Phearsanta",
            tuatha_de: "Dian Cecht",
          },
          {
            code: "KC-CT",
            slug: "critical-creative-thinking",
            name_en: "Critical & Creative Thinking",
            name_ga: "Smaointeoireacht Chriticiúil agus Chruthaitheach",
            tuatha_de: "Lugh",
          },
        ],
      };
    }),

  explainAcrossSubjects: os
    .input(z.object({
      competency: KeyCompetencySchema,
      subjects: z.array(SubjectSchema).min(1).max(8),
      language: z.enum(["en", "ga"]).default("en"),
    }))
    .handler(async ({ input }) => {
      // TODO: call cianfhoghlaim.agents.tuatha.agents.cross_subject_agent.explain_across_subjects(...)
      return {
        competency: input.competency,
        subjects: input.subjects,
        explanation_en: `How ${input.competency.replace("-", " ")} applies across ${", ".join(input.subjects)} (placeholder)`,
        explanation_ga: null,
        per_subject_examples: input.subjects.map((subject) => ({
          subject,
          lo_codes: [`${subject.toUpperCase()}-LO-1.1`, `${subject.toUpperCase()}-LO-2.1`],
        })),
      };
    }),

  suggestMasteryPath: os
    .input(z.object({
      student_id: z.string(),
      language: z.enum(["en", "ga"]).default("en"),
    }))
    .handler(async ({ input }) => {
      // TODO: query Convex `practice_attempts` for the student's current
      // mastery + call cianfhoghlaim.agents.tuatha.agents.cross_subject_agent.suggest_mastery_path(...)
      return {
        student_id: input.student_id,
        mastery_path: [
          "Information Processing (Ogma) — start with Mathematics + Computer Science",
          "Communicating (Brigid) — then English + Gaeilge",
          "Personal Effectiveness (Dian Cecht) — then Chemistry + Biology",
          "Working with Others (Trí Dé Dána) — then Geography + History",
          "Critical & Creative Thinking (Lugh) — capstone across all 8",
        ],
      };
    }),
});