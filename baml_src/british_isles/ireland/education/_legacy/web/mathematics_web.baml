// BAML schema: Mathematics (Mata) web backend
//
// Per openspec/changes/2026-07-16-biiep-v1-lc-per-subject-web-surface-v1/
// The per-subject BAML backend that backs the 5 per-subject TanStack
// routes at apps/.../routes/en/subjects/mathematics/. Exposes 3 web-facing
// functions consumed by the per-subject Convex actions:
//
//   - WebStudyPlan              -> convex/mathematics/generateStudyPlan.ts
//   - WebExamPaperDiscussion    -> convex/mathematics/discussExamPaper.ts
//   - WebMarkingSchemeExplanation -> direct read from
//                                   apps/.../routes/en/subjects/mathematics/marking-schemes
//
// The foundation (qpack + syllabus extraction) lives in
// baml/education/subjects/qpack_mathematics.baml. This file layers the
// web-facing study-plan + discussion functions on top of that foundation.
//
// Usage:
//   from cianfhoghlaim.baml_client import b
//   plan = b.WebStudyPlan(subject="mathematics", weeks_until_exam=12,
//                        target_level="LC_HL", language="en")
//   discussion = b.WebExamPaperDiscussion(subject="mathematics", paper_year=2024,
//                                        paper_level="LC_HL", paper_language="en",
//                                        question_text="...")
//
// Re-gen after changes:  cd cianfhoghlaim && uv run baml-cli generate

// ============================================================================
// Enums
// ============================================================================

enum MathematicsLevel {
  JC @description("JC Mathematics level")
  LC_FL @description("LC_FL Mathematics level")
  LC_OL @description("LC_OL Mathematics level")
  LC_HL @description("LC_HL Mathematics level")
}

enum MathematicsLanguage {
  EN @description("English-language Mathematics")
  GA @description("Gaeilge (Mata) Mathematics")
}

// ============================================================================
// Output classes
// ============================================================================

class MathematicsWebStudyPlanResponse {
  title string @description("Title of the Mathematics study plan (bilingual EN+GA)")
  title_ga string @description("Gaeilge title")
  weeks int @description("Number of weeks in the plan")
  total_study_hours int @description("Total expected study hours")
  weeks_plan MathematicsStudyWeek[]
  milestones MathematicsStudyMilestone[]
  recommended_past_papers int[] @description("Past paper years to prioritise, oldest first")
  trace_id string? @description("Langfuse trace id (populated by the @trace decorator)")
}

class MathematicsStudyWeek {
  week_number int
  theme string @description("Week theme in English")
  theme_ga string @description("Week theme in Gaeilge")
  syllabus_topics string[] @description("NCCA syllabus topics covered this week")
  study_hours int
  past_paper_questions string[] @description("Past paper question ids to attempt this week")
  marking_scheme_focus string[] @description("PCLM patterns to drill this week")
  kc_weights MathematicsKCWeight[]
}

class MathematicsKCWeight {
  slug string @description("Key competency slug (one of: communicating, information-processing, critical-creative-thinking, personal-effectiveness, working-with-others)")
  weight int @description("Weight 0-100")
}

class MathematicsStudyMilestone {
  week int
  description string @description("Milestone description in English")
  description_ga string @description("Milestone description in Gaeilge")
  assessment_type string @description("Type of assessment: past_paper_full, past_paper_section, mock_orals, lab_practical, essay, ...")
}

class MathematicsWebExamPaperDiscussionResponse {
  question_summary string @description("Restatement of the question")
  question_summary_ga string? @description("Gaeilge summary")
  marking_scheme string @description("The PCLM marking scheme for this question")
  marking_scheme_ga string? @description("Gaeilge marking scheme")
  model_answer_outline string[] @description("Step-by-step model answer outline")
  model_answer_outline_ga string[] @description("Gaeilge outline")
  common_mistakes string[] @description("Common student mistakes for this question")
  marks_breakdown MathematicsMarksBreakdown[]
  follow_up_questions string[] @description("Suggested follow-up questions the tutor might ask")
  trace_id string?
}

