// BAML schema: History Quest Pack Generator (LC + JC)
// NCCA Leaving Certificate History (OL + HL) + Junior Cycle History.
// Topics: Early Modern Ireland, Modern Ireland, European History,
// World History, Research Study, Document Study.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

enum HistNCCALevel { JC, LC_OL, LC_HL }

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
  text_en: string
  text_ga: string?
}

class HistEvidenceLink {
  source_pdf: string
  source_page: int
  excerpt_en: string
  excerpt_ga: string?
  ncca_url: string?
}

class HistNCCALearningOutcome {
  lo_code: string
  framework: string
  level: HistNCCALevel
  topic: HistTopicArea
  competency_text: HistBilingualText
  marking_scheme_excerpt: HistBilingualText?
  evidence: HistEvidenceLink
}

class HistFormativeItem {
  id: string
  lo_code: string
  level: HistNCCALevel
  topic: HistTopicArea
  item_type: HistItemType
  difficulty: int @description("1-5")
  prompt: HistBilingualText
  expected_answer: HistBilingualText
  marking_scheme: HistBilingualText
  common_errors: HistBilingualText[]
  hints: HistBilingualText[]
  evidence: HistEvidenceLink
  feedback_channel: HistFeedbackChannel
  est_time_minutes: int
}

class HistFormativeItemAttempt {
  item_id: string
  student_response: string
  response_format: string
  time_taken_seconds: int
  hints_used: int
}

class HistScoreBreakdown {
  item_id: string
  lo_code: string
  total_marks: int
  marks_awarded: int
  marks_per_step: int[]
  is_correct: bool
  partial_credit_pct: float
  feedback_en: string
  feedback_ga: string?
  next_recommended_lo: string?
  badge_earned: bool
}

class HistQuestPack {
  id: string
  subject: string @description("Always 'history'") @stream.not_null
  framework: string
  level: HistNCCALevel
  title: HistBilingualText @stream.not_null
  description: HistBilingualText
  total_items: int
  total_marks: int
  est_time_minutes: int
  los_covered: string[]
  items: HistFormativeItem[] @stream.with_state
  prerequisites: string[]
  cross_subject_links: string[] @description("LC-GAEL, LC-ENGL for cultural synthesis")
  generated_at: string
  generated_by: string @description("Always 'hist_agent'")
}

class HistQuestPackValidation {
  pack_id: string
  is_valid: bool
  errors: string[]
  warnings: string[]
}

function GenerateHistQuestPack(
  syllabus: LeavingCertSyllabus,
  past_papers: LeavingCertPastPaper[],
  marking_schemes: LeavingCertMarkingScheme[],
  level: string
) -> HistQuestPack {
  client ExtractEnStrong
  prompt #"
    You are an Irish Leaving Certificate History expert. Build a
    formative assessment quest pack for NCCA History at the {{ level }}
    level (JC, LC_OL, or LC_HL).

    Cover ALL learning outcomes with ≥1 FormativeItem each. Reference
    the source NCCA PDF page in each item's evidence. Order items by
    difficulty (1 → 5). Suggest cross-subject links to Gaeilge and
    English (literature as historical source).

    Syllabus: {{ syllabus }}
    Past papers: {{ past_papers }}
    Marking schemes: {{ marking_schemes }}

    {{ ctx.output_format }}
  "#
}

function ExtractHistLOStatement(paragraph: string) -> string[] {
  client ExtractEn
  prompt #"
    Extract all History learning outcome statements from the following
    NCCA syllabus paragraph.

    Paragraph: {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

function GenerateHistFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string
) -> HistFormativeItem {
  client ExtractEnStrong
  prompt #"
    Generate a single History formative item for NCCA LO {{ lo_code }}.

    Difficulty: {{ difficulty }}
    Level: {{ level }} (JC / LC_OL / LC_HL)
    Topic: {{ topic }}

    Include 4 graduated hints, ≥2 common errors, evidence.source_page,
    bilingual EN + GA, est_time_minutes 1-30.

    {{ ctx.output_format }}
  "#
}

function ScoreHistFormativeResponse(
  item: HistFormativeItem,
  attempt: HistFormativeItemAttempt
) -> HistScoreBreakdown {
  client ExtractEnStrong
  prompt #"
    Score the History formative item attempt.

    Item: {{ item }}
    Attempt: {{ attempt }}

    {{ ctx.output_format }}
  "#
}

function ValidateHistQuestPack(pack: HistQuestPack) -> HistQuestPackValidation {
  client ExtractEn
  prompt #"
    Validate the History quest pack.

    Pack: {{ pack }}

    {{ ctx.output_format }}
  "#
}