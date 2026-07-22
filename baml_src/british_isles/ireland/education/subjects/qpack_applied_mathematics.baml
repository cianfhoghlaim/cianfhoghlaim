// BAML schema: Applied Mathematics Quest Pack Generator (LC Higher only)
//
// Builds formative assessment quest packs for NCCA Leaving Certificate
// Applied Mathematics at Higher Level only. APPM is the most
// mechanics-focused subject in the LC, with 7 broad topic areas
// covering dynamics, statics, rigid bodies, oscillations, gravity,
// and circular motion.
//
// Bilingual EN + GA on every user-facing field. Gaeilge-taught content
// is rare for APPM; text_ga will usually be null.
//
// Usage:
//   from cianfhoghlaim.baml_client import b
//   pack = b.GenerateAppmQuestPack(syllabus, past_papers, marking_schemes, "hl")
//   item = b.GenerateAppmFormativeItem("LC-APPM-LO-2.4", difficulty=3)
//
// Re-gen after changes:  `cd cianfhoghlaim && uv run baml-cli generate`

// ============================================================================
// Enums
// ============================================================================

enum AppmNCCALevel {
  LC_HL @description("Leaving Certificate Applied Mathematics (Higher Level only)")
}

enum AppmTopicArea {
  UNIFORM_ACCELERATION @description("Constant acceleration in 1D and 2D")
  NEWTONS_LAWS         @description("Force, mass, momentum; Newton's 3 laws")
  PROJECTILES          @description("2D motion under gravity")
  FRICTION             @description("Static + kinetic friction, limiting equilibrium")
  WORK_ENERGY_POWER    @description("Work, kinetic/potential energy, power")
  IMPULSE_MOMENTUM     @description("Impulse-momentum; conservation of momentum")
  CIRCULAR_MOTION      @description("Angular velocity, centripetal force, conical pendulum")
  SIMPLE_HARMONIC      @description("SHM: x = a sin(ωt); springs; pendulums")
  RIGID_BODY           @description("Moment of inertia; rotational dynamics; torque")
  STATICS              @description("Equilibrium of coplanar forces; moments; couples")
  GRAVITY              @description("Universal gravitation; circular orbits; escape velocity")
  HYDROSTATICS         @description("Pressure; buoyancy; Archimedes' principle")
  DIFFERENTIAL_EQUATIONS @description("1st-order + 2nd-order ODEs in context")
  VECTORS              @description("Vector algebra; dot/cross product; unit vectors")
  DIMENSIONAL_ANALYSIS @description("Checking equations via units")
}

enum AppmItemType {
  SHORT_ANSWER
  WORKED_SOLUTION
  CONCEPTUAL
  VISUAL_INTERPRETATION @description("Read forces, velocities, accelerations from diagrams")
  WORD_PROBLEM          @description("Real-world mechanics contextual applications")
  PROOF                 @description("Derive a result; e.g. derive v² = u² + 2as")
}

enum AppmFeedbackChannel {
  APPM_TUTOR             @description("Concrete + worked-example feedback (appm_agent)")
  QUEST_GUIDE            @description("Graduated hints (4 levels)")
  CURRICULUM_LOOKUP      @description("Direct NCCA LO citation")
  RESEARCH_ASSISTANT     @description("Cross-topic + cross-subject synthesis")
  MATH_BRIDGE            @description("Cross-subject link to Mathematics (calculus, vectors)")
}

// ============================================================================
// Core value types
// ============================================================================

class AppmBilingualText {
  text_en string
  text_ga string? @description("Irish translation; null if EN-only")
}

class AppmEvidenceLink {
  source_pdf string
  source_page int @description("PDF page (1-indexed)")
  excerpt_en string
  excerpt_ga string?
  ncca_url string?
}

class AppmNCCALearningOutcome {
  lo_code string @description("Canonical NCCA code, e.g. 'LC-APPM-LO-2.4'")
  framework string @description("Always 'ncca-lc' for this subject")
  level AppmNCCALevel
  topic AppmTopicArea
  competency_text AppmBilingualText
  marking_scheme_excerpt AppmBilingualText?
  evidence AppmEvidenceLink
}

// ============================================================================
// Formative items + quest packs
// ============================================================================

class AppmFormativeItem {
  id string
  lo_code string
  level AppmNCCALevel
  topic AppmTopicArea
  item_type AppmItemType
  difficulty int @description("1-5")
  prompt AppmBilingualText
  expected_answer AppmBilingualText
  marking_scheme AppmBilingualText
  common_errors AppmBilingualText[]
  hints AppmBilingualText[] @description("4 graduated hints, indexed 0-3")
  evidence AppmEvidenceLink
  feedback_channel AppmFeedbackChannel
  est_time_minutes int @description("1-30")
}

class AppmFormativeItemAttempt {
  item_id string
  student_response string
  response_format string @description("text / latex / image / multiple_choice")
  time_taken_seconds int
  hints_used int @description("0-4")
}

class AppmScoreBreakdown {
  item_id string
  lo_code string
  total_marks int
  marks_awarded int
  marks_per_step int[]
  is_correct bool
  partial_credit_pct float @description("0-100")
  feedback_en string
  feedback_ga string?
  next_recommended_lo string?
  badge_earned bool @description("True iff partial_credit_pct >= 80")
}

class AppmQuestPack {
  id string
  subject string @description("Always 'applied_mathematics'") @stream.not_null
  framework string @description("Always 'ncca-lc'")
  level AppmNCCALevel
  title AppmBilingualText @stream.not_null
  description AppmBilingualText
  total_items int
  total_marks int
  est_time_minutes int
  los_covered string[]
  items AppmFormativeItem[] @stream.with_state
  prerequisites string[] @description("Pure Mathematics LOs (LC-MATHS-LO-*) the student should have mastered first")
  cross_subject_links string[] @description("Suggested cross-subject LO codes (LC-MATHS-*, LC-CHEM, LC-PHYS)")
  generated_at string @description("ISO datetime")
  generated_by string @description("Always 'appm_agent'")
}

class AppmQuestPackValidation {
  pack_id string
  is_valid bool
  errors string[]
  warnings string[]
}

// ============================================================================
// BAML functions
// ============================================================================

function GenerateAppmQuestPack(
  syllabus: LeavingCertSyllabus,
  past_papers: PastPaper[],
  marking_schemes: MarkingSchemeSec[],
  level: string
) -> AppmQuestPack {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractAppmLOStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// -----------------------------------------------------------------------------
// ExtractAppmGaStatement (added 2026-07-13-baml-cocoindex-tutorials-ga-v1)
// -----------------------------------------------------------------------------
// The bilingual EN+GA variant of ExtractAppmLOStatement. Same
// return shape (`string[]`); routes via `client Default`; the
// prompt asks for the Irish (Gaeilge) statements verbatim with a
// leading '[EN-only]' fallback marker. Applied Mathematics is
// almost entirely English-language at NCCA level; the fallback
// path is the common case here.

function ExtractAppmGaStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function GenerateAppmFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string
) -> AppmFormativeItem {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ScoreAppmFormativeResponse(
  item: AppmFormativeItem,
  attempt: AppmFormativeItemAttempt
) -> AppmScoreBreakdown {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ValidateAppmQuestPack(pack: AppmQuestPack) -> AppmQuestPackValidation {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}