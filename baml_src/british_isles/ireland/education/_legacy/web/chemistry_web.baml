// BAML schema: Chemistry (Ceimic) web backend
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject BAML backend that backs the 5 per-subject TanStack
// routes at apps/.../routes/en/subjects/chemistry/. Exposes 3 web-facing
// functions consumed by the per-subject Convex actions:
//
//   - WebStudyPlan              -> convex/chemistry/generateStudyPlan.ts
//   - WebExamPaperDiscussion    -> convex/chemistry/discussExamPaper.ts
//   - WebMarkingSchemeExplanation -> direct read from
//                                   apps/.../routes/en/subjects/chemistry/marking-schemes
//
// The foundation (qpack + syllabus extraction) lives in
// baml/education/subjects/qpack_chemistry.baml. This file layers the
// web-facing study-plan + discussion functions on top of that foundation.
//
// Usage:
//   from cianfhoghlaim.baml_client import b
//   plan = b.WebStudyPlan(subject="chemistry", weeks_until_exam=12,
//                        target_level="LC_HL", language="en")
//   discussion = b.WebExamPaperDiscussion(subject="chemistry", paper_year=2024,
//                                        paper_level="LC_HL", paper_language="en",
//                                        question_text="...")
//
// Re-gen after changes:  cd cianfhoghlaim && uv run baml-cli generate

// ============================================================================
// Enums
// ============================================================================

enum ChemistryLevel {
  LC_OL @description("LC_OL Chemistry level")
  LC_HL @description("LC_HL Chemistry level")
}

enum ChemistryLanguage {
  EN @description("English-language Chemistry")
  GA @description("Gaeilge (Ceimic) Chemistry")
}

// ============================================================================
// Output classes
// ============================================================================

class ChemistryWebStudyPlanResponse {
  title string @description("Title of the Chemistry study plan (bilingual EN+GA)")
  title_ga string @description("Gaeilge title")
  weeks int @description("Number of weeks in the plan")
  total_study_hours int @description("Total expected study hours")
  weeks_plan ChemistryStudyWeek[]
  milestones ChemistryStudyMilestone[]
  recommended_past_papers int[] @description("Past paper years to prioritise, oldest first")
  trace_id string? @description("Langfuse trace id (populated by the @trace decorator)")
}

class ChemistryStudyWeek {
  week_number int
  theme string @description("Week theme in English")
  theme_ga string @description("Week theme in Gaeilge")
  syllabus_topics string[] @description("NCCA syllabus topics covered this week")
  study_hours int
  past_paper_questions string[] @description("Past paper question ids to attempt this week")
  marking_scheme_focus string[] @description("PCLM patterns to drill this week")
  kc_weights ChemistryKCWeight[]
}

class ChemistryKCWeight {
  slug string @description("Key competency slug (one of: communicating, information-processing, critical-creative-thinking, personal-effectiveness, working-with-others)")
  weight int @description("Weight 0-100")
}

class ChemistryStudyMilestone {
  week int
  description string @description("Milestone description in English")
  description_ga string @description("Milestone description in Gaeilge")
  assessment_type string @description("Type of assessment: past_paper_full, past_paper_section, mock_orals, lab_practical, essay, ...")
}

class ChemistryWebExamPaperDiscussionResponse {
  question_summary string @description("Restatement of the question")
  question_summary_ga string? @description("Gaeilge summary")
  marking_scheme string @description("The PCLM marking scheme for this question")
  marking_scheme_ga string? @description("Gaeilge marking scheme")
  model_answer_outline string[] @description("Step-by-step model answer outline")
  model_answer_outline_ga string[] @description("Gaeilge outline")
  common_mistakes string[] @description("Common student mistakes for this question")
  marks_breakdown ChemistryMarksBreakdown[]
  follow_up_questions string[] @description("Suggested follow-up questions the tutor might ask")
  trace_id string?
}

class ChemistryMarksBreakdown {
  part_label string @description("e.g. (a), (b)(i), (c)")
  part_text string @description("What this part asks for")
  marks int
  marking_notes string @description("How marks are awarded for this part")
}

class ChemistryWebMarkingSchemeExplanationResponse {
  paper_year int
  paper_level ChemistryLevel
  paper_language ChemistryLanguage
  total_marks int
  sections ChemistryMarkingSection[]
  pclm_patterns string[] @description("PCLM patterns used throughout the paper")
  trace_id string?
}

class ChemistryMarkingSection {
  section_label string @description("e.g. Section A, Section B")
  total_marks int
  questions ChemistryMarkingQuestion[]
}

class ChemistryMarkingQuestion {
  question_label string @description("e.g. Q1, Q2(a)(i)")
  marks int
  pclm string @description("PCLM rationale for this question")
}

// ============================================================================
// Functions
// ============================================================================

function ChemistryWebStudyPlan(
  subject: string,
  weeks_until_exam: int,
  target_level: ChemistryLevel,
  language: ChemistryLanguage,
  focus_topics: string[]
) -> ChemistryWebStudyPlanResponse {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ChemistryWebExamPaperDiscussion(
  subject: string,
  paper_year: int,
  paper_level: ChemistryLevel,
  paper_language: ChemistryLanguage,
  question_text: string
) -> ChemistryWebExamPaperDiscussionResponse {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ChemistryWebMarkingSchemeExplanation(
  subject: string,
  paper_year: int,
  paper_level: ChemistryLevel,
  paper_language: ChemistryLanguage
) -> ChemistryWebMarkingSchemeExplanationResponse {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
