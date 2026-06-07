/**
 * Leaving Certificate resource pipeline — server-side data aggregation.
 *
 * This module provides the data layer for the per-subject portal pages at
 * `oideachais.cianfhoghlaim.ie/leaving-cert/{subject}/`.
 *
 * Data sources (in priority order):
 *   1. MotherDuck (public-read aggregates, authenticated Dives) — fastest
 *   2. DuckDB local (dev fallback, reads .duckdb files from R2) — dev
 *   3. Cloudflare R2 signed URLs (original PDFs: syllabi, exam papers,
 *      marking schemes) — via `getSignedUrl()`
 *
 * Each function returns a typed payload that the TanStack Start loader
 * can pass to the per-subject page component.
 */

// ── Types ────────────────────────────────────────────────────────────────

export interface SyllabusTopic {
  topicId: string;
  name: string;
  description: string;
  learningOutcomes: string[];
  weightPct: number; // percentage of the total exam marks this topic represents
}

export interface PastExamQuestion {
  questionId: string;
  year: number;
  paper: string; // "paper-1" | "paper-2" | "paper-1-f" | "paper-2-f"
  level: "H" | "O" | "F";
  questionNumber: number;
  topic: string;
  marks: number;
  questionText: string;
  markingNotes: string;
}

export interface MarkingSchemePattern {
  patternId: string;
  topic: string;
  description: string;
  commonMistakes: string[];
  fullMarkExample: string;
  frequencyPct: number;
}

export interface TopicPrioritisation {
  topic: string;
  expectedMarks: number;
  studyHours: number;
  marksPerHour: number;
  difficulty: "low" | "medium" | "high";
  recommendation: string;
}

export interface ExamLayoutTip {
  tipId: string;
  paper: string;
  section: string;
  tip: string;
  category: "time-management" | "common-trap" | "marker-expectation" | "structure";
}

export interface LeavingCertSubjectPayload {
  subject: string;
  examDate: string;
  papers: Array<{ label: string; startTime: string; endTime: string; level: string }>;
  syllabusSummary: string;
  syllabusTopics: SyllabusTopic[];
  pastExamQuestions: PastExamQuestion[];
  markingSchemePatterns: MarkingSchemePattern[];
  topicPrioritisations: TopicPrioritisation[];
  examLayoutTips: ExamLayoutTip[];
  aggregateTable: string; // MotherDuck table name (e.g. "mathematics_topic_frequency")
}

export type Subject =
  | "mathematics"
  | "irish"
  | "biology"
  | "french"
  | "history"
  | "business"
  | "construction-studies";

// ── Exam schedule (from the SEC 2026 timetable) ──────────────────────────

const SCHEDULE: Record<Subject, { date: string; papers: LeavingCertSubjectPayload["papers"] }> = {
  mathematics: {
    date: "2026-06-05, 2026-06-08",
    papers: [
      { label: "Paper 1 (H&O)", startTime: "14:00", endTime: "16:30", level: "H&O" },
      { label: "Paper 1 (F)", startTime: "14:00", endTime: "16:30", level: "F" },
      { label: "Paper 2 (H&O)", startTime: "09:30", endTime: "12:00", level: "H&O" },
    ],
  },
  irish: {
    date: "2026-06-08, 2026-06-09",
    papers: [
      { label: "Paper 1 H (incl aural)", startTime: "14:00", endTime: "16:20", level: "H" },
      { label: "Paper 1 O (incl aural)", startTime: "14:00", endTime: "15:50", level: "O" },
      { label: "Paper 1 F (incl aural)", startTime: "14:00", endTime: "16:20", level: "F" },
      { label: "Paper 2 H", startTime: "09:30", endTime: "12:35", level: "H" },
      { label: "Paper 2 O", startTime: "09:30", endTime: "11:50", level: "O" },
    ],
  },
  biology: {
    date: "2026-06-09",
    papers: [{ label: "Biology H&O", startTime: "14:00", endTime: "17:00", level: "H&O" }],
  },
  french: {
    date: "2026-06-10",
    papers: [
      { label: "Written H&O", startTime: "09:30", endTime: "12:00", level: "H&O" },
      { label: "Aural", startTime: "12:10", endTime: "12:50", level: "H&O" },
    ],
  },
  history: {
    date: "2026-06-10",
    papers: [{ label: "History H&O", startTime: "14:00", endTime: "16:50", level: "H&O" }],
  },
  business: {
    date: "2026-06-11",
    papers: [
      { label: "Business H", startTime: "09:30", endTime: "12:30", level: "H" },
      { label: "Business O", startTime: "09:30", endTime: "12:00", level: "O" },
    ],
  },
  "construction-studies": {
    date: "2026-06-11",
    papers: [
      { label: "Construction Studies H", startTime: "14:00", endTime: "17:00", level: "H" },
      { label: "Construction Studies O", startTime: "14:00", endTime: "16:30", level: "O" },
    ],
  },
};

