// BAML schema: Geography Quest Pack Generator (LC + JC)
// NCCA Leaving Certificate Geography (OL + HL) + Junior Cycle Geography.
// Topics: Physical Geography (rivers, coasts, climate, biomes),
// Regional Geography (Ireland, Europe, global), Geoecology,
// Human Environment (population, urban, economic).

enum GeogNCCALevel {
  JC
  LC_OL
  LC_HL
}

enum GeogTopicArea {
  PHYSICAL_RIVERS
  PHYSICAL_COASTS
  PHYSICAL_CLIMATE
  PHYSICAL_BIOMES
  PHYSICAL_PLATE_TECTONICS
  PHYSICAL_GLACIATION
  REGIONAL_IRELAND
  REGIONAL_EUROPE
  REGLOBAL_SUB_CONTINENT
  REGIONAL_GLOBAL
  GEOECOLOGY
  HUMAN_POPULATION
  HUMAN_URBAN
  HUMAN_ECONOMIC
  HUMAN_DEVELOPMENT
  FIELDWORK_INVESTIGATION
}

enum GeogItemType {
  SHORT_ANSWER
  WORKED_SOLUTION
  MAP_INTERPRETATION
  GRAPH_READING
  OS_MAP_SKILLS
  CONCEPTUAL
  ESSAY_PROMPT
  FIELDWORK_REPORT
}

enum GeogFeedbackChannel {
  GEOG_TUTOR
  QUEST_GUIDE
  CURRICULUM_LOOKUP
  RESEARCH_ASSISTANT
}

