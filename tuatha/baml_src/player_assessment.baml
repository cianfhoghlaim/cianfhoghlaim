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
  vocabulary_notes VocabularyNote[]

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

class VocabularyNote {
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
  client CelticContentFallback
  prompt #"
    Analyze this player's Celtic language response in an educational game context.

    Player Response: {{ player_response }}
    {% if expected_response %}Expected Response: {{ expected_response }}{% endif %}
    Context: {{ context }}
    Language: {{ language }}
    Skill Being Tested: {{ skill_being_tested }}

    Provide detailed analysis including:
    - Whether the response is correct (be lenient for minor spelling variations)
    - Specific spelling errors with Celtic language rules
    - Grammar errors with clear explanations
    - Encouraging, constructive feedback
    - Feedback in the target language for immersion

    Remember this is a game - be encouraging while educational.

    {{ ctx.output_format }}
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
  client CelticContentFallback
  prompt #"
    Generate an adaptive language assessment for this player.

    Player Profile:
    - Language: {{ player_profile.language }}
    - Current Level: {{ player_profile.overall_level }}
    - Strengths: {{ player_profile.strengths }}
    - Areas to Improve: {{ player_profile.areas_for_improvement }}

    Focus Areas: {{ focus_areas }}
    Number of Questions: {{ question_count }}

    Create questions that:
    - Start at the player's current level
    - Mix question types (translation, fill_blank, etc.)
    - Focus on identified weak areas
    - Include some review of strengths
    - Progress in difficulty
    - Are engaging and game-appropriate

    {{ ctx.output_format }}
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
  responses PlacementResponse[],
  language: CelticLanguage
) -> PlacementResult {
  client Claude
  prompt #"
    Evaluate this Celtic language placement test to determine player's starting level.

    Language: {{ language }}

    Responses:
    {% for response in responses %}
    Question: {{ response.question }}
    Player Answer: {{ response.answer }}
    Correct Answer: {{ response.correct_answer }}
    Skill Tested: {{ response.skill }}
    Difficulty: {{ response.difficulty }}
    {% endfor %}

    Determine:
    - Overall proficiency level (CEFR A1-C2)
    - Skill-by-skill breakdown
    - Known vocabulary and grammar
    - Appropriate starting zone in game
    - First quests suited to level
    - Personalized learning tips

    Be encouraging - even beginners should feel welcome!

    {{ ctx.output_format }}
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
  activity_data: map<string, any>,
  language: CelticLanguage,
  period: string
) -> ProgressReport {
  client CelticContentFallback
  prompt #"
    Generate an encouraging progress report for this Celtic language learner.

    Player ID: {{ player_id }}
    Language: {{ language }}
    Period: {{ period }}

    Activity Data:
    {{ activity_data }}

    Create a report that:
    - Celebrates achievements and progress
    - Includes a summary in the target Celtic language
    - Identifies areas of improvement
    - Sets achievable next goals
    - Provides motivation to continue
    - Uses warm, encouraging tone

    End with a Celtic phrase of encouragement.

    {{ ctx.output_format }}
  "#
}