const SUBJECT_NAMES: Record<Subject, string> = {
  mathematics: "Mathematics",
  irish: "Gaeilge (Irish)",
  biology: "Biology",
  french: "French",
  history: "History",
  business: "Business",
  "construction-studies": "Construction Studies",
};

// ── MotherDuck table names ────────────────────────────────────────────────

function tableName(subject: Subject, suffix: string): string {
  return `leaving_cert.${subject}_${suffix}`;
}

// ── R2 signed URL helper ──────────────────────────────────────────────────

/**
 * Returns a signed Cloudflare R2 URL for the given resource.
 * The R2 bucket is `cianfhoghlaim-leaving-cert`.
 *
 * In production, this calls the Cloudflare Workers API for signing.
 * In development, returns a local file:// or fallback URL.
 */
export function getR2SignedUrl(bucket: string, key: string, expirySeconds = 3600): string {
  // In production, use a Cloudflare Worker to generate signed URLs.
  // For now, returns a presigned-style URL pattern that the worker
  // will substitute.
  return `https://r2.cianfhoghlaim.ie/${bucket}/${key}?expires=${expirySeconds}`;
}

export function getPdfUrl(subject: Subject, type: "syllabus" | "exam-paper" | "marking-scheme", year: number, paper?: string): string {
  const bucket = "cianfhoghlaim-leaving-cert";
  const keyParts: string[] = [type];
  if (type === "syllabus") {
    keyParts.push(`${year}-syllabus.pdf`);
  } else if (type === "exam-paper") {
    keyParts.push(`${year}-${paper ?? "paper-1"}.pdf`);
  } else {
    keyParts.push(`${year}-${paper ?? "paper-1"}-marking.pdf`);
  }
  return getR2SignedUrl(bucket, `${subject}/${keyParts.join("/")}`);
}

// ── DuckDB/MotherDuck query wrapper (server-side) ────────────────────────

/**
 * Queries the DuckDB/MotherDuck instance for the given subject's data.
 *
 * In production (MOTHERDUCK_ENABLED=true), queries MotherDuck cloud.
 * In dev (local), queries a local DuckDB file.
 *
 * This is a server-side function — it runs in a TanStack Start server
 * function or a Cloudflare Worker, not in the browser.
 */
export async function getSubjectPayload(subject: Subject): Promise<LeavingCertSubjectPayload> {
  const schedule = SCHEDULE[subject];
  const name = SUBJECT_NAMES[subject];

  // In production, each of these would be queried from MotherDuck/DuckDB
  // via a server function. For now, return a typed payload with placeholders
  // that the pipeline will populate.

  return {
    subject: name,
    examDate: schedule.date,
    papers: schedule.papers,
    syllabusSummary: `Syllabus analysis for ${name} — loading…`,
    syllabusTopics: [],
    pastExamQuestions: [],
    markingSchemePatterns: [],
    topicPrioritisations: [],
    examLayoutTips: [],
    aggregateTable: tableName(subject, "topic_frequency"),
  };
}

/**
 * Returns the 7 priority subjects in build order (hardest first).
 */
export function getPrioritySubjects(): Subject[] {
  return [
    "mathematics",
    "irish",
    "biology",
    "french",
    "history",
    "business",
    "construction-studies",
  ];
}

export function getSubjectName(subject: Subject): string {
  return SUBJECT_NAMES[subject];
}

export function getSubjectSchedule(subject: Subject): LeavingCertSubjectPayload["papers"] {
  return SCHEDULE[subject].papers;
}

export function getExamDate(subject: Subject): string {
  return SCHEDULE[subject].date;
}
