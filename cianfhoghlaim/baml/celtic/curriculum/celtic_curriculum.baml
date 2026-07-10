// Celtic Curriculum Extraction Schemas
// Extract structured data from Celtic language curriculum documents

enum CelticLanguageCurriculum {
  IRISH
  SCOTTISH_GAELIC
  WELSH
  MANX
  CORNISH
  BRETON
}

enum EducationLevelCeltic {
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

class CelticLearningOutcome {
  id: string @description("Unique identifier")
  description: string @description("What the learner will achieve")
  skill_domains SkillDomain[] @description("Skills developed")
  prerequisites: string[] @description("Prior knowledge required")
  assessable: bool @description("Can be formally assessed")
}

class GrammarTopic {
  name: string @description("Grammar topic name")
  native_term: string? @description("Term in target language")
  description: string @description("Explanation of the concept")
  examples CelticExample[] @description("Usage examples")
  difficulty: int @description("1-5 difficulty scale")
  common_errors: string[] @description("Mistakes learners often make")
  @@stream.done
}

class CelticExample {
  celtic_text: string @description("Text in Celtic language")
  english_translation: string @description("English meaning")
  pronunciation: string? @description("IPA or guide")
  grammatical_notes: string? @description("Grammar explanation")
}

class VocabularySet {
  theme: string @description("Vocabulary theme")
  words CelticWord[] @description("Words in the set")
  cultural_context: string? @description("Cultural background")
  @@stream.done
}

class CelticWord {
  word: string @description("Word in Celtic language")
  pronunciation: string? @description("How to pronounce")
  translations: string[] @description("English meanings")
  part_of_speech: string @description("noun, verb, adjective, etc.")
  gender: string? @description("Grammatical gender if applicable")
  plural: string? @description("Plural form")
  mutations: string[] @description("Initial mutations")
  example_sentence CelticExample? @description("Example usage")
}

class CurriculumUnit {
  title: string @description("Unit title")
  language CelticLanguageCurriculum @description("Target language")
  level EducationLevelCeltic @description("Education level")
  grade_year: string? @description("Specific grade/year")
  nation: string @description("Country of origin")

  learning_outcomes CelticLearningOutcome[] @description("Unit outcomes")
  grammar_topics GrammarTopic[] @description("Grammar covered")
  vocabulary VocabularySet[] @description("Vocabulary themes")

  cultural_content: string[] @description("Cultural elements")
  assessment_criteria: string[] @description("How to assess")
  resources: string[] @description("Suggested resources")
  @@stream.done
}

// Extract curriculum unit from document
function ExtractCurriculumUnit(document: string, language: CelticLanguageCurriculum, nation: string) -> CurriculumUnit {
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
function ExtractGrammarTopic(content: string, language: CelticLanguageCurriculum) -> GrammarTopic {
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
function ExtractVocabulary(text: string, language: CelticLanguageCurriculum, theme: string?) -> VocabularySet {
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
  outcome CelticLearningOutcome
  assessment_type: string @description("quiz, oral, written, project")
  questions AssessmentQuestion[]
  rubric: string[] @description("Grading criteria")
}

class AssessmentQuestion {
  question_text: string
  celtic_content: string? @description("Celtic language in question")
  question_type: string @description("multiple_choice, fill_blank, translation, oral")
  correct_answer: string
  distractors: string[]? @description("Wrong answers for MC")
  points: int
  skill_tested SkillDomain
}

function GenerateAssessment(
  outcome: CelticLearningOutcome,
  language: CelticLanguageCurriculum,
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
  topic: string
  nations: string[]
  similarities: string[]
  differences: string[]
  linguistic_connections: string[] @description("Shared Celtic features")
  recommendations: string[] @description("Cross-curriculum opportunities")
}

function CompareCelticCurricula(
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

// ============================================================================
// Cross-nation curriculum comparison
// Promoted from spaces/_common/baml/hackathon_schemas.baml (2026-06-24).
// Used by:
//   - spaces/meaisin_cliste/curaclam.py (the Curaclam Trasteorann panel)
//   - tuatha/cognify_rules/author_archive_cross_corpus.py (the cross-corpus KG)
// ============================================================================

class CurriculumMapping {
  nation_code string  // "IE" | "NI" | "WLS" | "IM" | "SCT" | "COR" | "BRT"
  nation_name_en string
  nation_name_native string
  curriculum_body string  // e.g. "NCCA", "CCEA", "WJEC", "SQA"
  topic_label_en string
  topic_label_native string?
  year_level string
  topic_code string?  // official code if available
  similar_topics string[]  // topic_codes in other nations
}

class CelticCurriculumComparison {
  topic_query string
  mappings CurriculumMapping[]
  shared_year_levels string[]
  notes string
}

function CompareCelticNations(
  topic_query: string,
  scope: string[] = ["IE", "NI", "WLS", "IM", "SCT"],
) -> CelticCurriculumComparison {
  client LitellmClient
  prompt #"
    The user wants to know how "{{ topic_query }}" is taught across
    these Celtic-nation curricula: {{ scope }}.

    For each nation, return:
      - nation_code, nation_name_en, nation_name_native
      - curriculum_body (e.g. "NCCA" for ROI, "CCEA" for NI, etc.)
      - topic_label_en, topic_label_native (if not English)
      - year_level (e.g. "Senior Cycle", "A-Level", "Higher")
      - topic_code (the official code if known)
      - similar_topics: topic_codes from other nations that map

    Also produce:
      - shared_year_levels: the union of year_levels across nations
      - notes: a 1-2 sentence explanation of the cross-jurisdiction
        mapping (note any equivalences or divergences)
  "#
}
