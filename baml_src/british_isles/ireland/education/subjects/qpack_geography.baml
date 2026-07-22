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

function GenerateGeogQuestPack(syllabus: LeavingCertSyllabus, past_papers: PastPaper[], marking_schemes: MarkingSchemeSec[], level: string) -> GeogQuestPack {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractGeogLOStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// -----------------------------------------------------------------------------
// ExtractGeogGaStatement (added 2026-07-13-baml-cocoindex-tutorials-ga-v1)
// -----------------------------------------------------------------------------
// The bilingual EN+GA variant of ExtractGeogLOStatement. Same
// return shape; routes via `client Default`; the prompt asks for
// the Irish (Gaeilge) statements verbatim with a leading '[EN-only]'
// fallback marker for LOs the NCCA did not translate.

function ExtractGeogGaStatement(paragraph: string) -> string[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function GenerateGeogFormativeItem(lo_code: string, difficulty: int, level: string, topic: string) -> GeogFormativeItem {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ScoreGeogFormativeResponse(item: GeogFormativeItem, attempt: GeogFormativeItemAttempt) -> GeogScoreBreakdown {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ValidateGeogQuestPack(pack: GeogQuestPack) -> GeogQuestPackValidation {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}