class GeogBilingualText {
  text_en string?
  text_ga string
}
class GeogEvidenceLink {
  source_pdf string
  source_page int
  excerpt_en string?
  excerpt_ga string
  ncca_url string?
}
class GeogNCCALearningOutcome {
  lo_code string
  framework string
  level GeogNCCALevel
  topic GeogTopicArea
  competency_text GeogBilingualText
  marking_scheme_excerpt GeogBilingualText?
  evidence GeogEvidenceLink
}
class GeogFormativeItem {
  id string
  lo_code string
  level GeogNCCALevel
  topic GeogTopicArea
  item_type GeogItemType
  difficulty int
  prompt GeogBilingualText
  expected_answer GeogBilingualText
  marking_scheme GeogBilingualText
  common_errors GeogBilingualText[]
  hints GeogBilingualText[]
  evidence GeogEvidenceLink
  feedback_channel GeogFeedbackChannel
  est_time_minutes int
}
class GeogFormativeItemAttempt {
  item_id string
  student_response string
  response_format string
  time_taken_seconds int
  hints_used int
}
class GeogScoreBreakdown {
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
class GeogQuestPack {
  id string
  subject string @description("Always 'geography'") @stream.not_null
  framework string
  level GeogNCCALevel
  title GeogBilingualText @stream.not_null
  description GeogBilingualText
  total_items int
  total_marks int
  est_time_minutes int
  los_covered string[]
  items GeogFormativeItem[] @stream.with_state
  prerequisites string[]
  cross_subject_links string[] @description("LC-MATHS for statistics, LC-ENGL for essay composition")
  generated_at string
  generated_by string @description("Always 'geog_agent'")
}
class GeogQuestPackValidation {
  pack_id string
  is_valid bool
  errors string[]
  warnings string[]
}

// ============================================================================
// Real generation prompts (2026-08-08 docs-informed-quest-and-credential-
// generation-v1 change). Grounded in the v3 extraction types. `level: JC`
// is Junior Cycle Geography — no separate file. Note: GeogBilingualText
// requires text_ga and makes text_en optional (the class's existing
// nullability, unchanged here) — always populate text_ga; populate
// text_en only when the source text or a faithful translation is available.
// ============================================================================

function GenerateGeogQuestPack(syllabus: SyllabusDocument, past_papers: ExamPaper[], marking_schemes: MarkingScheme[], level: string) -> GeogQuestPack {  client ExtractEn
  prompt #"
    You are building a Geography formative-assessment quest pack for NCCA
    students at level {{ level }} ("JC" = Junior Cycle; "LC_OL"/"LC_HL" =
    Leaving Cert Ordinary/Higher Geography). Ground every item in the
    official syllabus, past exam papers, and marking scheme guidance below —
    do not invent topics, learning outcomes, or questions beyond what these
    documents actually establish.

    Official syllabus:
    {{ syllabus }}

    Past exam papers (for question style + marks allocation reference):
    {{ past_papers }}

    Marking scheme guidance (for grading bands + common-error reference):
    {{ marking_schemes }}

    Build a GeogQuestPack:
    - subject: "geography"
    - framework: "ncca-lc" if level starts with "LC", "ncca-jc" if level is "JC"
    - level: the GeogNCCALevel matching {{ level }}
    - title / description: text_ga always populated; text_en only if
      derivable from the source
    - items: select up to 15 learning outcomes spanning as many distinct
      module_topics as the syllabus has (breadth over exhaustive LO
      coverage — a quest pack is a bounded, completable unit, not the
      entire syllabus in one response), and generate one GeogFormativeItem
      per selected LO, drawn from
      syllabus.module_topics[].learning_outcomes — prompt/expected_answer/
      marking_scheme grounded in the real syllabus wording, preferring
      MAP_INTERPRETATION / OS_MAP_SKILLS / GRAPH_READING item types where the
      syllabus text describes physical or fieldwork content; where a
      past-paper question's related_lo_id matches, mirror its style and mark
      allocation; hints escalate from a light nudge to a near-complete
      answer; evidence.source_page and evidence.excerpt_ga (+ excerpt_en if
      available) copied verbatim from the grounding text, never invented;
      evidence.source_pdf from syllabus.source_pdf
    - los_covered: exactly the LO codes of the items you actually
      generated above (not the full syllabus's LO list)
    - total_items / total_marks / est_time_minutes: sums over the actual items
    - prerequisites / cross_subject_links: only what the syllabus's
      cross_curricular field or assessment_objectives actually name
    - generated_at: current ISO-8601 datetime
    - generated_by: "geog_agent"

    Count and cite carefully from the actual text. Output exactly one complete
    JSON object matching GeogQuestPack. Never use ellipses (...) or comments;
    include every one of your selected items in full (up to 15 — never
    truncate a generated item, but do not exceed the cap either).

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ExtractGeogLOStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"
    Extract every distinct NCCA Geography learning-outcome statement from the
    syllabus paragraph below. Return each as its own string, verbatim from
    the text — do not merge multiple outcomes into one string.

    {{ _.role("user") }}
    Paragraph:
    {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

// -----------------------------------------------------------------------------
// ExtractGeogGaStatement (added 2026-07-13-baml-cocoindex-tutorials-ga-v1)
// -----------------------------------------------------------------------------
// The bilingual EN+GA variant of ExtractGeogLOStatement. Same
// return shape; routes via `client Default`; the prompt asks for
// the Irish (Gaeilge) statements verbatim with a leading '[EN-only]'
// fallback marker for LOs the NCCA did not translate.

function ExtractGeogGaStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"
    Extract every distinct Irish-language (Gaeilge) NCCA Geography
    learning-outcome statement from the syllabus paragraph below. Return each
    as its own string, verbatim from the text. If the paragraph is
    English-only, return an empty list rather than translating.

    {{ _.role("user") }}
    Paragraph:
    {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

function GenerateGeogFormativeItem(lo_code: string, difficulty: int, level: string, topic: string, evidence: GeogEvidenceLink) -> GeogFormativeItem {  client ExtractEn
  prompt #"
    You are writing a single formative-assessment item for NCCA Geography
    learning outcome {{ lo_code }} (topic: {{ topic }}, level: {{ level }},
    target difficulty: {{ difficulty }}/5).

    Ground the item entirely in this verbatim evidence from the official
    syllabus — do not write a generic geography question unrelated to it:

    {{ evidence }}

    Build a GeogFormativeItem:
    - id: a fresh UUID
    - lo_code: {{ lo_code }}, level: the GeogNCCALevel matching {{ level }},
      topic: the GeogTopicArea matching {{ topic }}
    - item_type: choose the type that best fits the evidence (e.g.
      MAP_INTERPRETATION or OS_MAP_SKILLS for physical/fieldwork outcomes,
      GRAPH_READING for climate/data outcomes, ESSAY_PROMPT for human
      geography synthesis)
    - difficulty: {{ difficulty }}
    - prompt / expected_answer / marking_scheme: text_ga always populated,
      derived from the evidence excerpt, not a generic template
    - common_errors: plausible mistakes for this specific outcome
    - hints: exactly 4, escalating from a light nudge to a near-complete answer
    - evidence: pass the input evidence through unchanged
    - feedback_channel: GEOG_TUTOR for content items, CURRICULUM_LOOKUP for
      definitional items
    - est_time_minutes: realistic for the item's difficulty (1-30)

    Output exactly one complete JSON object matching GeogFormativeItem.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ScoreGeogFormativeResponse(item: GeogFormativeItem, attempt: GeogFormativeItemAttempt) -> GeogScoreBreakdown {  client ExtractEn
  prompt #"
    You are marking a student's response to a Geography formative item,
    using the item's own marking scheme.

    Item (including its expected_answer and marking_scheme):
    {{ item }}

    Student attempt:
    {{ attempt }}

    Build a GeogScoreBreakdown:
    - item_id: {{ item.id }}, lo_code: {{ item.lo_code }}
    - total_marks: derived from item.marking_scheme's stated allocation
    - marks_awarded / marks_per_step: partial credit per the marking scheme
    - is_correct: true iff marks_awarded == total_marks
    - partial_credit_pct: marks_awarded / total_marks * 100
    - feedback_en / feedback_ga: specific to what the student actually wrote
    - next_recommended_lo: a plausible next LO only if the response reveals a
      specific gap; otherwise null
    - badge_earned: true iff partial_credit_pct >= 80

    Output exactly one complete JSON object matching GeogScoreBreakdown.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ValidateGeogQuestPack(pack: GeogQuestPack) -> GeogQuestPackValidation {  client ExtractEn
  prompt #"
    Validate the internal consistency of this GeogQuestPack — every item's
    lo_code SHOULD appear in los_covered, total_items SHOULD equal
    items.length, total_marks SHOULD equal the sum of each item's marking
    scheme allocation, and no item SHOULD have an empty evidence.excerpt_ga.

    Quest pack:
    {{ pack }}

    Build a GeogQuestPackValidation: pack_id from the input, is_valid true
    only if no errors were found, errors for hard inconsistencies, warnings
    for anything suspicious but not necessarily wrong.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}