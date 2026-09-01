// BAML schema: Geography (Tireolaiocht) web backend
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject BAML backend that backs the 5 per-subject TanStack
// routes at apps/.../routes/en/subjects/geography/. Exposes 3 web-facing
// functions consumed by the per-subject Convex actions:
//
//   - WebStudyPlan              -> convex/geography/generateStudyPlan.ts
//   - WebExamPaperDiscussion    -> convex/geography/discussExamPaper.ts
//   - WebMarkingSchemeExplanation -> direct read from
//                                   apps/.../routes/en/subjects/geography/marking-schemes
//
// The foundation (qpack + syllabus extraction) lives in
// baml/education/subjects/qpack_geography.baml. This file layers the
// web-facing study-plan + discussion functions on top of that foundation.
//
// Usage:
//   from cianfhoghlaim.baml_client import b
//   plan = b.WebStudyPlan(subject="geography", weeks_until_exam=12
//   discussion = b.WebExamPaperDiscussion(subject="geography", paper_year=2024
//                                        question_text="...")
//
// Re-gen after changes:  cd cianfhoghlaim && uv run baml-cli generate

// ============================================================================
// Enums
// ============================================================================

enum GeographyLevel {
  LC_OL @description("LC_OL Geography level")
  LC_HL @description("LC_HL Geography level")
}

enum GeographyLanguage {
  EN @description("English-language Geography")
  GA @description("Gaeilge (Tireolaiocht) Geography")
}

// ============================================================================
// Output classes
// ============================================================================

class GeographyWebStudyPlanResponse {
  title string @description("Title of the Geography study plan (bilingual EN+GA)")
  title_ga string @description("Gaeilge title")
  weeks int @description("Number of weeks in the plan")
  total_study_hours int @description("Total expected study hours")
  weeks_plan GeographyStudyWeek[]
  milestones GeographyStudyMilestone[]
  recommended_past_papers int[] @description("Past paper years to prioritise, oldest first")
  trace_id string? @description("Langfuse trace id (populated by the @trace decorator)")
}

class GeographyStudyWeek {
  week_number int
  theme string @description("Week theme in English")
  theme_ga string @description("Week theme in Gaeilge")
  syllabus_topics string[] @description("NCCA syllabus topics covered this week")
  study_hours int
  past_paper_questions string[] @description("Past paper question ids to attempt this week")
  marking_scheme_focus string[] @description("PCLM patterns to drill this week")
  kc_weights GeographyKCWeight[]
}

class GeographyKCWeight {
  slug string @description("Key competency slug (one of: communicating, information-processing, critical-creative-thinking, personal-effectiveness, working-with-others)")
  weight int @description("Weight 0-100")
}

class GeographyStudyMilestone {
  week int
  description string @description("Milestone description in English")
  description_ga string @description("Milestone description in Gaeilge")
  assessment_type string @description("Type of assessment: past_paper_full, past_paper_section, mock_orals, lab_practical, essay, ...")
}

class GeographyWebExamPaperDiscussionResponse {
  question_summary string @description("Restatement of the question")
  question_summary_ga string? @description("Gaeilge summary")
  marking_scheme string @description("The PCLM marking scheme for this question")
  marking_scheme_ga string? @description("Gaeilge marking scheme")
  model_answer_outline string[] @description("Step-by-step model answer outline")
  model_answer_outline_ga string[] @description("Gaeilge outline")
  common_mistakes string[] @description("Common student mistakes for this question")
  marks_breakdown GeographyMarksBreakdown[]
  follow_up_questions string[] @description("Suggested follow-up questions the tutor might ask")
  trace_id string?
}

class GeographyMarksBreakdown {
  part_label string @description("e.g. (a), (b)(i), (c)")
  part_text string @description("What this part asks for")
  marks int
  marking_notes string @description("How marks are awarded for this part")
}

class GeographyWebMarkingSchemeExplanationResponse {
  paper_year int
  paper_level GeographyLevel
  paper_language GeographyLanguage
  total_marks int
  sections GeographyMarkingSection[]
  pclm_patterns string[] @description("PCLM patterns used throughout the paper")
  trace_id string?
}

class GeographyMarkingSection {
  section_label string @description("e.g. Section A, Section B")
  total_marks int
  questions GeographyMarkingQuestion[]
}

class GeographyMarkingQuestion {
  question_label string @description("e.g. Q1, Q2(a)(i)")
  marks int
  pclm string @description("PCLM rationale for this question")
}

// ============================================================================
// Functions
// ============================================================================

function GeographyWebStudyPlan(
  subject: string,
  weeks_until_exam: int,
  target_level: GeographyLevel,
  language: GeographyLanguage,
  focus_topics: string[]
) -> GeographyWebStudyPlanResponse {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

function GeographyWebExamPaperDiscussion(
  subject: string,
  paper_year: int,
  paper_level: GeographyLevel,
  paper_language: GeographyLanguage,
  question_text: string
) -> GeographyWebExamPaperDiscussionResponse {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

function GeographyWebMarkingSchemeExplanation(
  subject: string,
  paper_year: int,
  paper_level: GeographyLevel,
  paper_language: GeographyLanguage
) -> GeographyWebMarkingSchemeExplanationResponse {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
