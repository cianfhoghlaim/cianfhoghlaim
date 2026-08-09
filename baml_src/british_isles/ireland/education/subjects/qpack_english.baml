// BAML schema: English Quest Pack Generator (LC + JC)
//
// NCCA Leaving Certificate English (OL + HL) + Junior Cycle English.
// Topics: Comprehending, Composition (personal essay, discursive,
// argumentative, narrative, descriptive), Comparative (single text +
// comparative), Poetry (prescribed + unseen), Drama, Fiction.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

enum EnglNCCALevel {
  JC       @description("Junior Cycle English")
  LC_OL    @description("Leaving Certificate Ordinary Level English")
  LC_HL    @description("Leaving Certificate Higher Level English")
}

enum EnglTopicArea {
  COMPREHENDING            @description("Reading comprehension: fiction + non-fiction")
  COMPOSITION              @description("Personal essay, discursive, argumentative, narrative, descriptive")
  COMPARATIVE              @description("Comparative study of 2+ texts (mode: cultural context / vision / literary genre)")
  POETRY_PRESCRIBED        @description("Set poetry (8 poets prescribed for LC)")
  POETRY_UNSEEN            @description("Unseen poetry analysis")
  DRAMA_PRESCRIBED         @description("Set drama text (Shakespeare + Irish playwright)")
  FILM                    @description("Film studies (HL only since 2022)")
  SPOKEN_ENGLISH           @description("Oral / listening component")
  LITERARY_GENRE           @description("Genre conventions: novel, short story, drama, poetry")
  MEDIA_LITERACY           @description("Critical reading of journalism, advertising, social media")
}

enum EnglItemType {
  COMPREHENSION_ITEM
  COMPOSITION_PROMPT
  COMPARATIVE_ITEM
  POETRY_ANALYSIS
  UNSEEN_POETRY_ITEM
  DRAMA_ANALYSIS
  FILM_ANALYSIS
  MEDIA_LITERACY_ITEM
}

enum EnglFeedbackChannel {
  ENGL_TUTOR
  QUEST_GUIDE
  CURRICULUM_LOOKUP
  RESEARCH_ASSISTANT
}

class EnglBilingualText {
  text_en string
  text_ga string?
}

class EnglEvidenceLink {
  source_pdf string
  source_page int
  excerpt_en string
  excerpt_ga string?
  ncca_url string?
}

class EnglNCCALearningOutcome {
  lo_code string
  framework string
  level EnglNCCALevel
  topic EnglTopicArea
  competency_text EnglBilingualText
  marking_scheme_excerpt EnglBilingualText?
  evidence EnglEvidenceLink
}

class EnglFormativeItem {
  id string
  lo_code string
  level EnglNCCALevel
  topic EnglTopicArea
  item_type EnglItemType
  difficulty int @description("1-5")
  prompt EnglBilingualText
  expected_answer EnglBilingualText
  marking_scheme EnglBilingualText
  common_errors EnglBilingualText[]
  hints EnglBilingualText[]
  evidence EnglEvidenceLink
  feedback_channel EnglFeedbackChannel
  est_time_minutes int
}

class EnglFormativeItemAttempt {
  item_id string
  student_response string
  response_format string
  time_taken_seconds int
  hints_used int
}

