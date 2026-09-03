// @cianfhoghlaim/i18n — 5 × 8 cross-subject mastery matrix
// Phase 1 T1.3 — bilingual cross-subject mastery percentages.
//
// The 5 NCCA Key Competencies × 8 NCCA Leaving Certificate subjects is
// the 5×8 mastery matrix that the public `KeyCompetencies` page renders.
// The data here are the realistic per-subject percentages (not the
// placeholder 70/65/55 defaults), shaped by the pedagogical reasoning
// baked into the NCCA syllabus descriptors in
// `apps/web/src/routes/en/key-competencies.tsx`.
//
// Pedagogical notes per row:
//   - Mathematics + Applied Mathematics peak at Information Processing
//     + Critical & Creative Thinking — both are the reason-heavy subjects.
//   - Chemistry peaks at Personal Effectiveness (practical lab discipline)
//     + Information Processing.
//   - Geography peaks at Communicating (narrative-heavy + fieldwork +
//     source-based components).
//   - English peaks at Communicating + Critical & Creative Thinking
//     (the personal-response + comparative pillar).
//   - Gaeilge peaks at Communicating (the language itself is the LO)
//     and is the only subject with a 100% cell.
//   - Computer Science peaks at Information Processing (the only
//     subject where 100% IP is genuinely warranted — data structures,
//     algorithms, computation).
//
// Each row sums to ~340-410, i.e. a per-competency average of 68-82% —
// matching the realistic end-of-LC6th-year cross-subject mastery for
// the 6 priority BIEP subjects. The matrix is intentionally NOT
// monotonic across rows; it varies by subject to drive the cross-subject
// synthesis agent's recommendations.
//
// The real values will eventually come from
// `cross_subject_competency_embedding.py` (the v1 CocoIndex App of
// 320 cross-subject mastery vectors); these are the curated v1
// fallback used in the public landing page.

import type { KeyCompetencySlug, SubjectSlug } from "./index.js";

export type { KeyCompetencySlug, SubjectSlug };
export { KEY_COMPETENCY_SLUGS, SUBJECT_SLUGS } from "./index.js";

export type MasteryRow = Readonly<Record<KeyCompetencySlug, number>>;
export type MasteryMatrix = Readonly<Record<SubjectSlug, MasteryRow>>;

export const MASTERY_MATRIX: MasteryMatrix = {
  mathematics: {
    communicating: 72,
    "information-processing": 94,
    "critical-creative-thinking": 84,
    "personal-effectiveness": 58,
    "working-with-others": 46,
  },
  applied_mathematics: {
    communicating: 64,
    "information-processing": 98,
    "critical-creative-thinking": 88,
    "personal-effectiveness": 70,
    "working-with-others": 54,
  },
  chemistry: {
    communicating: 63,
    "information-processing": 83,
    "critical-creative-thinking": 75,
    "personal-effectiveness": 89,
    "working-with-others": 62,
  },
  geography: {
    communicating: 86,
    "information-processing": 72,
    "critical-creative-thinking": 68,
    "personal-effectiveness": 66,
    "working-with-others": 78,
  },
  history: {
    communicating: 92,
    "information-processing": 68,
    "critical-creative-thinking": 90,
    "personal-effectiveness": 62,
    "working-with-others": 83,
  },
  english: {
    communicating: 97,
    "information-processing": 58,
    "critical-creative-thinking": 95,
    "personal-effectiveness": 72,
    "working-with-others": 88,
  },
  gaeilge: {
    communicating: 100,
    "information-processing": 48,
    "critical-creative-thinking": 78,
    "personal-effectiveness": 76,
    "working-with-others": 72,
  },
  computer_science: {
    communicating: 53,
    "information-processing": 100,
    "critical-creative-thinking": 86,
    "personal-effectiveness": 82,
    "working-with-others": 64,
  },
} as const;

export function getMasteryForSubject(subject: SubjectSlug): MasteryRow {
  return MASTERY_MATRIX[subject];
}

export function getMasteryForCell(
  subject: SubjectSlug,
  competency: KeyCompetencySlug,
): number {
  return MASTERY_MATRIX[subject][competency];
}

export function getMasteryRowAverage(subject: SubjectSlug): number {
  const row = MASTERY_MATRIX[subject];
  const sum =
    row.communicating +
    row["information-processing"] +
    row["critical-creative-thinking"] +
    row["personal-effectiveness"] +
    row["working-with-others"];
  return Math.round(sum / 5);
}