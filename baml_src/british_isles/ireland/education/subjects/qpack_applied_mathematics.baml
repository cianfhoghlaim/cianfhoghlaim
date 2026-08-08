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

// ============================================================================
// Real generation prompts (2026-08-08 docs-informed-quest-and-credential-
// generation-v1 change). Grounded in the v3 extraction types. Applied
// Mathematics has NO Junior Cycle equivalent (`AppmNCCALevel` is `LC_HL`
// only) — this subject is out of scope for the Junior Cycle phase of this
// change.
// ============================================================================

function GenerateAppmQuestPack(
  syllabus: SyllabusDocument,
  past_papers: ExamPaper[],
  marking_schemes: MarkingScheme[],
  level: string
) -> AppmQuestPack {  client ExtractEn
  prompt #"
    You are building an Applied Mathematics formative-assessment quest pack
    for NCCA Leaving Certificate Higher Level students (Applied Mathematics
    is Higher Level only; {{ level }} should be "LC_HL"). Ground every item
    in the official syllabus, past exam papers, and marking scheme guidance
    below — do not invent topics, learning outcomes, or questions beyond
    what these documents actually establish.

    Official syllabus:
    {{ syllabus }}

    Past exam papers (for question style + marks allocation reference):
    {{ past_papers }}

    Marking scheme guidance (for grading bands + common-error reference):
    {{ marking_schemes }}

    Build an AppmQuestPack:
    - subject: "applied_mathematics"
    - framework: "ncca-lc" (Applied Mathematics has no Junior Cycle track)
    - level: LC_HL
    - title / description: bilingual; text_ga null only if the syllabus text
      itself is English-only (the common case for Applied Mathematics)
    - items: one AppmFormativeItem per learning outcome actually present in
      syllabus.module_topics[].learning_outcomes — prefer WORKED_SOLUTION or
      VISUAL_INTERPRETATION for mechanics outcomes involving forces/motion
      diagrams, PROOF where the syllabus asks students to derive a result;
      where a past-paper question's related_lo_id matches, mirror its style
      and mark allocation; hints escalate from a light nudge to a
      near-complete worked solution; evidence.source_page and
      evidence.excerpt_en copied verbatim from the grounding syllabus text,
      never invented; evidence.source_pdf from syllabus.source_pdf
    - los_covered: every lo actually present in the syllabus
    - total_items / total_marks / est_time_minutes: sums over the actual items
    - prerequisites: pure Mathematics LO codes (LC-MATHS-LO-*) the syllabus
      text implies as background (calculus, vectors, trigonometry)
    - cross_subject_links: only what the syllabus's cross_curricular field
      or assessment_objectives actually name
    - generated_at: current ISO-8601 datetime
    - generated_by: "appm_agent"

    Count and cite carefully from the actual text. Output exactly one complete
    JSON object matching AppmQuestPack. Never use ellipses (...) or comments;
    include every item in full, however long the list is.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ExtractAppmLOStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"
    Extract every distinct NCCA Applied Mathematics learning-outcome
    statement from the syllabus paragraph below. Return each as its own
    string, verbatim from the text — do not merge multiple outcomes into one
    string.

    {{ _.role("user") }}
    Paragraph:
    {{ paragraph }}

    {{ ctx.output_format }}
  "#
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
  prompt #"
    Extract every distinct Irish-language (Gaeilge) NCCA Applied Mathematics
    learning-outcome statement from the syllabus paragraph below, verbatim.
    Applied Mathematics is almost entirely English-language at NCCA level —
    if the paragraph carries no Irish-language strand, return an empty list
    rather than translating.

    {{ _.role("user") }}
    Paragraph:
    {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

function GenerateAppmFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: AppmEvidenceLink
) -> AppmFormativeItem {  client ExtractEn
  prompt #"
    You are writing a single formative-assessment item for NCCA Applied
    Mathematics learning outcome {{ lo_code }} (topic: {{ topic }}, level:
    {{ level }}, target difficulty: {{ difficulty }}/5).

    Ground the item entirely in this verbatim evidence from the official
    syllabus — do not write a generic mechanics question unrelated to it:

    {{ evidence }}

    Build an AppmFormativeItem:
    - id: a fresh UUID
    - lo_code: {{ lo_code }}, level: LC_HL, topic: the AppmTopicArea
      matching {{ topic }}
    - item_type: choose the type that best fits the evidence (e.g.
      WORKED_SOLUTION for calculation-heavy outcomes, VISUAL_INTERPRETATION
      for force/motion-diagram outcomes, PROOF where the syllabus asks
      students to derive a result)
    - difficulty: {{ difficulty }}
    - prompt / expected_answer / marking_scheme: bilingual, derived from the
      evidence excerpt, not a generic template
    - common_errors: plausible mistakes for this specific outcome (e.g. sign
      errors, unit mismatches, mixing up scalar/vector quantities)
    - hints: exactly 4, escalating from a light nudge to a near-complete
      worked solution
    - evidence: pass the input evidence through unchanged
    - feedback_channel: APPM_TUTOR for calculation items, MATH_BRIDGE where
      the outcome depends on prerequisite pure-maths content, CURRICULUM_LOOKUP
      for definitional items
    - est_time_minutes: realistic for the item's difficulty (1-30)

    Output exactly one complete JSON object matching AppmFormativeItem.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ScoreAppmFormativeResponse(
  item: AppmFormativeItem,
  attempt: AppmFormativeItemAttempt
) -> AppmScoreBreakdown {  client ExtractEn
  prompt #"
    You are marking a student's response to an Applied Mathematics formative
    item, using the item's own marking scheme — do not apply an external
    standard.

    Item (including its expected_answer and marking_scheme):
    {{ item }}

    Student attempt:
    {{ attempt }}

    Build an AppmScoreBreakdown:
    - item_id: {{ item.id }}, lo_code: {{ item.lo_code }}
    - total_marks: derived from item.marking_scheme's stated allocation
    - marks_awarded / marks_per_step: award partial credit per the marking
      scheme's per-step breakdown, not all-or-nothing
    - is_correct: true iff marks_awarded == total_marks
    - partial_credit_pct: marks_awarded / total_marks * 100
    - feedback_en / feedback_ga: specific to what the student actually wrote,
      referencing item.common_errors where applicable
    - next_recommended_lo: a plausible next LO only if the response reveals a
      specific gap; otherwise null
    - badge_earned: true iff partial_credit_pct >= 80

    Output exactly one complete JSON object matching AppmScoreBreakdown.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ValidateAppmQuestPack(pack: AppmQuestPack) -> AppmQuestPackValidation {  client ExtractEn
  prompt #"
    Validate the internal consistency of this AppmQuestPack — every item's
    lo_code SHOULD appear in los_covered, total_items SHOULD equal
    items.length, total_marks SHOULD equal the sum of each item's marking
    scheme allocation, and no item SHOULD have an empty evidence.excerpt_en.

    Quest pack:
    {{ pack }}

    Build an AppmQuestPackValidation: pack_id from the input, is_valid true
    only if no errors were found, errors for hard inconsistencies, warnings
    for anything suspicious but not necessarily wrong.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}