class MathematicsMarksBreakdown {
  part_label string @description("e.g. (a), (b)(i), (c)")
  part_text string @description("What this part asks for")
  marks int
  marking_notes string @description("How marks are awarded for this part")
}

class MathematicsWebMarkingSchemeExplanationResponse {
  paper_year int
  paper_level MathematicsLevel
  paper_language MathematicsLanguage
  total_marks int
  sections MathematicsMarkingSection[]
  pclm_patterns string[] @description("PCLM patterns used throughout the paper")
  trace_id string?
}

class MathematicsMarkingSection {
  section_label string @description("e.g. Section A, Section B")
  total_marks int
  questions MathematicsMarkingQuestion[]
}

class MathematicsMarkingQuestion {
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
  target_level: MathematicsLevel,
  language: MathematicsLanguage,
  focus_topics: string[]
) -> MathematicsWebStudyPlanResponse {
  // Build a per-subject study plan over `weeks_until_exam` weeks for the
  // chosen target_level (LC HL/OL/FL or JC). The function delegates to the
  // per-subject qpack + syllabus extraction in qpack_mathematics.baml to ground the
  // plan in real NCCA learning outcomes and SEC past-paper questions.
  //
  // The Convex action convex/mathematics/generateStudyPlan.ts invokes this
  // function and persists the response to study_plans.
  prompt #"
    You are the Mathematics study planner for the Cianfhoghlaim BIEP v1
    per-subject interactive web surface.

    Subject slug: { subject }
    Target level: { target_level }
    Language: { language }
    Weeks until exam: { weeks_until_exam }
    Optional focus topics: { focus_topics }

    Build a { weeks_until_exam }-week { target_level } Mathematics study
    plan grounded in the NCCA Mathematics syllabus + SEC past-paper corpus.
    Each week must reference concrete syllabus topics + past-paper
    question ids + PCLM marking-scheme patterns. Include 3-5 milestones
    (one per assessment block).

    Return strictly as MathematicsWebStudyPlanResponse with
    bilingual EN+GA fields where applicable.
  "#
}

function WebExamPaperDiscussion(
  subject: string,
  paper_year: int,
  paper_level: MathematicsLevel,
  paper_language: MathematicsLanguage,
  question_text: string
) -> MathematicsWebExamPaperDiscussionResponse {
  // Walk a student through a single Mathematics past-paper question.
  // Returns the PCLM marking scheme + a model answer outline + common
  // mistakes + marks breakdown + follow-up questions.
  //
  // Invoked by the Convex action convex/mathematics/discussExamPaper.ts.
  prompt #"
    You are the Mathematics exam-paper discussion tutor for the Cianfhoghlaim
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

    Return strictly as MathematicsWebExamPaperDiscussionResponse.
  "#
}

function WebMarkingSchemeExplanation(
  subject: string,
  paper_year: int,
  paper_level: MathematicsLevel,
  paper_language: MathematicsLanguage
) -> MathematicsWebMarkingSchemeExplanationResponse {
  // Explain the full marking scheme (PCLM patterns) for an entire
  // Mathematics past paper at the chosen level + language.
  //
  // Invoked directly from apps/.../routes/en/subjects/mathematics/marking-schemes.
  prompt #"
    You are the Mathematics marking-scheme explainer for the Cianfhoghlaim
    BIEP v1 per-subject interactive web surface.

    Subject slug: { subject }
    Paper year: { paper_year }
    Paper level: { paper_level }
    Paper language: { paper_language }

    Walk through every section + question in the marking scheme. Highlight
    the PCLM patterns used (e.g. partial credit for setup, marks for
    logical marking, dependent steps).

    Return strictly as MathematicsWebMarkingSchemeExplanationResponse.
  "#
}
