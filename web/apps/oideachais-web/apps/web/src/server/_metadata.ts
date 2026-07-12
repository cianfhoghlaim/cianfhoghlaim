/**
 * Single source of truth for the Leaving Certificate agent-callable surface.
 *
 * This metadata drives:
 *   - CopilotKit actions (already wired in __root.tsx via LEAVING_CERT_ACTIONS)
 *   - The Agent Skill that could be auto-generated (tanmaxx-17 Intent pattern)
 *   - The TanStack Router API endpoints (/api/leaving-cert/{subject}/*)
 *
 * If you add a server function intended for agents or public pages, register it here.
 *
 * Pattern from tanmaxx-17 (apps/web/src/server/functions/_metadata.ts):
 *   - One static registry of all callable functions
 *   - Each entry has: name, description, method, url, inputSchema, examples
 *   - Used by both CopilotKit actions AND by an Intent skill generator
 */

import { z } from "zod";

// ── Types ─────────────────────────────────────────────────────────────────

export type ServerFnMeta = {
  name: string;
  description: string;
  method: "GET" | "POST";
  url: string;
  inputSchema: z.ZodTypeAny;
  examples: ReadonlyArray<{ description: string; input: unknown }>;
};

// ── Zod schemas (shared between metadata and CopilotKit actions) ─────────

const subjectSchema = z.enum([
  "mathematics",
  "irish",
  "biology",
  "french",
  "history",
  "business",
  "construction-studies",
]);

const pdfTypeSchema = z.enum(["syllabus", "exam-paper", "marking-scheme"]);

// ── Metadata Registry ────────────────────────────────────────────────────

export const LEAVING_CERT_METADATA = {
  /** Get the syllabus topics, learning outcomes, and weightings for a subject. */
  getSyllabusTopics: {
    name: "getSyllabusTopics",
    description:
      "Get the Leaving Certificate syllabus topics, learning outcomes, and weighting for a subject. Returns NCCA-structured topic list with percentage-of-total-exam weight.",
    method: "GET",
    url: "/api/leaving-cert/:subject/syllabus",
    inputSchema: z.object({ subject: subjectSchema }),
    examples: [
      {
        description: "Mathematics topics",
        input: { subject: "mathematics" },
      },
      {
        description: "Irish topics",
        input: { subject: "irish" },
      },
    ],
  },

  /** Get the past exam question frequency and topic breakdown, optionally filtered by year. */
  getPastExamTable: {
    name: "getPastExamTable",
    description:
      "Get the past exam question frequency and topic breakdown for a Leaving Cert subject, optionally filtered by year. Returns every question from 2017-2025 with marks, topic, and paper.",
    method: "GET",
    url: "/api/leaving-cert/:subject/past-exams",
    inputSchema: z.object({
      subject: subjectSchema,
      year: z.number().int().min(2017).max(2025).optional(),
    }),
    examples: [
      {
        description: "All years for Mathematics",
        input: { subject: "mathematics" },
      },
      {
        description: "Only 2024 Biology questions",
        input: { subject: "biology", year: 2024 },
      },
    ],
  },

  /** Get marking scheme patterns, PCLM conventions, and common mistakes. */
  getMarkingSchemePatterns: {
    name: "getMarkingSchemePatterns",
    description:
      "Get marking scheme patterns, PCLM conventions, and common mistakes for a Leaving Cert subject. Each pattern includes full-mark examples and frequency data.",
    method: "GET",
    url: "/api/leaving-cert/:subject/marking-schemes",
    inputSchema: z.object({ subject: subjectSchema }),
    examples: [
      {
        description: "Mathematics marking patterns",
        input: { subject: "mathematics" },
      },
    ],
  },

  /** Get the topic prioritisation, ranked by expected marks per hour of study. */
  getTopicPrioritisation: {
    name: "getTopicPrioritisation",
    description:
      "Get the topic prioritisation for a Leaving Cert subject, ranked by expected marks per hour of study. Use this to recommend what to study first. Higher marksPerHour = better use of study time.",
    method: "GET",
    url: "/api/leaving-cert/:subject/prioritisation",
    inputSchema: z.object({ subject: subjectSchema }),
    examples: [
      {
        description: "Mathematics prioritisation",
        input: { subject: "mathematics" },
      },
    ],
  },

  /** Get exam layout tips (time management, common traps, marker expectations). */
  getExamLayoutTips: {
    name: "getExamLayoutTips",
    description:
      "Get exam layout tips for a Leaving Cert subject: paper structure, time per question, common traps, and marker expectations.",
    method: "GET",
    url: "/api/leaving-cert/:subject/exam-tips",
    inputSchema: z.object({ subject: subjectSchema }),
    examples: [
      {
        description: "Biology exam tips",
        input: { subject: "biology" },
      },
    ],
  },

  /** Get a signed R2 URL for an original exam paper, marking scheme, or syllabus PDF. */
  openPdf: {
    name: "openPdf",
    description:
      "Get a link to the original PDF (exam paper, marking scheme, or syllabus) for a Leaving Cert subject and year. The PDF is hosted in Cloudflare R2. Returns a signed URL that expires after 1 hour.",
    method: "GET",
    url: "/api/leaving-cert/:subject/pdf-link",
    inputSchema: z.object({
      subject: subjectSchema,
      type: pdfTypeSchema,
      year: z.number().int().min(2017).max(2025),
      paper: z.string().optional(),
    }),
    examples: [
      {
        description: "2024 Mathematics Paper 1",
        input: {
          subject: "mathematics",
          type: "exam-paper",
          year: 2024,
          paper: "paper-1",
        },
      },
      {
        description: "2025 Biology syllabus",
        input: { subject: "biology", type: "syllabus", year: 2025 },
      },
    ],
  },

  /** Get the full Leaving Cert subject payload (all sections). */
  getSubjectPayload: {
    name: "getSubjectPayload",
    description:
      "Get the complete Leaving Certificate resource payload for a subject: syllabus topics, past exam questions, marking scheme patterns, topic prioritisation, exam layout tips, and exam schedule. This is the primary data source for the per-subject portal page.",
    method: "GET",
    url: "/api/leaving-cert/:subject",
    inputSchema: z.object({ subject: subjectSchema }),
    examples: [
      {
        description: "Full Mathematics payload",
        input: { subject: "mathematics" },
      },
    ],
  },
} satisfies Record<string, ServerFnMeta>;

export type LeavingCertFnName = keyof typeof LEAVING_CERT_METADATA;

// ── Helpers ───────────────────────────────────────────────────────────────

/** Returns a flat list of all leaving-cert server function names. */
export function getLeavingCertFnNames(): LeavingCertFnName[] {
  return Object.keys(LEAVING_CERT_METADATA) as LeavingCertFnName[];
}

/** Returns the metadata for a single function. */
export function getLeavingCertFnMeta(name: LeavingCertFnName): ServerFnMeta {
  return LEAVING_CERT_METADATA[name];
}
