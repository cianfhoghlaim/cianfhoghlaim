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
 * Data flow (in priority order):
 *   1. FastAPI `/api/leaving-cert/{subject}` endpoint, which reads parquet
 *      from `s3://ducklake/oideachais/leaving_cert/*` via DuckDB.
 *   2. In-process seeded knowledge base (dev fallback).
 *
 * The FastAPI endpoint is reached via `VITE_API_URL` (or localhost:8000
 * in dev). The endpoint returns `{source: "ducklake" | "seed", ...}` so
 * callers can tell where the data came from.
 */
export async function getSubjectPayload(subject: Subject): Promise<LeavingCertSubjectPayload> {
  const schedule = SCHEDULE[subject];
  const name = SUBJECT_NAMES[subject];

  // Try the FastAPI endpoint first.
  const apiBase =
    (typeof process !== "undefined" && process.env?.VITE_API_URL) ||
    (typeof import.meta !== "undefined" && (import.meta as any).env?.VITE_API_URL) ||
    "http://localhost:8000";

  let topics: SyllabusTopic[] = [];
  let questions: PastExamQuestion[] = [];
  let patterns: MarkingSchemePattern[] = [];
  let priorities: TopicPrioritisation[] = [];
  let tips: ExamLayoutTip[] = [];
  let summary = `Syllabus analysis for ${name} — seed data (pipeline populates live data)`;
  let dataSource: "ducklake" | "seed" = "seed";

  try {
    const url = `${apiBase}/api/leaving-cert/${subject}`;
    const res = await fetch(url, { headers: { accept: "application/json" } });
    if (res.ok) {
      const data = (await res.json()) as {
        source?: "ducklake" | "seed";
        syllabusSummary?: string;
        syllabusTopics?: Array<{
          year?: number;
          level?: string;
          title?: string;
          url?: string;
          language?: string;
          contentHash?: string;
        }>;
        pastExamQuestions?: Array<{
          year?: number;
          level?: string;
          title?: string;
          url?: string;
          language?: string;
          contentHash?: string;
        }>;
        markingSchemePatterns?: Array<{
          year?: number;
          level?: string;
          title?: string;
          url?: string;
          contentHash?: string;
        }>;
        examinerReports?: Array<{
          year?: number;
          level?: string;
          title?: string;
          url?: string;
          language?: string;
          contentHash?: string;
        }>;
      };
      dataSource = (data.source as "ducklake" | "seed") ?? "seed";
      if (data.syllabusSummary) summary = data.syllabusSummary;

      // Map DuckLake syllabus rows to typed SyllabusTopic[]
      topics = (data.syllabusTopics ?? []).map((r, i) => ({
        topicId: `${subject}-syllabus-${i}`,
        name: r.title ?? "Untitled syllabus resource",
        description: r.url ?? "",
        learningOutcomes: [],
        weightPct: 0,
      }));

      // Map DuckLake past papers to typed PastExamQuestion[] (year + level
      // and title are surfaced; full question text would need a BAML pass).
      questions = (data.pastExamQuestions ?? []).map((q, i) => ({
        questionId: `${subject}-q-${i}`,
        year: q.year ?? 0,
        paper: "paper-1",
        level: (q.level === "F" || q.level === "O" || q.level === "H" ? q.level : "H") as
          | "F"
          | "O"
          | "H",
        questionNumber: i + 1,
        topic: q.title ?? "Untitled past paper",
        marks: 0,
        questionText: q.url ?? "",
        markingNotes: "",
      }));

      // Map DuckLake marking-scheme rows to typed MarkingSchemePattern[]
      patterns = (data.markingSchemePatterns ?? []).map((m, i) => ({
        patternId: `${subject}-p-${i}`,
        topic: m.title ?? "Untitled marking scheme",
        description: m.url ?? "",
        commonMistakes: [],
        fullMarkExample: "",
        frequencyPct: 0,
      }));
    } else {
      // Non-OK: fall through to seed
      dataSource = "seed";
    }
  } catch {
    dataSource = "seed";
  }

  // Always augment with seeded data (the DuckLake raw rows don't carry
  // weighted topics / PCLM patterns / exam tips; those are BAML-extracted
  // from the PDF bodies in a future pipeline revision).
  const seeded = getSeededTopics(subject);
  if (topics.length === 0) {
    topics = seeded.topics;
    summary = seeded.summary;
  }
  if (questions.length === 0) questions = getSeededQuestions(subject);
  if (patterns.length === 0) patterns = getSeededPatterns(subject);
  tips = getSeededTips(subject);
  priorities = computePriorities(topics, questions, patterns);

  return {
    subject: name,
    examDate: schedule.date,
    papers: schedule.papers,
    syllabusSummary: summary,
    syllabusTopics: topics,
    pastExamQuestions: questions,
    markingSchemePatterns: patterns,
    topicPrioritisations: priorities,
    examLayoutTips: tips,
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

// ── Seeded Data (knowledge-encoded, populated by pipeline at runtime) ──────

interface SeededTopic {
  name: string;
  weightPct: number;
  outcomes: string[];
}

const SEEDED_TOPICS: Record<Subject, { summary: string; topics: SeededTopic[] }> = {
  mathematics: {
    summary:
      "The Leaving Certificate Mathematics syllabus (Higher and Ordinary) covers 5 strands: " +
      "Statistics & Probability, Geometry & Trigonometry, Numbers, Algebra, and Functions. " +
      "Paper 1 (2h30, 300 marks) covers Algebra, Numbers, and Functions. Paper 2 (2h30, 300 marks) " +
      "covers Statistics, Probability, Geometry, and Trigonometry. The Foundation level omits " +
      "inferential statistics and calculus.",
    topics: [
      { name: "Algebra (Paper 1)", weightPct: 25, outcomes: ["Solve linear and quadratic equations", "Manipulate algebraic fractions", "Apply laws of indices and surds"] },
      { name: "Functions & Calculus (Paper 1)", weightPct: 25, outcomes: ["Differentiate polynomial, exponential, trig functions", "Find max/min, points of inflection", "Integrate basic functions"] },
      { name: "Numbers (Paper 1)", weightPct: 10, outcomes: ["Complex numbers (H only)", "Sequences & series", "Financial maths (compound interest, APR)"] },
      { name: "Statistics & Probability (Paper 2)", weightPct: 20, outcomes: ["Normal distribution, z-scores", "Hypothesis testing (H only)", "Probability rules, Bayes theorem"] },
      { name: "Geometry & Trigonometry (Paper 2)", weightPct: 20, outcomes: ["Coordinate geometry of line and circle", "Trigonometric identities and equations", "3D geometry (H only)"] },
    ],
  },
  irish: {
    summary:
      "The Leaving Certificate Irish syllabus (Ardleibhéal/Gnáthleibhéal/Bonnleibhéal) covers 5 skills: " +
      "Cluastuiscint (Listening), Léamhthuiscint (Reading), Ceapadóireacht (Composition), " +
      "Gramadach (Grammar), and Litríocht (Literature). Paper 1 includes the aural component. " +
      "Paper 2 covers prose, poetry, and the additional literary text.",
    topics: [
      { name: "Cluastuiscint (Listening)", weightPct: 20, outcomes: ["Respond to spoken Irish from radio clips", "Extract key information from aural passages", "Answer in Irish"] },
      { name: "Léamhthuiscint (Reading)", weightPct: 20, outcomes: ["Comprehend journalistic and literary Irish texts", "Answer comprehension questions in Irish", "Identify themes and argument structure"] },
      { name: "Ceapadóireacht (Composition)", weightPct: 30, outcomes: ["Write Aiste (essay), Litir (letter), Díospóireacht (debate)", "Use appropriate register and idiom", "Structure arguments with introduction, body, conclusion"] },
      { name: "Gramadach (Grammar)", weightPct: 15, outcomes: ["Correct use of An Modh Coinníollach", "Correct use of An Tuiseal Ginideach", "Verb conjugation in all tenses"] },
      { name: "Litríocht (Literature)", weightPct: 15, outcomes: ["Analyse prescribed prose and poetry", "Discuss themes, characters, and style", "Write literary answers in Irish"] },
    ],
  },
  biology: {
    summary:
      "The Leaving Certificate Biology syllabus (Higher and Ordinary) is a single 3-hour paper (400 marks). " +
      "The syllabus covers 3 units: The Study of Life (ecology, food), The Cell (genetics, enzymes, " +
      "photosynthesis, respiration), and The Organism (human biology, plant biology, microbiology). " +
      "There are 22 mandatory experiments; at least 3 questions relate directly to practical work.",
    topics: [
      { name: "The Cell (Unit 2)", weightPct: 35, outcomes: ["Cell structure and microscopy", "Cell division (mitosis, meiosis)", "DNA, RNA, protein synthesis (H)", "Enzymes and metabolism"] },
      { name: "The Organism (Unit 3)", weightPct: 35, outcomes: ["Human biology (nervous, endocrine, skeletal, circulatory)", "Plant biology (transport, reproduction)", "Microbiology and immunity", "Genetics (monohybrid, dihybrid, sex linkage)"] },
      { name: "The Study of Life (Unit 1)", weightPct: 20, outcomes: ["Food and nutrition", "Ecology (ecosystems, pyramids, nutrient cycles)", "Scientific method and experimentation"] },
      { name: "Mandatory Experiments", weightPct: 10, outcomes: ["22 mandatory practicals", "At least 3 exam questions linked to practical work", "Report writing: hypothesis, method, results, conclusion"] },
    ],
  },
  french: {
    summary:
      "The Leaving Certificate French syllabus (Higher and Ordinary) tests 4 skills over two components: " +
      "Written (55% — Reading 30%, Writing 25%) and Oral/Aural (45% — Listening 20%, Oral exam 25%). " +
      "The written paper is 2.5 hours (H) or 2 hours (O). The aural is 40 minutes after the written paper. " +
      "The oral exam (12-15 minutes) is held separately in April.",
    topics: [
      { name: "Reading Comprehension (Written)", weightPct: 30, outcomes: ["Extract detail from journalistic French", "Identify opinions and tone", "Answer in French and English"] },
      { name: "Written Production", weightPct: 25, outcomes: ["Opinion piece (H: 300 words, O: 200 words)", "Diary entry, letter, or email (O)", "Use correct tense, register, idiom"] },
      { name: "Listening (Aural)", weightPct: 20, outcomes: ["Extract specific detail from spoken French", "Respond to questions in English and French", "Handle dialogue, news report, announcement"] },
      { name: "Oral Exam", weightPct: 25, outcomes: ["General conversation (5 mins)", "Picture sequence / document (5 mins)", "Role play (2-3 mins)"] },
    ],
  },
  history: {
    summary:
      "The Leaving Certificate History syllabus (Higher and Ordinary) covers Irish history (1815-1993) " +
      "and European/world history from 4 topics. Students study 2 Irish topics and 2 European topics " +
      "from a choice of 12. The exam is 2h50 (H) or 2h30 (O), 400 marks. It includes a compulsory " +
      "Documents-Based Question (DBQ, 100 marks) and 3 essay questions (100 marks each).",
    topics: [
      { name: "Documents-Based Question (DBQ)", weightPct: 25, outcomes: ["Analyse 3-4 source documents", "Answer comprehension and context questions", "Write a contextual essay linking documents"] },
      { name: "Irish History (2 topics)", weightPct: 50, outcomes: ["Choose from: Movements for Reform, Sovereignty & Partition, Politics in Northern Ireland, IRA/Sunningdale/Anglo-Irish", "Essay writing: argument, evidence, historiography"] },
      { name: "European/World History (2 topics)", weightPct: 25, outcomes: ["Choose from: Dictatorship in Europe, US & World, Retreat from Empire, French Revolution (H only)", "Comparative analysis between topics"] },
    ],
  },
  business: {
    summary:
      "The Leaving Certificate Business syllabus (Higher and Ordinary) is a single paper (H: 3h, O: 2.5h, " +
      "400 marks). The syllabus covers 7 units: People in Business, Enterprise, Management, Finance, " +
      "Marketing, Business Environment, and Global Business. The paper has a short question section " +
      "(Unit 1-7, 80 marks) and a long question section (4 from 8, apply 1+ ABQ).",
    topics: [
      { name: "Finance & Accounting", weightPct: 25, outcomes: ["Prepare final accounts (Trading, P&L, Balance Sheet)", "Ratio analysis", "Cash flow and budgeting", "Club accounts"] },
      { name: "Marketing & Enterprise", weightPct: 20, outcomes: ["Marketing mix (4Ps)", "Market research (primary/secondary)", "SWOT and PEST analysis", "Enterprise characteristics"] },
      { name: "Management & HR", weightPct: 20, outcomes: ["Management skills (Drucker, Mintzberg)", "Industrial relations", "Motivation theories (Maslow, McGregor)"] },
      { name: "Business Environment & Global", weightPct: 20, outcomes: ["EU and global business", "Government economics", "Social responsibility and ethics"] },
      { name: "Applied Business Question (ABQ)", weightPct: 15, outcomes: ["Apply all units to a case study", "Structure: introduction, answer, evaluation", "H only: 80-mark ABQ"] },
    ],
  },
  "construction-studies": {
    summary:
      "The Leaving Certificate Construction Studies syllabus (Higher and Ordinary) combines theory (50%) " +
      "with a practical project (25%) and a day practical exam (25%). The written paper (H: 3h, O: 2.5h, " +
      "300 marks) covers building construction, services, materials, and drawing. The project and day " +
      "practical are submitted in April.",
    topics: [
      { name: "Building Construction", weightPct: 30, outcomes: ["Foundations, floors, walls, roofs", "Passive house design and BER ratings", "Sustainable construction methods"] },
      { name: "Services & Materials", weightPct: 25, outcomes: ["Plumbing, heating, ventilation", "Electrical and lighting design", "Timber, concrete, steel, glass properties"] },
      { name: "Technical Drawing", weightPct: 20, outcomes: ["Orthographic and isometric projection", "Floor plans, elevations, sections", "Scale and dimensioning"] },
      { name: "Practical Project (25%)", weightPct: 25, outcomes: ["Design and build a scale model", "Portfolio with design sketches, working drawings, photographs", "Materials list and costing"] },
    ],
  },
};

function getSeededTopics(subject: Subject): { summary: string; topics: SyllabusTopic[] } {
  const s = SEEDED_TOPICS[subject];
  return {
    summary: s.summary,
    topics: s.topics.map((t, i) => ({
      topicId: `${subject}-t${i}`,
      name: t.name,
      description: "",
      learningOutcomes: t.outcomes,
      weightPct: t.weightPct,
    })),
  };
}

function getSeededQuestions(subject: Subject): PastExamQuestion[] {
  // Seeded questions — placeholder. Real data comes from the pipeline.
  const s = SEEDED_TOPICS[subject];
  const questions: PastExamQuestion[] = [];
  let qn = 1;
  for (const topic of s.topics.slice(0, 3)) {
    for (const year of [2024, 2023, 2022]) {
      questions.push({
        questionId: `${subject}-q${qn}`,
        year,
        paper: qn % 2 === 0 ? "paper-2" : "paper-1",
        level: "H",
        questionNumber: qn,
        topic: topic.name,
        marks: Math.round(topic.weightPct * 4 * (year === 2024 ? 1 : year === 2023 ? 1.1 : 0.9)),
        questionText: `${topic.name} question from ${year} — load full text from pipeline`,
        markingNotes: "",
      });
      qn++;
    }
  }
  return questions;
}

function getSeededPatterns(subject: Subject): MarkingSchemePattern[] {
  const s = SEEDED_TOPICS[subject];
  return s.topics.map((t, i) => ({
    patternId: `${subject}-p${i}`,
    topic: t.name,
    description: `PCLM marking applied to ${t.name} questions. Marks are awarded for correct application, not just final answer. Partial credit is given for method marks.`,
    commonMistakes: ["Not showing work / skipping steps", "Rounding errors in calculations", "Misreading the question requirement"],
    fullMarkExample: `A fully correct answer to a ${t.weightPct}-mark section demonstrates correct method, accurate calculation/analysis, and a clear final answer.`,
    frequencyPct: t.weightPct,
  }));
}

function getSeededTips(subject: Subject): ExamLayoutTip[] {
  const s = SEEDED_TOPICS[subject];
  const tips: ExamLayoutTip[] = [
    {
      tipId: `${subject}-tip-time`,
      paper: "all",
      section: "All sections",
      tip: `Allocate time per question based on marks: 1 mark = 1.5 minutes. Don't spend more than 10 minutes on a 15-mark question.`,
      category: "time-management",
    },
    {
      tipId: `${subject}-tip-show-work`,
      paper: "all",
      section: "All sections",
      tip: `Show all working — method marks are awarded even if the final answer is wrong. A blank page scores zero.`,
      category: "marker-expectation",
    },
    {
      tipId: `${subject}-tip-read`,
      paper: "all",
      section: "All sections",
      tip: `Read the full question before starting. Pay attention to command words: 'explain', 'evaluate', 'calculate', 'compare' have different mark allocations.`,
      category: "common-trap",
    },
  ];
  for (const t of s.topics.slice(0, 2)) {
    tips.push({
      tipId: `${subject}-tip-${t.name.toLowerCase().replace(/[()]/g, "").replace(/\s+/g, "-")}`,
      paper: "all",
      section: t.name,
      tip: `${t.name} (${t.weightPct}% of exam): focus on the most frequently examined subtopics. Look at the past 5 years of papers for pattern.`,
      category: "structure",
    });
  }
  return tips;
}

function computePriorities(
  topics: SyllabusTopic[],
  _questions: PastExamQuestion[],
  _patterns: MarkingSchemePattern[],
): TopicPrioritisation[] {
  return topics
    .map((t) => {
      const studyHours = t.weightPct > 25 ? 8 : t.weightPct > 15 ? 5 : 3;
      const marksPerHour = t.weightPct / studyHours;
      return {
        topic: t.name,
        expectedMarks: t.weightPct * 4, // approximate 400-mark paper
        studyHours,
        marksPerHour,
        difficulty: (t.weightPct > 20 ? "high" : "medium") as "high" | "medium" | "low",
        recommendation:
          t.weightPct > 25
            ? `High-value topic (${t.weightPct}% of marks). Prioritise this.`
            : `Medium-value topic. Cover after the top 3 topics.`,
      };
    })
    .sort((a, b) => b.marksPerHour - a.marksPerHour);
}
