// Cognates - Cross-Celtic Vocabulary Comparison
// Extract cognate relationships across Celtic languages
// December 2024

// ============================================================================
// COGNATE RELATIONSHIPS
// ============================================================================

// A set of cognate words across Celtic languages
class CognateSet {
  concept: string @description("The shared meaning in English")
  proto_celtic: string? @description("Reconstructed Proto-Celtic form (*)")

  // Goidelic (Q-Celtic)
  irish: string? @description("Modern Irish form")
  scottish_gaelic: string? @description("Scottish Gaelic form")
  manx: string? @description("Manx form")
  old_irish: string? @description("Old Irish form")

  // Brythonic (P-Celtic)
  welsh: string? @description("Welsh form")
  breton: string? @description("Breton form")
  cornish: string? @description("Cornish form")

  // Non-Celtic cognates
  latin: string? @description("Latin cognate if any")
  english: string? @description("English cognate or loan")

  etymology_notes: string? @description("Notes on etymology and sound changes")
}

// A single cognate pair
class CognatePair {
  concept: string @description("Shared meaning")
  source_language: CelticLanguage @description("Source language")
  source_word: string @description("Word in source language")
  target_language: CelticLanguage @description("Target language")
  target_word: string @description("Word in target language")
  confidence: float @description("Confidence in relationship (0-1)")
  sound_changes: string? @description("Sound changes involved")
}

// Historical sound change
class SoundChange {
  from_stage: string @description("Starting stage (Proto-Celtic, Old Irish, etc.)")
  to_stage: string @description("Ending stage")
  change_description: string @description("Description of the change")
  example: string? @description("Example word showing the change")
  phonetic_environment: string? @description("Where the change occurs")
}

// False friend warning
class FalseFriend {
  language_a: CelticLanguage @description("First language")
  word_a: string @description("Word in first language")
  meaning_a: string @description("Meaning in first language")
  language_b: CelticLanguage @description("Second language")
  word_b: string @description("Similar word in second language")
  meaning_b: string @description("Different meaning")
  warning: string @description("Why this is confusing")
}

// ============================================================================
// KEY SOUND CHANGES
// ============================================================================

// Major Celtic sound changes for reference
enum CelticSoundChange {
  KW_TO_K @alias("*kw > c in Goidelic (quattuor > ceathar)")
  KW_TO_P @alias("*kw > p in Brythonic (quattuor > pedwar)")
  LENITION @alias("Intervocalic lenition of stops")
  NASAL_MUTATION @alias("Assimilation after nasals")
  FINAL_SYLLABLE_LOSS @alias("Loss of final syllables")
  E_TO_I_RAISING @alias("*e > i in certain environments")
  S_TO_H @alias("*s > h (later lost) in Celtic")
  LABIOVELAR_SPLIT @alias("Different reflexes of *gw, *sw")
}

// ============================================================================
// EXTRACTION FUNCTIONS
// ============================================================================

// Identify cognates from a word in context
function IdentifyCognates(  word: string @description("Word to find cognates for"),
  language: CelticLanguage @description("Language of the word"),
  meaning: string? @description("Meaning if known")
) -> CognateSet {
  client: Claude
  prompt #"
    Find cognate words across Celtic languages for this word.

    Word: {{ word }}
    Language: {{ language }}
    {{#if meaning}}Meaning: {{ meaning }}{{/if}}

    Provide cognates in:
    - Goidelic: Irish, Scottish Gaelic, Manx
    - Brythonic: Welsh, Breton, Cornish
    - Also include Old Irish if relevant

    Include:
    - Reconstructed Proto-Celtic form (with *)
    - Notes on sound changes between branches

    Key Goidelic-Brythonic differences:
    - *kw > c (Goidelic) vs p (Brythonic)
    - Different vowel developments
    - Different mutation systems

    {{ ctx.output_format }}
  "#
}

// Compare vocabulary across two Celtic languages
function CompareCelticVocabulary(  text: string @description("Text to analyze for cognates"),
  language_a: CelticLanguage @description("First language"),
  language_b: CelticLanguage @description("Second language to compare")
) -> CognatePair[] {
  client: Claude
  prompt #"
    Analyze this text and find words that have cognates between {{ language_a }} and {{ language_b }}.

    Text: {{ text }}

    For each cognate pair:
    - Identify the source word
    - Give the cognate in the target language
    - Explain the semantic connection
    - Note any sound changes

    Common cognate patterns:
    - Irish "c" ~ Welsh "p" (ceann ~ pen)
    - Irish "mac" ~ Welsh "mab/map"
    - Shared vocabulary for basic concepts (numbers, family, nature)

    {{ ctx.output_format }}
  "#
}

// Identify false friends between Celtic languages
function IdentifyFalseFriends(  word: string @description("Word to check"),
  language_a: CelticLanguage @description("First language"),
  language_b: CelticLanguage @description("Second language")
) -> FalseFriend? {
  client: ClaudeHaiku
  prompt #"
    Check if this word has a false friend (similar form, different meaning) between {{ language_a }} and {{ language_b }}.

    Word: {{ word }}

    A false friend is when two words look/sound similar but have different meanings.

    Examples of Celtic false friends:
    - Irish "tá" (is) vs Welsh "ta" (thank you)
    - Irish "gwyn" doesn't exist, but Welsh "gwyn" means white

    If there is a false friend, explain:
    - What the word means in each language
    - Why it's confusing for learners

    Return null if no false friend exists.

    {{ ctx.output_format }}
  "#
}

// Explain sound changes in a cognate set
function ExplainSoundChanges(  proto_form: string @description("Reconstructed Proto-Celtic form"),
  modern_form: string @description("Modern form in any Celtic language"),
  language: CelticLanguage @description("Language of modern form")
) -> SoundChange[] {
  client: Claude
  prompt #"
    Explain the sound changes from Proto-Celtic to modern {{ language }}.

    Proto-Celtic: {{ proto_form }}
    Modern: {{ modern_form }}

    List each sound change in order:
    1. What changed (e.g., *kw > c)
    2. When/where it happened
    3. The intermediate stages if known

    Key Celtic sound changes:
    - Lenition of intervocalic consonants
    - Loss of final syllables
    - *p loss in Celtic (*pater > athair)
    - Vowel changes and ablaut
    - Palatalization in Goidelic

    {{ ctx.output_format }}
  "#
}

// Generate cognate vocabulary for a semantic field
function GenerateCognateVocabulary(  semantic_field: string @description("Topic: numbers, family, nature, etc."),
  languages: CelticLanguage[] @description("Languages to include")
) -> CognateSet[] {
  client: Claude
  prompt #"
    Generate a comparative vocabulary table for the semantic field: {{ semantic_field }}

    Include these languages: {{ languages }}

    Provide 10-15 key terms in the semantic field, with:
    - The concept/meaning
    - Word in each requested language
    - Proto-Celtic reconstruction if known
    - Notes on interesting developments

    Semantic fields to consider:
    - Numbers (1-10, 20, 100)
    - Family (mother, father, son, daughter)
    - Body parts (head, hand, foot, eye)
    - Nature (water, fire, sun, moon)
    - Animals (horse, dog, pig, cow)
    - Basic verbs (be, go, do, say)

    {{ ctx.output_format }}
  "#
}
