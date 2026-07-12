// BAML schema: Gaeilge (Gaeilge) web backend
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject BAML backend that backs the 5 per-subject TanStack
// routes at apps/.../routes/en/subjects/gaeilge/. Exposes 3 web-facing
// functions consumed by the per-subject Convex actions:
//
//   - WebStudyPlan              -> convex/gaeilge/generateStudyPlan.ts
//   - WebExamPaperDiscussion    -> convex/gaeilge/discussExamPaper.ts
//   - WebMarkingSchemeExplanation -> direct read from
//                                   apps/.../routes/en/subjects/gaeilge/marking-schemes
//
// The foundation (qpack + syllabus extraction) lives in
// baml/education/subjects/qpack_gaeilge.baml. This file layers the
// web-facing study-plan + discussion functions on top of that foundation.
//
// Usage:
//   from cianfhoghlaim.baml_client import b
//   plan = b.WebStudyPlan(subject="gaeilge", weeks_until_exam=12,
//                        target_level="LC_HL", language="en")
//   discussion = b.WebExamPaperDiscussion(subject="gaeilge", paper_year=2024,
//                                        paper_level="LC_HL", paper_language="en",
//                                        question_text="...")
//
// Re-gen after changes:  cd cianfhoghlaim && uv run baml-cli generate

// ============================================================================
// Enums
// ============================================================================

enum GaeilgeLevel {
  LC_OL @description("LC_OL Gaeilge level")
  LC_HL @description("LC_HL Gaeilge level")
}

enum GaeilgeLanguage {
  EN @description("English-language Gaeilge")
  GA @description("Gaeilge (Gaeilge) Gaeilge")
}

// ============================================================================
// Output classes
// ============================================================================

class GaeilgeWebStudyPlanResponse {
  title string @description("Title of the Gaeilge study plan (bilingual EN+GA)")
  title_ga string @description("Gaeilge title")
  weeks int @description("Number of weeks in the plan")
  total_study_hours int @description("Total expected study hours")
  weeks_plan GaeilgeStudyWeek[]
  milestones GaeilgeStudyMilestone[]
  recommended_past_papers int[] @description("Past paper years to prioritise, oldest first")
  trace_id string? @description("Langfuse trace id (populated by the @trace decorator)")
}

class GaeilgeStudyWeek {
  week_number int
  theme string @description("Week theme in English")
  theme_ga string @description("Week theme in Gaeilge")
  syllabus_topics string[] @description("NCCA syllabus topics covered this week")
  study_hours int
  past_paper_questions string[] @description("Past paper question ids to attempt this week")
  marking_scheme_focus string[] @description("PCLM patterns to drill this week")
  kc_weights GaeilgeKCWeight[]
}

class GaeilgeKCWeight {
  slug string @description("Key competency slug (one of: communicating, information-processing, critical-creative-thinking, personal-effectiveness, working-with-others)")
  weight int @description("Weight 0-100")
}

class GaeilgeStudyMilestone {
  week int
  description string @description("Milestone description in English")
  description_ga string @description("Milestone description in Gaeilge")
  assessment_type string @description("Type of assessment: past_paper_full, past_paper_section, mock_orals, lab_practical, essay, ...")
}

class GaeilgeWebExamPaperDiscussionResponse {
  question_summary string @description("Restatement of the question")
  question_summary_ga string? @description("Gaeilge summary")
  marking_scheme string @description("The PCLM marking scheme for this question")
  marking_scheme_ga string? @description("Gaeilge marking scheme")
  model_answer_outline string[] @description("Step-by-step model answer outline")
  model_answer_outline_ga string[] @description("Gaeilge outline")
  common_mistakes string[] @description("Common student mistakes for this question")
  marks_breakdown GaeilgeMarksBreakdown[]
  follow_up_questions string[] @description("Suggested follow-up questions the tutor might ask")
  trace_id string?
}

class GaeilgeMarksBreakdown {
  part_label string @description("e.g. (a), (b)(i), (c)")
  part_text string @description("What this part asks for")
  marks int
  marking_notes string @description("How marks are awarded for this part")
}

