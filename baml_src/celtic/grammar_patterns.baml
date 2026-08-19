
// Grammar Patterns - Celtic Syntactic Structures
// Extract and analyze Celtic-specific grammatical patterns
// December 2024

// ============================================================================
// GRAMMAR PATTERN TYPES
// ============================================================================

// Types of Celtic grammatical patterns
enum GrammarPatternType {
  VSO @alias("Verb-Subject-Object word order")
  COPULA @alias("Copula constructions (is/tá)")
  PREPOSITIONAL_PRONOUN @alias("Fused preposition+pronoun")
  MUTATION_TRIGGER @alias("Initial mutation trigger")
  GENITIVE_PHRASE @alias("Genitive noun phrase")
  VERBAL_NOUN @alias("Verbal noun construction")
  CLEFT @alias("Cleft sentence")
  RELATIVE @alias("Relative clause")
  POSSESSION @alias("Possession expression")
  PROGRESSIVE @alias("Progressive aspect")
}

// Irish copula pattern types
enum IrishCopulaType {
  IS_IDENTIFICATION @alias("Is múinteoir mé - I am a teacher (classification)")
  IS_CLASSIFICATION @alias("Is duine deas é - He is a nice person")
  IS_EMPHASIS @alias("Is é Seán a rinne é - It was Seán who did it")
  TA_STATE @alias("Tá mé go maith - I am well (state)")
  TA_LOCATION @alias("Tá mé sa bhaile - I am at home (location)")
  TA_POSSESSION @alias("Tá teach agam - I have a house")
}

// ============================================================================
// GRAMMAR PATTERN CLASSES
// ============================================================================

// A grammatical pattern instance
class GrammarPattern {
  pattern_type GrammarPatternType @description("Type of pattern")
  example_sentence string @description("Example sentence")
  translation string @description("English translation")
  structure string @description("Structural description")
  language CelticLanguage @description("Language")
  notes string? @description("Usage notes")
  @@stream.done
}

// Irish copula pattern analysis
class IrishCopulaPattern {
  sentence string @description("The sentence")
  copula_type IrishCopulaType @description("Type of copula usage")
  copula_form string @description("Form of copula: is, ba, an, nach, etc.")
  predicate string @description("What follows the copula")
  subject string @description("The subject")
  translation string @description("English translation")
  explanation string @description("Why this form is used")
  @@stream.done
}

// VSO word order analysis
class VSOPattern {
  sentence string @description("The sentence")
  verb string @description("The verb")
  subject string @description("The subject")
  object string? @description("The object if present")
  modifiers string[]? @description("Any modifiers")
  translation string @description("English translation")
}

// Possession expression
class PossessionPattern {
  sentence string @description("The sentence expressing possession")
  possessor string @description("Who possesses")
  possessed string @description("What is possessed")
  construction_type string @description("ag + owner, le + owner, etc.")
  translation string @description("English translation")
  @@stream.done
}

// Prepositional pronoun
class PrepositionalPronoun {
  preposition string @description("Base preposition")
  person int @description("1, 2, or 3")
  number string @description("sing or plur")
  form string @description("The fused form")
  meaning string @description("English meaning")
  examples string[]? @description("Example sentences")
}

// Mutation trigger pattern
class MutationTriggerPattern {
  trigger string @description("What triggers the mutation")
  mutation_type MutationType @description("Type of mutation caused")
  affected_pos string @description("Part of speech affected")
  example string @description("Example")
  exceptions string? @description("Any exceptions")
}

// ============================================================================
// EXTRACTION FUNCTIONS
// ============================================================================

