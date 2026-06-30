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
  text_en: string
  text_ga: string?
}

class EnglEvidenceLink {
  source_pdf: string
  source_page: int
  excerpt_en: string
  excerpt_ga: string?
  ncca_url: string?
}

class EnglNCCALearningOutcome {
  lo_code: string
  framework: string
  level: EnglNCCALevel
  topic: EnglTopicArea
  competency_text: EnglBilingualText
  marking_scheme_excerpt: EnglBilingualText?
  evidence: EnglEvidenceLink
}

class EnglFormativeItem {
  id: string
  lo_code: string
  level: EnglNCCALevel
  topic: EnglTopicArea
  item_type: EnglItemType
  difficulty: int @description("1-5")
  prompt: EnglBilingualText
  expected_answer: EnglBilingualText
  marking_scheme: EnglBilingualText
  common_errors: EnglBilingualText[]
  hints: EnglBilingualText[]
  evidence: EnglEvidenceLink
  feedback_channel: EnglFeedbackChannel
  est_time_minutes: int
}

class EnglFormativeItemAttempt {
  item_id: string
  student_response: string
  response_format: string
  time_taken_seconds: int
  hints_used: int
}

class EnglScoreBreakdown {
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

class EnglQuestPack {
  id: string
  subject: string @description("Always 'english'")
  framework: string
  level: EnglNCCALevel
  title: EnglBilingualText
  description: EnglBilingualText
  total_items: int
  total_marks: int
  est_time_minutes: int
  los_covered: string[]
  items: EnglFormativeItem[]
  prerequisites: string[]
  cross_subject_links: string[] @description("LC-GAEL for translation, LC-HIST for cultural context")
  generated_at: string
  generated_by: string @description("Always 'engl_agent'")
}

class EnglQuestPackValidation {
  pack_id: string
  is_valid: bool
  errors: string[]
  warnings: string[]
}

function GenerateEnglQuestPack(
  syllabus: LeavingCertSyllabus,
  past_papers: LeavingCertPastPaper[],
  marking_schemes: LeavingCertMarkingScheme[],
  level: string
) -> EnglQuestPack {
  client ExtractEnStrong
  prompt #"
    You are an Irish Leaving Certificate English expert. Build a
    formative assessment quest pack for NCCA English at the {{ level }}
    level (JC, LC_OL, or LC_HL).

    Cover ALL learning outcomes with ≥1 FormativeItem each. Reference
    the source NCCA PDF page in each item's evidence. Order items by
    difficulty (1 → 5). Suggest cross-subject links to Gaeilge (for
    translation practice) and to History (for cultural-context synthesis).

    Syllabus: {{ syllabus }}
    Past papers: {{ past_papers }}
    Marking schemes: {{ marking_schemes }}

    {{ ctx.output_format }}
  "#
}

function ExtractEnglLOStatement(paragraph: string) -> string[] {
  client ExtractEn
  prompt #"
    Extract all English learning outcome statements from the following
    NCCA syllabus paragraph.

    Paragraph: {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

function GenerateEnglFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string
) -> EnglFormativeItem {
  client ExtractEnStrong
  prompt #"
    Generate a single formative assessment item for the NCCA English
    learning outcome {{ lo_code }}.

    Difficulty: {{ difficulty }}
    Level: {{ level }} (JC / LC_OL / LC_HL)
    Topic: {{ topic }}

    Include 4 graduated hints, ≥2 common errors, evidence.source_page,
    bilingual EN + GA, est_time_minutes 1-30.

    {{ ctx.output_format }}
  "#
}

function ScoreEnglFormativeResponse(
  item: EnglFormativeItem,
  attempt: EnglFormativeItemAttempt
) -> EnglScoreBreakdown {
  client ExtractEnStrong
  prompt #"
    Score the English formative item attempt.

    Item: {{ item }}
    Attempt: {{ attempt }}

    Compute marks, feedback_en + feedback_ga, badge_earned.

    {{ ctx.output_format }}
  "#
}

function ValidateEnglQuestPack(pack: EnglQuestPack) -> EnglQuestPackValidation {
  client ExtractEn
  prompt #"
    Validate the English quest pack. Check LO codes + difficulty bounds + time bounds.

    Pack: {{ pack }}

    {{ ctx.output_format }}
  "#
}