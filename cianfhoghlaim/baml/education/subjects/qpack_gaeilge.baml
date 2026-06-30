// BAML schema: Gaeilge Quest Pack Generator (LC + JC)
//
// Builds formative assessment quest packs for NCCA Leaving Certificate
// Gaeilge (Irish) — taught IN IRISH. Bilingual EN+GA is special here:
// `text_en` is typically null for content; `text_ga` is the canonical
// value. The `text_en` field is reserved for citation + helper
// translation only.
//
// Gaeilge is the only subject taught primarily in Irish at the LC.
// 3 NCCA levels: Foundation, Ordinary, Higher.
//
// Topics: Léamhthuiscint, Litríocht, Gramadach, Filíocht, Prós,
// Béaloideas, Scríbhneoireacht (composition), Cluastuiscint
// (listening comprehension).
//
// Usage:
//   pack = b.GenerateGaelQuestPack(syllabus, past_papers, marking_schemes, "hl")
//   item = b.GenerateGaelFormativeItem("LC-GAEL-LO-2.4", difficulty=3)
//
// Re-gen:  cd cianfhoghlaim && uv run baml-cli generate

enum GaelNCCALevel {
  LC_FL @description("Leaving Certificate Foundation Level Gaeilge")
  LC_OL @description("Leaving Certificate Ordinary Level Gaeilge")
  LC_HL @description("Leaving Certificate Higher Level Gaeilge")
  JC    @description("Junior Cycle Gaeilge")
}

enum GaelTopicArea {
  LEAMHTHUISCINT     @description("Reading comprehension (aistí, nuachtlitirí, filíocht)")
  LITRIOCHT          @description("Literature: prós + filíocht + drámaíocht")
  GRAMADACH          @description("Grammar: aimsirí, modhanna, réimíreanna, tuiseal")
  FILIOCHT           @description("Poetry: filí móra (Ó Rathaille, Mhac an tSaoi, Ní Dhomhnaill)")
  PROS               @description("Prose: úrscéal, gearrscéal, aistí")
  BEALOIDEAS         @description("Folk tradition: scéalta, laethanta saint, paimsire")
  SCRIBHNEoireacht   @description("Composition: aistí, scéalta, litreacha, tráchtas")
  CLUASTUISCINT      @description("Listening comprehension (aural exam component)")
  SCOLAI             @description("Scholarly analysis of prescribed texts")
  CUNTASAIOCHT       @description("Translation EN ↔ GA")
}

enum GaelItemType {
  LEAMHTHUISCINT_ITEM   @description("Reading comprehension item")
  GRAMADACH_ITEM         @description("Grammar transformation / fill-in-the-blank")
  AISTRÚCHÁN_ITEM        @description("Translation EN ↔ GA")
  COMHRÁ_ITEM            @description("Conversation / dialogue")
  FILÍOCHT_ANALYSIS     @description("Poetry analysis")
  LITRÍOCHT_ANALYSIS    @description("Prose / drama analysis")
  COMPOSITION_PROMPT    @description("Long-form composition prompt")
  CLUASTUISCINT_ITEM     @description("Listening comprehension (transcribed audio)")
}

enum GaelFeedbackChannel {
  GAEL_TUTOR            @description("Gaeilge-medium feedback (native tutor)")
  QUEST_GUIDE           @description("Graduated hints (4 levels)")
  CURRICULUM_LOOKUP     @description("Direct NCCA LO citation")
  GRAMADACH_REVIEW      @description("Grammar review + conjugation tables")
  RESEARCH_ASSISTANT    @description("Cross-subject synthesis")
}

class GaelBilingualText {
  text_en: string? @description("English translation; null for Irish-only Gaeilge content")
  text_ga: string  @description("Canonical Irish text (required)")
}

class GaelEvidenceLink {
  source_pdf: string
  source_page: int @description("PDF page (1-indexed)")
  excerpt_ga: string  @description("Verbatim Irish excerpt (canonical)")
  excerpt_en: string? @description("Optional English translation")
  ncca_url: string?
}

class GaelNCCALearningOutcome {
  lo_code: string @description("Canonical NCCA code, e.g. 'LC-GAEL-LO-3.1'")
  framework: string @description("'ncca-lc' or 'ncaa-jc'")
  level: GaelNCCALevel
  topic: GaelTopicArea
  competency_text: GaelBilingualText @description("NCCA competency statement (Irish canonical)")
  marking_scheme_excerpt: GaelBilingualText?
  evidence: GaelEvidenceLink
}

class GaelFormativeItem {
  id: string
  lo_code: string
  level: GaelNCCALevel
  topic: GaelTopicArea
  item_type: GaelItemType
  difficulty: int @description("1-5")
  prompt: GaelBilingualText @description("Irish canonical; English null for comprehension items")
  expected_answer: GaelBilingualText
  marking_scheme: GaelBilingualText
  common_errors: GaelBilingualText[]
  hints: GaelBilingualText[] @description("4 graduated hints (Irish canonical)")
  evidence: GaelEvidenceLink
  feedback_channel: GaelFeedbackChannel
  est_time_minutes: int @description("1-30")
}

