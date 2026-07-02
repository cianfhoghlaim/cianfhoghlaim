// @cianfhoghlaim/api — leaving-cert oRPC router
// Per openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md T4.2.
// The 6 leaving-cert oRPC procedures: list + getSyllabus + getPastExams +
// getMarkingSchemes + getPrioritisation + getExamTips.

import { os, z } from "@orpc/server";
import type { ApiContext } from "../context";

// ── Zod schemas ──────────────────────────────────────────────────────

const SubjectSchema = z.enum([
  "mathematics",
  "applied_mathematics",
  "chemistry",
  "geography",
  "history",
  "english",
  "gaeilge",
  "computer_science",
  "biology",
  "french",
  "business",
  "construction-studies",
]);

const LevelSchema = z.enum(["hl", "ol", "fl", "jc"]);
const LanguageSchema = z.enum(["en", "ga"]);

const SyllabusTopicSchema = z.object({
  topicId: z.string(),
  name: z.string(),
  description: z.string(),
  learningOutcomes: z.array(z.string()),
  weightPct: z.number(),
  language: LanguageSchema,
});

const PastExamQuestionSchema = z.object({
  questionId: z.string(),
  year: z.number(),
  paper: z.string(),
  level: z.union([z.literal("H"), z.literal("O"), z.literal("F")]),
  questionNumber: z.number(),
  topic: z.string(),
  marks: z.number(),
  questionText: z.string(),
  markingNotes: z.string(),
});

const MarkingSchemePatternSchema = z.object({
  patternId: z.string(),
  topic: z.string(),
  description: z.string(),
  commonMistakes: z.array(z.string()),
  fullMarkExample: z.string(),
  frequencyPct: z.number(),
});

// ── Router ───────────────────────────────────────────────────────────

export const leavingCertRouter = os.$context<ApiContext>().router({
  list: os
    .input(z.object({
      subject: SubjectSchema.optional(),
      language: LanguageSchema.default("en"),
    }))
    .handler(async ({ input }) => {
      // TODO: query MotherDuck `oideachais.education.<subject>` for the
      // per-subject page list. For now, return the 8 NCCA subjects + the
      // 7 LC exam-window compat subjects.
      const subjects = input.subject ? [input.subject] : [
        "mathematics", "applied_mathematics", "chemistry", "geography",
        "history", "english", "gaeilge", "computer_science",
        "biology", "french", "business", "construction-studies",
      ];
      return subjects.map((s) => ({
        subject: s,
        language: input.language,
        url: `/en/leaving-cert/${s}`,
      }));
    }),

  getSyllabus: os
    .input(z.object({
      subject: SubjectSchema,
      level: LevelSchema.default("hl"),
      language: LanguageSchema.default("en"),
    }))
    .handler(async ({ input }) => {
      // TODO: query MotherDuck + BAML `qpack_<subject>.baml`
      return {
        subject: input.subject,
        level: input.level,
        language: input.language,
        topics: [
          {
            topicId: `${input.subject}-topic-1`,
            name: "Topic 1 (placeholder)",
            description: "First topic of the syllabus (placeholder)",
            learningOutcomes: [
              `${input.subject.toUpperCase()}-LO-1.1`,
              `${input.subject.toUpperCase()}-LO-1.2`,
            ],
            weightPct: 25,
            language: input.language,
          },
        ],
      };
    }),

  getPastExams: os
    .input(z.object({
      subject: SubjectSchema,
      level: LevelSchema.default("hl"),
      yearFrom: z.number().int().min(2017).max(2025).default(2017),
      yearTo: z.number().int().min(2017).max(2025).default(2025),
      language: LanguageSchema.default("en"),
    }))
    .handler(async ({ input }) => {
      // TODO: query MotherDuck
      return {
        subject: input.subject,
        level: input.level,
        yearFrom: input.yearFrom,
        yearTo: input.yearTo,
        language: input.language,
        questions: [],
      };
    }),

  getMarkingSchemes: os
    .input(z.object({
      subject: SubjectSchema,
      level: LevelSchema.default("hl"),
      yearFrom: z.number().int().min(2017).max(2025).default(2017),
      yearTo: z.number().int().min(2017).max(2025).default(2025),
      language: LanguageSchema.default("en"),
    }))
    .handler(async ({ input }) => {
      return {
        subject: input.subject,
        level: input.level,
        language: input.language,
        patterns: [],
      };
    }),

  getPrioritisation: os
    .input(z.object({
      subject: SubjectSchema,
      level: LevelSchema.default("hl"),
      language: LanguageSchema.default("en"),
    }))
    .handler(async ({ input }) => {
      // The BAML `qpack_<subject>.baml` `GetMathPrioritisation` (or equivalent)
      // returns the topic prioritisation ranked by marks ÷ study-hours
      return {
        subject: input.subject,
        level: input.level,
        language: input.language,
        topics: [],
      };
    }),

  getExamTips: os
    .input(z.object({
      subject: SubjectSchema,
      level: LevelSchema.default("hl"),
      language: LanguageSchema.default("en"),
    }))
    .handler(async ({ input }) => {
      return {
        subject: input.subject,
        level: input.level,
        language: input.language,
        tips: [
          {
            tipId: `${input.subject}-tip-1`,
            paper: "paper-1",
            section: "section-a",
            tip: "Read the question carefully before answering (placeholder).",
            category: "time-management",
          },
        ],
      };
    }),
});