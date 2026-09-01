// Player Assessment Schemas
// Assess player language proficiency and learning progress

enum ProficiencyLevel {
  A1 @description("Beginner - basic words and phrases")
  A2 @description("Elementary - simple sentences")
  B1 @description("Intermediate - main points of clear text")
  B2 @description("Upper Intermediate - complex text")
  C1 @description("Advanced - implicit meaning")
  C2 @description("Mastery - near-native fluency")
}

enum AssessmentType {
  DIAGNOSTIC @description("Initial placement")
  FORMATIVE @description("Ongoing progress check")
  SUMMATIVE @description("End of unit evaluation")
  ADAPTIVE @description("Difficulty adjusts to responses")
}

class PlayerLanguageProfile {
  player_id string
  language CelticLanguage
  overall_level ProficiencyLevel

  skill_levels SkillAssessment[]
  vocabulary_count int
  grammar_mastery GrammarProgress[]

  strengths string[]
  areas_for_improvement string[]
  recommended_focus string[]

  last_assessment string @description("ISO datetime")
  total_learning_hours float
}

class SkillAssessment {
  skill SkillDomain
  level ProficiencyLevel
  confidence float @description("0-1 assessment confidence")
  recent_performance float @description("Recent success rate")
  examples_correct int
  examples_attempted int
}

class GrammarProgress {
  topic string
  mastery_level float @description("0-1 mastery")
  examples_practiced int
  last_error string?
  next_review string @description("ISO datetime for spaced repetition")
}

// Analyze player response
class ResponseAnalysis {
  player_response string
  expected_response string?
  language CelticLanguage

  is_correct bool
  partial_credit float @description("0-1 for partial correctness")

  spelling_errors SpellingError[]
  grammar_errors GrammarError[]
  vocabulary_notes VocabularyNotePlayer[]

  feedback string @description("Encouraging feedback message")
  celtic_feedback string? @description("Feedback in target language")
  improvement_suggestion string
}

class SpellingError {
  word_written string
  word_expected string
  error_type string @description("accent, lenition, vowel, consonant")
  explanation string
}

class GrammarError {
  error_text string
  correct_text string
  grammar_rule string
  explanation string
  similar_examples string[]
}

class VocabularyNotePlayer {
  word string
  note_type string @description("new, review, mastered")
  definition string
  usage_note string?
}

function AnalyzePlayerResponse(
  player_response: string,
  expected_response: string?,
  context: string,
  language: CelticLanguage,
  skill_being_tested: SkillDomain
) -> ResponseAnalysis {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

// Generate adaptive assessment
class AdaptiveAssessment {
  assessment_id string
  player_id string
  language CelticLanguage
  assessment_type AssessmentType

  questions AdaptiveQuestion[]
  current_difficulty float @description("0-1 difficulty")
  estimated_level ProficiencyLevel

  started_at string
  time_limit_minutes int?
}

class AdaptiveQuestion {
  question_id string
  question_type string @description("translation, fill_blank, listening, speaking")
  difficulty float

  prompt string @description("Question in English")
  celtic_prompt string? @description("Question in Celtic if applicable")

  celtic_content string @description("The Celtic text involved")
  english_content string @description("English equivalent")

  options string[]? @description("For multiple choice")
  correct_answer string
  grammar_focus string?
  vocabulary_focus string[]

  hint string?
  explanation string @description("For after answering")
}

function GenerateAdaptiveAssessment(
  player_profile: PlayerLanguageProfile,
  focus_areas: SkillDomain[],
  question_count: int
) -> AdaptiveAssessment {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

// Placement test
class PlacementResult {
  player_id string
  language CelticLanguage

  recommended_level ProficiencyLevel
  confidence float

  skill_breakdown SkillAssessment[]
  known_vocabulary string[]
  grammar_familiar GrammarTopic[]

  starting_zone string @description("Recommended game zone")
  starting_quests string[] @description("Recommended first quests")
  personalized_tips string[]
}

function EvaluatePlacementTest(
  responses: PlacementResponse[],
  language: CelticLanguage
) -> PlacementResult {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

class PlacementResponse {
  question string
  answer string
  correct_answer string
  skill SkillDomain
  difficulty float
}

// Progress report
class ProgressReport {
  player_id string
  period string @description("weekly, monthly, etc.")
  language CelticLanguage

  summary string @description("Natural language summary")
  celtic_summary string? @description("Summary in target language")

  statistics ProgressStatistics
  achievements string[]
  vocabulary_learned VocabularyProgress[]
  grammar_improved GrammarProgress[]

  recommendations string[]
  next_goals string[]
  motivational_message string
  celtic_encouragement string
}

class ProgressStatistics {
  quests_completed int
  xp_earned int
  time_played_hours float
  conversations_had int
  words_learned int
  accuracy_rate float
  streak_days int
}

class VocabularyProgress {
  word string
  translation string
  times_practiced int
  mastery_level float
  last_seen string
}

function GenerateProgressReport(
  player_id: string,
  activity_data: map<string, string>,
  language: CelticLanguage,
  period: string
) -> ProgressReport {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}

// ============================================================================
// Bilingual EN+GA exit cards for formative assessment
// Promoted from spaces/_common/baml/hackathon_schemas.baml (2026-06-24).
// Used by:
//   - spaces/anam_tuatha/mac_leinn.py (the Mac Léinn panel)
//   - tuatha/agents/agno/formative_assessment_team.py
// ============================================================================

class ExitCardQuestion {
  question_id string
  prompt_en string
  prompt_ga string
  question_type string  // "multiple_choice" | "short_answer" | "numeric"
  correct_answer string
  explanation_en string
  explanation_ga string
  bloom_level string  // "remember" | "understand" | "apply" | "analyze" | "evaluate" | "create"
  marking_point_ref string?  // e.g. "CH1.T3" — links back to the circular
}

class ExitCardSet {
  lesson_topic string
  subject string
  level string
  questions ExitCardQuestion[]
  total_questions int
  estimated_completion_min int
}

function GenerateExitCardQuestions(
  lesson_topic: string,
  subject: string,
  level: string,
  num_questions: int,
  curriculum_extract: CircularExtraction?
) -> ExitCardSet {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
