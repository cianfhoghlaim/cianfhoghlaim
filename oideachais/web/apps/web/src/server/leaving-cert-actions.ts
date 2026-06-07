/**
 * CopilotKit M3 chat agent for Leaving Certificate per-subject pages.
 *
 * Powered by MiniMax M3 via the LiteLLM gateway (already wired at
 * infrastructure/stacks/engineering/litellm/config/config.yaml § opencode-go/minimax-m3).
 *
 * The agent has 6 tools that map to the per-subject data hosted in
 * MotherDuck (production) or seeded data (dev/fallback).
 *
 * This file is loaded by the CopilotKit runtime in the __root.tsx layout
 * and scoped to the leaving-cert/{subject} routes via the CopilotKit
 * action parameter `subject`.
 */

import type { Action } from "@copilotkit/runtime";

// ── Types (mirrors server/leaving-cert.ts) ────────────────────────────────

type Subject = "mathematics" | "irish" | "biology" | "french" | "history" | "business" | "construction-studies";

// ── Tools (CopilotKit actions) ────────────────────────────────────────────

/**
 * Returns the syllabus topics for a given subject.
 */
export const getSyllabusTopics: Action<{ subject: Subject }> = {
  name: "getSyllabusTopics",
  description: "Get the Leaving Certificate syllabus topics, learning outcomes, and weighting for a subject.",
  parameters: [
    { name: "subject", type: "string", description: "Subject slug (mathematics, irish, biology, french, history, business, construction-studies)", required: true },
  ],
  handler: async ({ subject }) => {
    // In production, this queries the MotherDuck leaving_cert.{subject}_syllabus_extracted table.
    // In dev, it returns the seeded data from server/leaving-cert.ts.
    const endpoint = `/api/leaving-cert/${subject}/syllabus`;
    const res = await fetch(endpoint);
    if (!res.ok) throw new Error(`Failed to fetch syllabus for ${subject}`);
    return res.json();
  },
};

/**
 * Returns the past exam question frequency table for a given subject.
 */
export const getPastExamTable: Action<{ subject: Subject; year?: number }> = {
  name: "getPastExamTable",
  description: "Get the past exam question frequency and topic breakdown for a Leaving Cert subject, optionally filtered by year.",
  parameters: [
    { name: "subject", type: "string", description: "Subject slug", required: true },
    { name: "year", type: "number", description: "Exam year (e.g. 2024). If omitted, returns all years.", required: false },
  ],
  handler: async ({ subject, year }) => {
    const url = `/api/leaving-cert/${subject}/past-exams${year ? `?year=${year}` : ""}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to fetch past exams for ${subject}`);
    return res.json();
  },
};

/**
 * Returns marking scheme patterns (PCLM conventions, common mistakes).
 */
export const getMarkingSchemePatterns: Action<{ subject: Subject }> = {
  name: "getMarkingSchemePatterns",
  description: "Get marking scheme patterns, PCLM conventions, and common mistakes for a Leaving Cert subject.",
  parameters: [
    { name: "subject", type: "string", description: "Subject slug", required: true },
  ],
  handler: async ({ subject }) => {
    const res = await fetch(`/api/leaving-cert/${subject}/marking-schemes`);
    if (!res.ok) throw new Error(`Failed to fetch marking schemes for ${subject}`);
    return res.json();
  },
};

/**
 * Returns the topic prioritisation (ranked by marks-per-study-hour).
 */
export const getTopicPrioritisation: Action<{ subject: Subject }> = {
  name: "getTopicPrioritisation",
  description: "Get the topic prioritisation for a Leaving Cert subject, ranked by expected marks per hour of study. Use this to recommend what to study first.",
  parameters: [
    { name: "subject", type: "string", description: "Subject slug", required: true },
  ],
  handler: async ({ subject }) => {
    const res = await fetch(`/api/leaving-cert/${subject}/prioritisation`);
    if (!res.ok) throw new Error(`Failed to fetch prioritisation for ${subject}`);
    return res.json();
  },
};

/**
 * Returns exam layout tips (time management, common traps, marker expectations).
 */
export const getExamLayoutTips: Action<{ subject: Subject }> = {
  name: "getExamLayoutTips",
  description: "Get exam layout tips for a Leaving Cert subject: paper structure, time per question, common traps, and marker expectations.",
  parameters: [
    { name: "subject", type: "string", description: "Subject slug", required: true },
  ],
  handler: async ({ subject }) => {
    const res = await fetch(`/api/leaving-cert/${subject}/exam-tips`);
    if (!res.ok) throw new Error(`Failed to fetch exam tips for ${subject}`);
    return res.json();
  },
};

/**
 * Returns a signed R2 URL for an original exam paper, marking scheme, or syllabus PDF.
 */
export const openPdf: Action<{ subject: Subject; type: "syllabus" | "exam-paper" | "marking-scheme"; year: number; paper?: string }> = {
  name: "openPdf",
  description: "Get a link to the original PDF (exam paper, marking scheme, or syllabus) for a Leaving Cert subject and year. The PDF is hosted in Cloudflare R2.",
  parameters: [
    { name: "subject", type: "string", description: "Subject slug", required: true },
    { name: "type", type: "string", description: "PDF type: syllabus, exam-paper, or marking-scheme", required: true },
    { name: "year", type: "number", description: "Exam year (e.g. 2024)", required: true },
    { name: "paper", type: "string", description: "Paper number (e.g. paper-1, paper-2). Only needed for exam-paper and marking-scheme types.", required: false },
  ],
  handler: async ({ subject, type, year, paper }) => {
    const res = await fetch(`/api/leaving-cert/${subject}/pdf-link?type=${type}&year=${year}${paper ? `&paper=${paper}` : ""}`);
    if (!res.ok) throw new Error(`Failed to generate PDF link for ${subject}`);
    const { url } = await res.json();
    return { url };
  },
};

/**
 * All 6 leaving-cert CopilotKit actions, ready to be registered
 * in the CopilotKit runtime or the __root.tsx CopilotKit wrapper.
 */
export const LEAVING_CERT_ACTIONS: Action<any>[] = [
  getSyllabusTopics,
  getPastExamTable,
  getMarkingSchemePatterns,
  getTopicPrioritisation,
  getExamLayoutTips,
  openPdf,
];
