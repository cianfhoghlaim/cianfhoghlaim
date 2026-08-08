// BAML schema: History Quest Pack Generator (LC + JC)
// NCCA Leaving Certificate History (OL + HL) + Junior Cycle History.
// Topics: Early Modern Ireland, Modern Ireland, European History,
// World History, Research Study, Document Study.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

enum HistNCCALevel {
  JC
  LC_OL
  LC_HL
}

enum HistTopicArea {
  EARLY_MODERN_IRELAND_1500_1800
  MODERN_IRELAND_1800_PRESENT
  EUROPEAN_HISTORY
  WORLD_HISTORY
  RESEARCH_STUDY
  DOCUMENT_STUDY
  SHORT_ANSWERS_DOCUMENTS
}

enum HistItemType {
  DOCUMENT_BASED_QUESTION
  ESSAY_PROMPT
  SHORT_ANSWER
  CONCEPTUAL
  SOURCE_COMPARISON
}

enum HistFeedbackChannel {
  HIST_TUTOR
  QUEST_GUIDE
  CURRICULUM_LOOKUP
  RESEARCH_ASSISTANT
}

class HistBilingualText {
  text_en string
  text_ga string?
}

class HistEvidenceLink {
  source_pdf string
  source_page int
  excerpt_en string
  excerpt_ga string?
  ncca_url string?
}

class HistNCCALearningOutcome {
  lo_code string
  framework string
  level HistNCCALevel
  topic HistTopicArea
  competency_text HistBilingualText
  marking_scheme_excerpt HistBilingualText?
  evidence HistEvidenceLink
}

class HistFormativeItem {
  id string
  lo_code string
  level HistNCCALevel
  topic HistTopicArea
  item_type HistItemType
  difficulty int @description("1-5")
  prompt HistBilingualText
  expected_answer HistBilingualText
  marking_scheme HistBilingualText
  common_errors HistBilingualText[]
  hints HistBilingualText[]
  evidence HistEvidenceLink
  feedback_channel HistFeedbackChannel
  est_time_minutes int
}

class HistFormativeItemAttempt {
  item_id string
  student_response string
  response_format string
  time_taken_seconds int
  hints_used int
}

class HistScoreBreakdown {
  item_id string
  lo_code string
  total_marks int
  marks_awarded int
  marks_per_step int[]
  is_correct bool
  partial_credit_pct float
  feedback_en string
  feedback_ga string?
  next_recommended_lo string?
  badge_earned bool
}

class HistQuestPack {
  id string
  subject string @description("Always 'history'") @stream.not_null
  framework string
  level HistNCCALevel
  title HistBilingualText @stream.not_null
  description HistBilingualText
  total_items int
  total_marks int
  est_time_minutes int
  los_covered string[]
  items HistFormativeItem[] @stream.with_state
  prerequisites string[]
  cross_subject_links string[] @description("LC-GAEL, LC-ENGL for cultural synthesis")
  generated_at string
  generated_by string @description("Always 'hist_agent'")
}

class HistQuestPackValidation {
  pack_id string
  is_valid bool
  errors string[]
  warnings string[]
}

// ============================================================================
// Real generation prompts (2026-08-08 docs-informed-quest-and-credential-
// generation-v1 change). Grounded in the v3 extraction types. `level: JC`
// is Junior Cycle History — no separate file.
// ============================================================================