class EnglScoreBreakdown {
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

class EnglQuestPack {
  id string
  subject string @description("Always 'english'") @stream.not_null
  framework string
  level EnglNCCALevel
  title EnglBilingualText @stream.not_null
  description EnglBilingualText
  total_items int
  total_marks int
  est_time_minutes int
  los_covered string[]
  items EnglFormativeItem[] @stream.with_state
  prerequisites string[]
  cross_subject_links string[] @description("LC-GAEL for translation, LC-HIST for cultural context")
  generated_at string
  generated_by string @description("Always 'engl_agent'")
}

class EnglQuestPackValidation {
  pack_id string
  is_valid bool
  errors string[]
  warnings string[]
}

// ============================================================================
// Real generation prompts (2026-08-08 docs-informed-quest-and-credential-
// generation-v1 change). Grounded in the v3 extraction types. `level: JC`
// is Junior Cycle English — no separate file.
// ============================================================================

function GenerateEnglQuestPack(
  syllabus: SyllabusDocument,
  past_papers: ExamPaper[],
  marking_schemes: MarkingScheme[],
  level: string
) -> EnglQuestPack {  client ExtractEn
  prompt #"
    You are building an English formative-assessment quest pack for NCCA
    students at level {{ level }} ("JC" = Junior Cycle; "LC_OL"/"LC_HL" =
    Leaving Cert Ordinary/Higher English). Ground every item in the official
    syllabus, past exam papers, and marking scheme guidance below — do not
    invent prescribed texts, learning outcomes, or questions beyond what
    these documents actually establish.

    Official syllabus:
    {{ syllabus }}

    Past exam papers (for question style + marks allocation reference):
    {{ past_papers }}

    Marking scheme guidance (for grading bands + common-error reference):
    {{ marking_schemes }}

    Build an EnglQuestPack:
    - subject: "english"
    - framework: "ncca-lc" if level starts with "LC", "ncca-jc" if level is "JC"
    - level: the EnglNCCALevel matching {{ level }}
    - title / description: bilingual; text_ga null if the syllabus is EN-only
    - items: select up to 15 learning outcomes spanning as many distinct
      module_topics as the syllabus has (breadth over exhaustive LO
      coverage — a quest pack is a bounded, completable unit, not the
      entire syllabus in one response), and generate one EnglFormativeItem
      per selected LO, drawn from
      syllabus.module_topics[].learning_outcomes — for COMPOSITION_PROMPT and
      ESSAY-style items, base the prompt on the actual mode/genre the
      syllabus names, not a generic essay title; for COMPREHENSION_ITEM,
      POETRY_ANALYSIS, DRAMA_ANALYSIS items, ground in any prescribed-text
      references the syllabus text actually contains; where a past-paper
      question's related_lo_id matches, mirror its style and mark
      allocation; hints escalate from a light nudge to concrete structural
      guidance; evidence.source_page and evidence.excerpt_en (+ excerpt_ga
      if available) copied verbatim from the grounding text, never invented;
      evidence.source_pdf from syllabus.source_pdf
    - los_covered: exactly the LO codes of the items you actually
      generated above (not the full syllabus's LO list)
    - total_items / total_marks / est_time_minutes: sums over the actual items
    - prerequisites / cross_subject_links: only what the syllabus's
      cross_curricular field or assessment_objectives actually name
    - generated_at: current ISO-8601 datetime
    - generated_by: "engl_agent"

    Count and cite carefully from the actual text. Output exactly one complete
    JSON object matching EnglQuestPack. Never use ellipses (...) or comments;
    include every one of your selected items in full (up to 15 — never
    truncate a generated item, but do not exceed the cap either).

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ExtractEnglLOStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"
    Extract every distinct NCCA English learning-outcome statement from the
    syllabus paragraph below. Return each as its own string, verbatim from
    the text — do not merge multiple outcomes into one string.

    {{ _.role("user") }}
    Paragraph:
    {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

function GenerateEnglFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string,
  evidence: EnglEvidenceLink
) -> EnglFormativeItem {  client ExtractEn
  prompt #"
    You are writing a single formative-assessment item for NCCA English
    learning outcome {{ lo_code }} (topic: {{ topic }}, level: {{ level }},
    target difficulty: {{ difficulty }}/5).

    Ground the item entirely in this verbatim evidence from the official
    syllabus — do not write a generic English question unrelated to it:

    {{ evidence }}

    Build an EnglFormativeItem:
    - id: a fresh UUID
    - lo_code: {{ lo_code }}, level: the EnglNCCALevel matching {{ level }},
      topic: the EnglTopicArea matching {{ topic }}
    - item_type: choose the type that best fits the evidence (e.g.
      COMPOSITION_PROMPT for composition outcomes, POETRY_ANALYSIS/
      DRAMA_ANALYSIS for prescribed-text outcomes, COMPREHENSION_ITEM for
      reading outcomes)
    - difficulty: {{ difficulty }}
    - prompt / expected_answer / marking_scheme: bilingual, derived from the
      evidence excerpt, not a generic template
    - common_errors: plausible mistakes for this specific outcome
    - hints: exactly 4, escalating from a light nudge to concrete structural
      guidance
    - evidence: pass the input evidence through unchanged
    - feedback_channel: ENGL_TUTOR for content items, CURRICULUM_LOOKUP for
      definitional items
    - est_time_minutes: realistic for the item's difficulty (1-30)

    Output exactly one complete JSON object matching EnglFormativeItem.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ScoreEnglFormativeResponse(
  item: EnglFormativeItem,
  attempt: EnglFormativeItemAttempt
) -> EnglScoreBreakdown {  client ExtractEn
  prompt #"
    You are marking a student's response to an English formative item, using
    the item's own marking scheme.

    Item (including its expected_answer and marking_scheme):
    {{ item }}

    Student attempt:
    {{ attempt }}

    Build an EnglScoreBreakdown:
    - item_id: {{ item.id }}, lo_code: {{ item.lo_code }}
    - total_marks: derived from item.marking_scheme's stated allocation
    - marks_awarded / marks_per_step: partial credit per the marking scheme,
      weighing content, structure, and language use as the scheme directs
    - is_correct: true iff marks_awarded == total_marks
    - partial_credit_pct: marks_awarded / total_marks * 100
    - feedback_en / feedback_ga: specific to what the student actually wrote
    - next_recommended_lo: a plausible next LO only if the response reveals a
      specific gap; otherwise null
    - badge_earned: true iff partial_credit_pct >= 80

    Output exactly one complete JSON object matching EnglScoreBreakdown.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

function ValidateEnglQuestPack(pack: EnglQuestPack) -> EnglQuestPackValidation {  client ExtractEn
  prompt #"
    Validate the internal consistency of this EnglQuestPack — every item's
    lo_code SHOULD appear in los_covered, total_items SHOULD equal
    items.length, total_marks SHOULD equal the sum of each item's marking
    scheme allocation, and no item SHOULD have an empty evidence.excerpt_en.

    Quest pack:
    {{ pack }}

    Build an EnglQuestPackValidation: pack_id from the input, is_valid true
    only if no errors were found, errors for hard inconsistencies, warnings
    for anything suspicious but not necessarily wrong.

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}