class GaelFormativeItemAttempt {
  item_id: string
  student_response: string @description("Student's response (Irish expected)")
  response_format: string @description("text / latex / image / audio")
  time_taken_seconds: int
  hints_used: int @description("0-4")
}

class GaelScoreBreakdown {
  item_id: string
  lo_code: string
  total_marks: int
  marks_awarded: int
  marks_per_step: int[]
  is_correct: bool
  partial_credit_pct: float @description("0-100")
  feedback_ga: string  @description("Irish feedback (canonical)")
  feedback_en: string? @description("Optional English translation of feedback")
  next_recommended_lo: string?
  badge_earned: bool @description("True iff partial_credit_pct >= 80")
}

class GaelQuestPack {
  id: string
  subject: string @description("Always 'gaeilge'")
  framework: string @description("'ncca-lc' or 'ncca-jc'")
  level: GaelNCCALevel
  title: GaelBilingualText
  description: GaelBilingualText
  total_items: int
  total_marks: int
  est_time_minutes: int
  los_covered: string[]
  items: GaelFormativeItem[]
  prerequisites: string[]
  cross_subject_links: string[] @description("LC-ENGL, LC-HIST for cross-language synthesis")
  generated_at: string
  generated_by: string @description("Always 'gael_agent'")
}

class GaelQuestPackValidation {
  pack_id: string
  is_valid: bool
  errors: string[]
  warnings: string[]
}

function GenerateGaelQuestPack(
  syllabus: LeavingCertSyllabus,
  past_papers: LeavingCertPastPaper[],
  marking_schemes: LeavingCertMarkingScheme[],
  level: string
) -> GaelQuestPack {
  client ExtractEnStrong
  prompt #"
    You are an Irish Leaving Certificate Gaeilge expert. Build a
    formative assessment quest pack for NCCA Gaeilge at the {{ level }}
    level.

    Gaeilge is taught in IRISH. All content is canonical in Irish
    (text_ga); text_en may be null for native comprehension items
    but should be provided as a helper translation for the student
    when useful.

    3 NCCA levels (FL / OL / HL) plus Junior Cycle. Cover ALL
    learning outcomes with ≥1 FormativeItem each. Reference the
    source NCCA PDF page in each item's evidence. Order items by
    difficulty (1 → 5).

    Cross-subject links: suggest bridges to English (LC-ENGL-LO-*)
    for translation exercises, and to History (LC-HIST-LO-*) for
    cultural-context synthesis.

    Syllabus: {{ syllabus }}
    Past papers: {{ past_papers }}
    Marking schemes: {{ marking_schemes }}

    {{ ctx.output_format }}
  "#
}

function ExtractGaelLOStatement(paragraph: string) -> string[] {
  client ExtractEn
  prompt #"
    Extract all Gaeilge learning outcome statements from the
    following NCCA syllabus paragraph. Return them as a list of
    full Irish statements (verbatim from the source, with the LO
    code if present).

    Paragraph: {{ paragraph }}

    {{ ctx.output_format }}
  "#
}

function GenerateGaelFormativeItem(
  lo_code: string,
  difficulty: int,
  level: string,
  topic: string
) -> GaelFormativeItem {
  client ExtractEnStrong
  prompt #"
    Generate a single formative assessment item for the NCCA Leaving
    Certificate (or Junior Cycle) Gaeilge learning outcome
    {{ lo_code }}.

    Difficulty: {{ difficulty }} (1-5)
    Level: {{ level }} (JC / LC_FL / LC_OL / LC_HL)
    Topic: {{ topic }}

    All content MUST be canonical in Irish (text_ga required);
    text_en may be null for native comprehension items but should
    be a helper translation when useful for the student.

    Include 4 graduated hints (Irish canonical), ≥2 common student
    errors, evidence.source_page, est_time_minutes between 1-30.

    Use the gael_tutor feedback channel by default.

    {{ ctx.output_format }}
  "#
}

function ScoreGaelFormativeResponse(
  item: GaelFormativeItem,
  attempt: GaelFormativeItemAttempt
) -> GaelScoreBreakdown {
  client ExtractEnStrong
  prompt #"
    Score the following student attempt at the Gaeilge formative
    item. The student wrote their response in Irish.

    Item: {{ item }}
    Attempt: {{ attempt }}

    Compute total_marks, marks_awarded, marks_per_step, is_correct,
    partial_credit_pct, feedback_ga (Irish canonical) +
    feedback_en (optional helper translation), next_recommended_lo,
    badge_earned (true iff partial_credit_pct >= 80).

    The feedback MUST be in Irish (feedback_ga canonical).
    feedback_en is optional and only needed if it adds pedagogical
    value (e.g. for a parent or non-Irish-speaking teacher).

    {{ ctx.output_format }}
  "#
}

function ValidateGaelQuestPack(pack: GaelQuestPack) -> GaelQuestPackValidation {
  client ExtractEn
  prompt #"
    Validate the Gaeilge quest pack. Check:
    - All items reference valid LC-GAEL-LO-* or JC-GAEL-LO-* codes
    - All items have text_ga populated (text_ga is REQUIRED for Gaeilge)
    - text_en may be null but not all items should be null
    - Each item's est_time_minutes is within [1, 30]

    Pack: {{ pack }}

    {{ ctx.output_format }}
  "#
}