function GenerateHistQuestPack(
  syllabus: SyllabusDocument,
  past_papers: ExamPaper[],
  marking_schemes: MarkingScheme[],
  level: string
) -> HistQuestPack {  client ExtractEn
  prompt #"
    You are building a History formative-assessment quest pack for NCCA
    students at level {{ level }} ("JC" = Junior Cycle; "LC_OL"/"LC_HL" =
    Leaving Cert Ordinary/Higher History). Ground every item in the official
    syllabus, past exam papers, and marking scheme guidance below — do not
    invent topics, learning outcomes, or questions beyond what these
    documents actually establish.

    Official syllabus:
    {{ syllabus }}

    Past exam papers (for question style + marks allocation reference):
    {{ past_papers }}

    Marking scheme guidance (for grading bands + common-error reference):
    {{ marking_schemes }}

    Build a HistQuestPack:
    - subject: "history"
    - framework: "ncca-lc" if level starts with "LC", "ncca-jc" if level is "JC"
    - level: the HistNCCALevel matching {{ level }}
    - title / description: bilingual; text_ga null only if the syllabus text
      itself is English-only
    - items: select up to 15 learning outcomes spanning as many distinct
      module_topics as the syllabus has (breadth over exhaustive LO
      coverage — a quest pack is a bounded, completable unit, not the
      entire syllabus in one response), and generate one HistFormativeItem
      per selected LO, drawn from
      syllabus.module_topics[].learning_outcomes — prefer
      DOCUMENT_BASED_QUESTION or SOURCE_COMPARISON where the syllabus text
      references primary-source study, ESSAY_PROMPT for synthesis outcomes;
      where a past-paper question's related_lo_id matches, mirror its style
      and mark allocation; hints escalate from a light nudge to concrete
      structural guidance; evidence.source_page and evidence.excerpt_en (+
      excerpt_ga if available) copied verbatim from the grounding text,
      never invented; evidence.source_pdf from syllabus.source_pdf
    - los_covered: exactly the LO codes of the items you actually
      generated above (not the full syllabus's LO list)
    - total_items / total_marks / est_time_minutes: sums over the actual items
    - prerequisites / cross_subject_links: only what the syllabus's
      cross_curricular field or assessment_objectives actually name
    - generated_at: current ISO-8601 datetime
    - generated_by: "hist_agent"

    Count and cite carefully from the actual text. Output exactly one complete
    JSON object matching HistQuestPack. Never use ellipses (...) or comments;
    include every one of your selected items in full (up to 15 — never
    truncate a generated item, but do not exceed the cap either).

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ExtractHistLOStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"
    Extract every distinct NCCA History learning-outcome statement from the
    syllabus paragraph below. Return each as its own string, verbatim from
    the text — do not merge multiple outcomes into one string.

    {{ _.role("user") }}
    Paragraph:
    {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

// -----------------------------------------------------------------------------
// ExtractHistGaStatement (added 2026-07-13-baml-cocoindex-tutorials-ga-v1)
// -----------------------------------------------------------------------------
// The bilingual EN+GA variant of ExtractHistLOStatement. History
// has more Irish-language coverage than Mathematics (LC History
// syllabi carry Irish-language strands on a subset of LOs), so
// this path returns the Irish statements verbatim from the NCCA
// source where present, and falls back to the English statements
// with a leading '[EN-only]' marker otherwise.

function ExtractHistGaStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"
    Extract every distinct Irish-language (Gaeilge) NCCA History
    learning-outcome statement from the syllabus paragraph below, verbatim.
    If the paragraph carries no Irish-language strand for a given outcome,
    return its English statement prefixed with "[EN-only] " instead of
    omitting it — History syllabi carry Irish-language strands on only a
    subset of learning outcomes.

    {{ _.role("user") }}
    Paragraph:
    {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

function GenerateHistFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: HistEvidenceLink
) -> HistFormativeItem {  client ExtractEn
  prompt #"
    You are writing a single formative-assessment item for NCCA History
    learning outcome {{ lo_code }} (topic: {{ topic }}, level: {{ level }},
    target difficulty: {{ difficulty }}/5).

    Ground the item entirely in this verbatim evidence from the official
    syllabus — do not write a generic history question unrelated to it:

    {{ evidence }}

    Build a HistFormativeItem:
    - id: a fresh UUID
    - lo_code: {{ lo_code }}, level: the HistNCCALevel matching {{ level }},
      topic: the HistTopicArea matching {{ topic }}
    - item_type: choose the type that best fits the evidence (e.g.
      DOCUMENT_BASED_QUESTION or SOURCE_COMPARISON for primary-source
      outcomes, ESSAY_PROMPT for synthesis outcomes)
    - difficulty: {{ difficulty }}
    - prompt / expected_answer / marking_scheme: bilingual, derived from the
      evidence excerpt, not a generic template
    - common_errors: plausible mistakes for this specific outcome
    - hints: exactly 4, escalating from a light nudge to concrete structural
      guidance
    - evidence: pass the input evidence through unchanged
    - feedback_channel: HIST_TUTOR for content items, CURRICULUM_LOOKUP for
      definitional items
    - est_time_minutes: realistic for the item's difficulty (1-30)

    Output exactly one complete JSON object matching HistFormativeItem.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ScoreHistFormativeResponse(
  item: HistFormativeItem,
  attempt: HistFormativeItemAttempt
) -> HistScoreBreakdown {  client ExtractEn
  prompt #"
    You are marking a student's response to a History formative item, using
    the item's own marking scheme.

    Item (including its expected_answer and marking_scheme):
    {{ item }}

    Student attempt:
    {{ attempt }}

    Build a HistScoreBreakdown:
    - item_id: {{ item.id }}, lo_code: {{ item.lo_code }}
    - total_marks: derived from item.marking_scheme's stated allocation
    - marks_awarded / marks_per_step: partial credit per the marking scheme
    - is_correct: true iff marks_awarded == total_marks
    - partial_credit_pct: marks_awarded / total_marks * 100
    - feedback_en / feedback_ga: specific to what the student actually wrote
    - next_recommended_lo: a plausible next LO only if the response reveals a
      specific gap; otherwise null
    - badge_earned: true iff partial_credit_pct >= 80

    Output exactly one complete JSON object matching HistScoreBreakdown.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ValidateHistQuestPack(pack: HistQuestPack) -> HistQuestPackValidation {  client ExtractEn
  prompt #"
    Validate the internal consistency of this HistQuestPack — every item's
    lo_code SHOULD appear in los_covered, total_items SHOULD equal
    items.length, total_marks SHOULD equal the sum of each item's marking
    scheme allocation, and no item SHOULD have an empty evidence.excerpt_en.

    Quest pack:
    {{ pack }}

    Build a HistQuestPackValidation: pack_id from the input, is_valid true
    only if no errors were found, errors for hard inconsistencies, warnings
    for anything suspicious but not necessarily wrong.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}