// Extract grammar patterns from text
function ExtractGrammarPatterns(
  text: string @description("Celtic language text"),
  language: CelticLanguage @description("Language of the text")
) -> GrammarPattern[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting Celtic-language grammar patterns from a pedagogical text.

    Source type: markdown pedagogical text

    Extract:
    - language: the Celtic language (ga, cy, gd, br, kw, gv)
    - pattern_name: the name of the grammar pattern (e.g. 'Irish mutations')
    - examples: list of example sentences demonstrating the pattern
    - rules: list of formal rules for the pattern
    - related_patterns: list of cross-references to related patterns

    {% if language == 'ga' %}
    - Capture the 4 Irish mutations (séimhiú + urú + eclipsis + lenition)
    {% elif language == 'cy' %}
    - Capture the Welsh soft + nasal + aspirate mutations
    {% endif %}

    Celtic mutations are the most distinctive feature. Always capture the input → output transformation explicitly.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Analyze Irish copula usage
function ExtractIrishCopula(
  sentence: string @description("Irish sentence possibly containing copula")
) -> IrishCopulaPattern? {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting Celtic-language grammar patterns from a pedagogical text.

    Source type: markdown pedagogical text

    Extract:
    - language: the Celtic language (ga, cy, gd, br, kw, gv)
    - pattern_name: the name of the grammar pattern (e.g. 'Irish mutations')
    - examples: list of example sentences demonstrating the pattern
    - rules: list of formal rules for the pattern
    - related_patterns: list of cross-references to related patterns

    {% if language == 'ga' %}
    - Capture the 4 Irish mutations (séimhiú + urú + eclipsis + lenition)
    {% elif language == 'cy' %}
    - Capture the Welsh soft + nasal + aspirate mutations
    {% endif %}

    Celtic mutations are the most distinctive feature. Always capture the input → output transformation explicitly.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Analyze VSO word order
function AnalyzeVSOOrder(
  sentence: string @description("Celtic sentence"),
  language: CelticLanguage @description("Language")
) -> VSOPattern {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting Celtic-language grammar patterns from a pedagogical text.

    Source type: markdown pedagogical text

    Extract:
    - language: the Celtic language (ga, cy, gd, br, kw, gv)
    - pattern_name: the name of the grammar pattern (e.g. 'Irish mutations')
    - examples: list of example sentences demonstrating the pattern
    - rules: list of formal rules for the pattern
    - related_patterns: list of cross-references to related patterns

    {% if language == 'ga' %}
    - Capture the 4 Irish mutations (séimhiú + urú + eclipsis + lenition)
    {% elif language == 'cy' %}
    - Capture the Welsh soft + nasal + aspirate mutations
    {% endif %}

    Celtic mutations are the most distinctive feature. Always capture the input → output transformation explicitly.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Extract possession patterns
function ExtractPossession(
  sentence: string @description("Sentence expressing possession")
) -> PossessionPattern {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting Celtic-language grammar patterns from a pedagogical text.

    Source type: markdown pedagogical text

    Extract:
    - language: the Celtic language (ga, cy, gd, br, kw, gv)
    - pattern_name: the name of the grammar pattern (e.g. 'Irish mutations')
    - examples: list of example sentences demonstrating the pattern
    - rules: list of formal rules for the pattern
    - related_patterns: list of cross-references to related patterns

    {% if language == 'ga' %}
    - Capture the 4 Irish mutations (séimhiú + urú + eclipsis + lenition)
    {% elif language == 'cy' %}
    - Capture the Welsh soft + nasal + aspirate mutations
    {% endif %}

    Celtic mutations are the most distinctive feature. Always capture the input → output transformation explicitly.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Generate prepositional pronoun table
function GeneratePrepositionalPronouns(
  preposition: string @description("Base preposition"),
  language: CelticLanguage @description("Language")
) -> PrepositionalPronoun[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting Celtic-language grammar patterns from a pedagogical text.

    Source type: markdown pedagogical text

    Extract:
    - language: the Celtic language (ga, cy, gd, br, kw, gv)
    - pattern_name: the name of the grammar pattern (e.g. 'Irish mutations')
    - examples: list of example sentences demonstrating the pattern
    - rules: list of formal rules for the pattern
    - related_patterns: list of cross-references to related patterns

    {% if language == 'ga' %}
    - Capture the 4 Irish mutations (séimhiú + urú + eclipsis + lenition)
    {% elif language == 'cy' %}
    - Capture the Welsh soft + nasal + aspirate mutations
    {% endif %}

    Celtic mutations are the most distinctive feature. Always capture the input → output transformation explicitly.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Document mutation triggers
function DocumentMutationTriggers(
  language: CelticLanguage @description("Language to document")
) -> MutationTriggerPattern[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting Celtic-language grammar patterns from a pedagogical text.

    Source type: markdown pedagogical text

    Extract:
    - language: the Celtic language (ga, cy, gd, br, kw, gv)
    - pattern_name: the name of the grammar pattern (e.g. 'Irish mutations')
    - examples: list of example sentences demonstrating the pattern
    - rules: list of formal rules for the pattern
    - related_patterns: list of cross-references to related patterns

    {% if language == 'ga' %}
    - Capture the 4 Irish mutations (séimhiú + urú + eclipsis + lenition)
    {% elif language == 'cy' %}
    - Capture the Welsh soft + nasal + aspirate mutations
    {% endif %}

    Celtic mutations are the most distinctive feature. Always capture the input → output transformation explicitly.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// ============================================================================
// CANONICAL EXTRACTION FUNCTION (added 2026-07-17 for the gaois-celtic-language-pipeline-v1 change)
// Re-activates the 6 archived grammar functions by providing a canonical
// per-language grammar pattern extraction entrypoint.
// ============================================================================

// A single Celtic grammar pattern extracted from text
class CelticGrammarPattern {
  language CelticLanguageCurriculum @description("Which Celtic language")
  pattern_type GrammarPatternType @description("Type of grammar pattern (VSO, COPULA, etc.)")
  text string @description("The text example in the source language")
  english_translation string @description("English translation")
  grammar_explanation string @description("Detailed grammar explanation")
  example_breakdown string? @description("Word-by-word grammatical analysis")
  difficulty int @description("1-5 difficulty scale")
  common_errors string[] @description("Common learner errors")
}

// Extract grammar patterns from a Celtic-language text. Per-language
// routing via LlamaSwap (Irish → uccix-mistral-24b, others → gemma-4-26B-A4B).
function ExtractCelticGrammar(
  text: string,
  language: CelticLanguageCurriculum,
  max_patterns: int?
) -> CelticGrammarPattern[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert at extracting Celtic-language grammar patterns from a pedagogical text.

    Source type: markdown pedagogical text

    Extract:
    - language: the Celtic language (ga, cy, gd, br, kw, gv)
    - pattern_name: the name of the grammar pattern (e.g. 'Irish mutations')
    - examples: list of example sentences demonstrating the pattern
    - rules: list of formal rules for the pattern
    - related_patterns: list of cross-references to related patterns

    {% if language == 'ga' %}
    - Capture the 4 Irish mutations (séimhiú + urú + eclipsis + lenition)
    {% elif language == 'cy' %}
    - Capture the Welsh soft + nasal + aspirate mutations
    {% endif %}

    Celtic mutations are the most distinctive feature. Always capture the input → output transformation explicitly.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    CelticGrammarPattern[] {}
  }
}
