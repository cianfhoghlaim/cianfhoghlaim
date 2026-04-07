// Celtic Curriculum Extraction Schemas
// Extract structured data from Celtic language curriculum documents

enum CelticLanguage {
  IRISH
  SCOTTISH_GAELIC
  WELSH
  MANX
  CORNISH
  BRETON
}

enum EducationLevel {
  PRIMARY
  SECONDARY
  HIGHER
}

enum SkillDomain {
  LISTENING
  SPEAKING
  READING
  WRITING
  GRAMMAR
  VOCABULARY
  CULTURE
}

class LearningOutcome {
  id string @description("Unique identifier")
  description string @description("What the learner will achieve")
  skill_domains SkillDomain[] @description("Skills developed")
  prerequisites string[] @description("Prior knowledge required")
  assessable bool @description("Can be formally assessed")
}

class GrammarTopic {
  name string @description("Grammar topic name")
  native_term string? @description("Term in target language")
  description string @description("Explanation of the concept")
  examples CelticExample[] @description("Usage examples")
  difficulty int @description("1-5 difficulty scale")
  common_errors string[] @description("Mistakes learners often make")
}

class CelticExample {
  celtic_text string @description("Text in Celtic language")
  english_translation string @description("English meaning")
  pronunciation string? @description("IPA or guide")
  grammatical_notes string? @description("Grammar explanation")
}

class VocabularySet {
  theme string @description("Vocabulary theme")
  words CelticWord[] @description("Words in the set")
  cultural_context string? @description("Cultural background")
}

class CelticWord {
  word string @description("Word in Celtic language")
  pronunciation string? @description("How to pronounce")
  translations string[] @description("English meanings")
  part_of_speech string @description("noun, verb, adjective, etc.")
  gender string? @description("Grammatical gender if applicable")
  plural string? @description("Plural form")
  mutations string[] @description("Initial mutations")
  example_sentence CelticExample? @description("Example usage")
}

class CurriculumUnit {
  title string @description("Unit title")
  language CelticLanguage @description("Target language")
  level EducationLevel @description("Education level")
  grade_year string? @description("Specific grade/year")
  nation string @description("Country of origin")

  learning_outcomes LearningOutcome[] @description("Unit outcomes")
  grammar_topics GrammarTopic[] @description("Grammar covered")
  vocabulary VocabularySet[] @description("Vocabulary themes")

  cultural_content string[] @description("Cultural elements")
  assessment_criteria string[] @description("How to assess")
  resources string[] @description("Suggested resources")
}

// Extract curriculum unit from document
function ExtractCurriculumUnit(document: string, language: CelticLanguage, nation: string) -> CurriculumUnit {
  client CelticContentFallback
  prompt #"
    Extract structured curriculum information from this Celtic language education document.

    Target Language: {{ language }}
    Nation: {{ nation }}

    Document:
    {{ document }}

    Extract all learning outcomes, grammar topics, vocabulary, and cultural content.
    Ensure Celtic text is accurately transcribed with proper diacritics.

    {{ ctx.output_format }}
  "#
}

// Extract grammar explanation
function ExtractGrammarTopic(content: string, language: CelticLanguage) -> GrammarTopic {
  client CelticContentFallback
  prompt #"
    Extract a structured grammar explanation from this Celtic language content.

    Language: {{ language }}

    Content:
    {{ content }}

    Provide clear examples with translations and note common learner errors.

    {{ ctx.output_format }}
  "#
}

// Extract vocabulary from text
function ExtractVocabulary(text: string, language: CelticLanguage, theme: string?) -> VocabularySet {
  client FastExtraction
  prompt #"
    Extract vocabulary from this Celtic language text.

    Language: {{ language }}
    Theme: {{ theme ?? "general" }}

    Text:
    {{ text }}

    Include pronunciation guides and grammatical information.

    {{ ctx.output_format }}
  "#
}

// Generate learning outcome assessment
class OutcomeAssessment {
  outcome LearningOutcome
  assessment_type string @description("quiz, oral, written, project")
  questions AssessmentQuestion[]
  rubric string[] @description("Grading criteria")
}

class AssessmentQuestion {
  question_text string
  celtic_content string? @description("Celtic language in question")
  question_type string @description("multiple_choice, fill_blank, translation, oral")
  correct_answer string
  distractors string[]? @description("Wrong answers for MC")
  points int
  skill_tested SkillDomain
}

function GenerateAssessment(
  outcome: LearningOutcome,
  language: CelticLanguage,
  question_count: int
) -> OutcomeAssessment {
  client CelticContentFallback
  prompt #"
    Generate an assessment for this Celtic language learning outcome.

    Language: {{ language }}
    Outcome: {{ outcome.description }}
    Number of questions: {{ question_count }}

    Create varied question types testing the specified skill domains.
    Include Celtic text with accurate spelling and diacritics.

    {{ ctx.output_format }}
  "#
}

// Compare curriculum across Celtic nations
class CurriculumComparison {
  topic string
  nations string[]
  similarities string[]
  differences string[]
  linguistic_connections string[] @description("Shared Celtic features")
  recommendations string[] @description("Cross-curriculum opportunities")
}

function CompareCurricula(
  topic: string,
  irish_content: string?,
  gaelic_content: string?,
  welsh_content: string?
) -> CurriculumComparison {
  client Claude
  prompt #"
    Compare how this topic is taught across Celtic language curricula.

    Topic: {{ topic }}

    Irish Curriculum:
    {{ irish_content ?? "Not provided" }}

    Scottish Gaelic Curriculum:
    {{ gaelic_content ?? "Not provided" }}

    Welsh Curriculum:
    {{ welsh_content ?? "Not provided" }}

    Identify similarities, differences, and opportunities for cross-Celtic learning.
    Highlight shared linguistic features (cognates, grammar patterns).

    {{ ctx.output_format }}
  "#
}