class GaeilgeWebMarkingSchemeExplanationResponse {
  paper_year int
  paper_level GaeilgeLevel
  paper_language GaeilgeLanguage
  total_marks int
  sections GaeilgeMarkingSection[]
  pclm_patterns string[] @description("PCLM patterns used throughout the paper")
  trace_id string?
}

class GaeilgeMarkingSection {
  section_label string @description("e.g. Section A, Section B")
  total_marks int
  questions GaeilgeMarkingQuestion[]
}

class GaeilgeMarkingQuestion {
  question_label string @description("e.g. Q1, Q2(a)(i)")
  marks int
  pclm string @description("PCLM rationale for this question")
}

// ============================================================================
// Functions
// ============================================================================

function WebStudyPlan(
  subject: string,
  weeks_until_exam: int,
  target_level: GaeilgeLevel,
  language: GaeilgeLanguage,
  focus_topics: string[]
) -> GaeilgeWebStudyPlanResponse {
  // Build a per-subject study plan over `weeks_until_exam` weeks for the
  // chosen target_level (LC HL/OL/FL or JC). The function delegates to the
  // per-subject qpack + syllabus extraction in qpack_gaeilge.baml to ground the
  // plan in real NCCA learning outcomes and SEC past-paper questions.
  //
  // The Convex action convex/gaeilge/generateStudyPlan.ts invokes this
  // function and persists the response to study_plans.
  prompt #"
    You are the Gaeilge study planner for the Cianfhoghlaim BIEP v1
    per-subject interactive web surface.

    Subject slug: { subject }
    Target level: { target_level }
    Language: { language }
    Weeks until exam: { weeks_until_exam }
    Optional focus topics: { focus_topics }

    Build a { weeks_until_exam }-week { target_level } Gaeilge study
    plan grounded in the NCCA Gaeilge syllabus + SEC past-paper corpus.
    Each week must reference concrete syllabus topics + past-paper
    question ids + PCLM marking-scheme patterns. Include 3-5 milestones
    (one per assessment block).

    Return strictly as GaeilgeWebStudyPlanResponse with
    bilingual EN+GA fields where applicable.
  "#
}

function WebExamPaperDiscussion(
  subject: string,
  paper_year: int,
  paper_level: GaeilgeLevel,
  paper_language: GaeilgeLanguage,
  question_text: string
) -> GaeilgeWebExamPaperDiscussionResponse {
  // Walk a student through a single Gaeilge past-paper question.
  // Returns the PCLM marking scheme + a model answer outline + common
  // mistakes + marks breakdown + follow-up questions.
  //
  // Invoked by the Convex action convex/gaeilge/discussExamPaper.ts.
  prompt #"
    You are the Gaeilge exam-paper discussion tutor for the Cianfhoghlaim
    BIEP v1 per-subject interactive web surface.

    Subject slug: { subject }
    Paper year: { paper_year }
    Paper level: { paper_level }
    Paper language: { paper_language }
    Question: { question_text }

    Explain the PCLM marking scheme for this question, then walk through a
    step-by-step model answer outline (in English + Gaeilge where
    applicable), highlight common student mistakes, and propose 3
    follow-up questions the tutor might ask.

    Return strictly as GaeilgeWebExamPaperDiscussionResponse.
  "#
}

function WebMarkingSchemeExplanation(
  subject: string,
  paper_year: int,
  paper_level: GaeilgeLevel,
  paper_language: GaeilgeLanguage
) -> GaeilgeWebMarkingSchemeExplanationResponse {
  // Explain the full marking scheme (PCLM patterns) for an entire
  // Gaeilge past paper at the chosen level + language.
  //
  // Invoked directly from apps/.../routes/en/subjects/gaeilge/marking-schemes.
  prompt #"
    You are the Gaeilge marking-scheme explainer for the Cianfhoghlaim
    BIEP v1 per-subject interactive web surface.

    Subject slug: { subject }
    Paper year: { paper_year }
    Paper level: { paper_level }
    Paper language: { paper_language }

    Walk through every section + question in the marking scheme. Highlight
    the PCLM patterns used (e.g. partial credit for setup, marks for
    logical marking, dependent steps).

    Return strictly as GaeilgeWebMarkingSchemeExplanationResponse.
  "#
}
