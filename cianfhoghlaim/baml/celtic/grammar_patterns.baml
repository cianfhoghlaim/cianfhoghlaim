// === ARCHIVED 2026-06-24 ===
// The 6 functions in this file (ExtractGrammarPatterns,
// ExtractIrishCopula, AnalyzeVSOOrder, ExtractPossession,
// GeneratePrepositionalPronouns, DocumentMutationTriggers) have
// no current Python consumer in the oideachais quadrant. They
// are intended for the meaisinfhoghlaim/ Celtic-linguistic
// agents, which are not yet built.
//
// To re-activate:
// 1. Implement the consumer (e.g.
//    meaisinfhoghlaim/agents/celtic_grammar.py)
// 2. Move this file back to baml_src/ (git mv)
// 3. Remove the ARCHIVED header from the top
// 4. Update STATUS.md to mark the functions as wired
// 5. Update REFACTORING.md to remove the archive entry
//
// Reference: openspec/changes/archive-celtic-baml-orphans/
// =====================================================================

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
  text string @description("Celtic language text"),
  language CelticLanguage @description("Language of the text")
) -> GrammarPattern[] {
  client Claude
  prompt #"
    Identify grammatical patterns in this {{ language }} text.

    Text: {{ text }}

    Look for:
    1. VSO word order - verb before subject
    2. Copula constructions - is/tá in Irish
    3. Prepositional pronouns - agam, agat, orm, etc.
    4. Initial mutations triggered by particles/articles
    5. Genitive constructions - noun + noun
    6. Verbal noun constructions - ag + verbal noun
    7. Cleft sentences - Is é X a rinne Y
    8. Relative clauses - with 'a' particle

    For each pattern provide:
    - Type of pattern
    - Example from the text
    - English translation
    - Structural description

    {{ ctx.output_format }}
  "#
}

// Analyze Irish copula usage
function ExtractIrishCopula(
  sentence string @description("Irish sentence possibly containing copula")
) -> IrishCopulaPattern? {
  client Claude
  prompt #"
    Analyze the copula usage in this Irish sentence.

    Sentence: {{ sentence }}

    Irish has two copulas:
    1. IS - for identification, classification, emphasis
       - Is múinteoir mé (I am a teacher)
       - Is í Máire an múinteoir (Mary is the teacher)
       - Is é Seán a rinne é (It was Seán who did it)

    2. TÁ (not a copula, but existential/locative 'bí')
       - Tá mé go maith (I am well)
       - Tá mé sa bhaile (I am at home)
       - Tá teach agam (I have a house)

    Determine:
    - Which type of copula construction
    - The form used (is, ba, ní, an, nach, gur, etc.)
    - The predicate and subject
    - Why this form is appropriate

    Return null if no copula pattern is present.

    {{ ctx.output_format }}
  "#
}

// Analyze VSO word order
function AnalyzeVSOOrder(
  sentence string @description("Celtic sentence"),
  language CelticLanguage @description("Language")
) -> VSOPattern {
  client Claude
  prompt #"
    Analyze the VSO (Verb-Subject-Object) word order in this {{ language }} sentence.

    Sentence: {{ sentence }}

    Celtic languages use VSO as their basic word order:
    - Verb comes first
    - Subject follows verb
    - Object follows subject

    Identify:
    - The main verb
    - The subject (may be fused with verb in synthetic forms)
    - The object (if present)
    - Any adverbs, adjuncts, or modifiers

    Note: In Irish, some verb forms include the pronoun (synthetic):
    - Beidh mé (analytic) vs Bead (synthetic: I will be)

    {{ ctx.output_format }}
  "#
}

// Extract possession patterns
function ExtractPossession(
  sentence string @description("Sentence expressing possession")
) -> PossessionPattern {
  client Claude
  prompt #"
    Analyze how possession is expressed in this Irish sentence.

    Sentence: {{ sentence }}

    Irish expresses possession in multiple ways:
    1. Tá X ag Y - Y has X (most common)
       - Tá carr agam = I have a car

    2. Is le Y X - X belongs to Y
       - Is liomsa an leabhar = The book is mine

    3. Mo/do/a + noun - possessive adjective
       - Mo theach = my house

    4. Noun + noun (genitive)
       - Teach Sheáin = Seán's house

    Identify:
    - What is possessed
    - Who possesses it
    - Which construction is used
    - English translation

    {{ ctx.output_format }}
  "#
}

// Generate prepositional pronoun table
function GeneratePrepositionalPronouns(
  preposition string @description("Base preposition"),
  language CelticLanguage @description("Language")
) -> PrepositionalPronoun[] {
  client Claude
  prompt #"
    Generate the full prepositional pronoun paradigm for this {{ language }} preposition.

    Preposition: {{ preposition }}

    Irish prepositional pronouns fuse preposition + personal pronoun:
    - ag (at) → agam, agat, aige, aici, againn, agaibh, acu
    - le (with) → liom, leat, leis, léi, linn, libh, leo
    - ar (on) → orm, ort, air, uirthi, orainn, oraibh, orthu

    Provide all forms:
    - 1st person singular
    - 2nd person singular
    - 3rd person singular masculine
    - 3rd person singular feminine
    - 1st person plural
    - 2nd person plural
    - 3rd person plural

    {{ ctx.output_format }}
  "#
}

// Document mutation triggers
function DocumentMutationTriggers(
  language CelticLanguage @description("Language to document")
) -> MutationTriggerPattern[] {
  client Claude
  prompt #"
    Document the main initial mutation triggers in {{ language }}.

    For Irish, include:
    LENITION (séimhiú) triggers:
    - Feminine singular nouns after 'an'
    - After possessives (mo, do, a [his])
    - Past tense marker 'd'
    - Certain prepositions

    ECLIPSIS (urú) triggers:
    - After 'i' (in)
    - After numbers 7-10
    - After plural 'na'
    - After possessive 'ár, bhur, a [their]'

    For Welsh mutations, include soft, nasal, and aspirate triggers.

    For each trigger provide:
    - What triggers it
    - What mutation type
    - What parts of speech are affected
    - An example
    - Any exceptions

    {{ ctx.output_format }}
  "#
}
