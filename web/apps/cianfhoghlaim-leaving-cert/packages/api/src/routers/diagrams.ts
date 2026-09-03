// @cianfhoghlaim/api — diagrams oRPC router
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T4.3.
// The 4 diagram endpoints: renderConceptMap + renderTopicHeatmap +
// renderPCLMFlow + renderQuestionSankey.

import { os } from "@orpc/server";
import { z } from "zod";
import type { ApiContext } from "../context";

const SubjectSchema = z.enum([
  "mathematics", "applied_mathematics", "chemistry", "geography",
  "history", "english", "gaeilge", "computer_science",
]);
const LevelSchema = z.enum(["hl", "ol", "fl", "jc"]);
const LanguageSchema = z.enum(["en", "ga"]);
const DiagramModeSchema = z.enum(["concept-map", "topic-heatmap", "pclm-flow", "question-sankey"]);

const DiagramPayloadSchema = z.object({
  mode: DiagramModeSchema,
  subject: SubjectSchema,
  language: LanguageSchema,
  nodes: z.array(z.any()),
  edges: z.array(z.any()),
  caption: z.object({
    text_en: z.string(),
    text_ga: z.string().optional(),
  }),
  source_evidence: z.object({
    text_en: z.string(),
    text_ga: z.string().optional(),
  }),
  rendered_at: z.string(),
});

export const diagramsRouter = os.$context<ApiContext>().router({
  renderConceptMap: os
    .input(z.object({
      subject: SubjectSchema,
      language: LanguageSchema.default("en"),
      level: LevelSchema.default("hl"),
    }))
    .handler(async ({ input }) => {
      // TODO: call BAML `b.RenderConceptMap(subject, language, syllabus_json,
      //       past_papers_json, marking_schemes_json, 5_key_competencies_json)`
      return {
        mode: "concept-map" as const,
        subject: input.subject,
        language: input.language,
        nodes: [],
        edges: [],
        caption: { text_en: `Concept-map for ${input.subject}`, text_ga: null },
        source_evidence: { text_en: "Source: NCCA syllabus + 5 Key Competencies", text_ga: null },
        rendered_at: new Date().toISOString(),
      };
    }),

  renderTopicHeatmap: os
    .input(z.object({
      subject: SubjectSchema,
      language: LanguageSchema.default("en"),
      level: LevelSchema.default("hl"),
      yearFrom: z.number().int().min(2017).max(2025).default(2017),
      yearTo: z.number().int().min(2017).max(2025).default(2025),
    }))
    .handler(async ({ input }) => {
      return {
        mode: "topic-heatmap" as const,
        subject: input.subject,
        language: input.language,
        nodes: [],
        edges: [],
        caption: { text_en: `Topic-heatmap for ${input.subject} (${input.yearFrom}-${input.yearTo})`, text_ga: null },
        source_evidence: { text_en: "Source: Past exam papers 2017-2025", text_ga: null },
        rendered_at: new Date().toISOString(),
      };
    }),

  renderPCLMFlow: os
    .input(z.object({
      subject: SubjectSchema,
      language: LanguageSchema.default("en"),
      level: LevelSchema.default("hl"),
      paper: z.enum(["paper-1", "paper-2", "paper-1-f"]).default("paper-1"),
      year: z.number().int().min(2017).max(2025).default(2024),
    }))
    .handler(async ({ input }) => {
      return {
        mode: "pclm-flow" as const,
        subject: input.subject,
        language: input.language,
        nodes: [],
        edges: [],
        caption: { text_en: `PCLM Flow for ${input.subject} ${input.paper} ${input.year}`, text_ga: null },
        source_evidence: { text_en: "Source: SEC marking scheme", text_ga: null },
        rendered_at: new Date().toISOString(),
      };
    }),

  renderQuestionSankey: os
    .input(z.object({
      subject: SubjectSchema,
      language: LanguageSchema.default("en"),
      level: LevelSchema.default("hl"),
      yearFrom: z.number().int().min(2017).max(2025).default(2017),
      yearTo: z.number().int().min(2017).max(2025).default(2025),
    }))
    .handler(async ({ input }) => {
      return {
        mode: "question-sankey" as const,
        subject: input.subject,
        language: input.language,
        nodes: [],
        edges: [],
        caption: { text_en: `Question → Topic → Difficulty → Year Sankey for ${input.subject}`, text_ga: null },
        source_evidence: { text_en: "Source: Past exam papers 2017-2025", text_ga: null },
        rendered_at: new Date().toISOString(),
      };
    }),
});