// Morphological Extraction - Verb and Noun Paradigms
// Full conjugation and declension extraction for Celtic languages
// December 2024

// ============================================================================
// VERB CONJUGATION
// ============================================================================

// Irish verb conjugation class
enum VerbConjugationClass {
  FIRST @alias("First Conjugation (-igh verbs, short stems)")
  SECOND @alias("Second Conjugation (-aigh/-igh verbs, polysyllabic)")
  IRREGULAR @alias("Irregular verbs (11 common verbs)")
}

// A single conjugated verb form
class VerbForm {
  person int @description("1, 2, or 3")
  number string @description("sing or plur")
  form string @description("The conjugated form")
  mutation MutationType? @description("Mutation on the form")
  is_autonomous bool @description("Is this the autonomous form?")
}

// Complete verb conjugation paradigm
class VerbConjugation {
  infinitive string @description("Infinitive / citation form")
  language CelticLanguage @description("Language of the verb")
  verb_stem string? @description("The verb stem")
  conjugation_class VerbConjugationClass? @description("Conjugation class")

  verbal_noun string? @description("Ainm briathartha (Irish)")
  verbal_adjective string? @description("Aidiacht bhriathartha (Irish)")

  // Present tense
  present_1sg string? @description("1st person singular present")
  present_2sg string? @description("2nd person singular present")
  present_3sg string? @description("3rd person singular present")
  present_1pl string? @description("1st person plural present")
  present_2pl string? @description("2nd person plural present")
  present_3pl string? @description("3rd person plural present")
  present_auto string? @description("Autonomous present")

  // Past tense
  past_1sg string? @description("1st person singular past")
  past_2sg string? @description("2nd person singular past")
  past_3sg string? @description("3rd person singular past")
  past_1pl string? @description("1st person plural past")
  past_2pl string? @description("2nd person plural past")
  past_3pl string? @description("3rd person plural past")
  past_auto string? @description("Autonomous past")

  // Future tense
  future_1sg string? @description("1st person singular future")
  future_2sg string? @description("2nd person singular future")
  future_3sg string? @description("3rd person singular future")
  future_1pl string? @description("1st person plural future")
  future_2pl string? @description("2nd person plural future")
  future_3pl string? @description("3rd person plural future")
  future_auto string? @description("Autonomous future")

  // Conditional
  conditional_1sg string? @description("1st person singular conditional")
  conditional_2sg string? @description("2nd person singular conditional")
  conditional_3sg string? @description("3rd person singular conditional")
  conditional_1pl string? @description("1st person plural conditional")
  conditional_2pl string? @description("2nd person plural conditional")
  conditional_3pl string? @description("3rd person plural conditional")
  conditional_auto string? @description("Autonomous conditional")

  // Imperative
  imperative_2sg string? @description("2nd person singular imperative")
  imperative_3sg string? @description("3rd person singular imperative")
  imperative_1pl string? @description("1st person plural imperative")
  imperative_2pl string? @description("2nd person plural imperative")
  imperative_3pl string? @description("3rd person plural imperative")
  imperative_auto string? @description("Autonomous imperative")
  @@stream.done
}

// ============================================================================
// NOUN DECLENSION
// ============================================================================

// Irish noun declension class
enum NounDeclensionClass {
  FIRST @alias("First Declension - masculine ending in consonant")
  SECOND @alias("Second Declension - feminine ending in consonant")
  THIRD @alias("Third Declension - ending in -acht, -úint, etc.")
  FOURTH @alias("Fourth Declension - ending in vowel")
  FIFTH @alias("Fifth Declension - irregular, mostly feminine")
}

// Complete noun declension paradigm
class NounDeclension {
  lemma string @description("Citation form (nominative singular)")
  language CelticLanguage @description("Language of the noun")
  gender GrammaticalGender @description("Grammatical gender")
  declension_class NounDeclensionClass? @description("Declension class")

  // Singular forms
  nom_sg string @description("Nominative singular")
  gen_sg string? @description("Genitive singular")
  voc_sg string? @description("Vocative singular")
  dat_sg string? @description("Dative singular (archaic)")

  // Plural forms
  nom_pl string? @description("Nominative plural")
  gen_pl string? @description("Genitive plural")
  voc_pl string? @description("Vocative plural")
  dat_pl string? @description("Dative plural (archaic)")

  // Notes
  plural_type string? @description("How plural is formed: strong, weak, irregular")
  notes string? @description("Special notes about this noun")
  @@stream.done
}

// ============================================================================
// ADJECTIVE FORMS
// ============================================================================

// Adjective comparison forms
class AdjectiveComparison {
  positive string @description("Positive degree")
  comparative string @description("Comparative degree")
  superlative string @description("Superlative degree")
  language CelticLanguage @description("Language")
}

// ============================================================================
// EXTRACTION FUNCTIONS
// ============================================================================

// Extract full verb conjugation
function ExtractVerbConjugation(
  verb: string @description("Verb infinitive or any form"),
  language: CelticLanguage @description("Language of the verb")
) -> VerbConjugation {
  client Claude
  prompt #"
    Generate the complete conjugation paradigm for this Celtic verb.

    Verb: {{ verb }}
    Language: {{ language }}

    Provide all forms for:
    - Present tense (all persons + autonomous)
    - Past tense (all persons + autonomous)
    - Future tense (all persons + autonomous)
    - Conditional (all persons + autonomous)
    - Imperative (all persons)
    - Verbal noun and verbal adjective

    For Irish, note:
    - First conjugation: short stems, regular endings
    - Second conjugation: polysyllabic, syncopation
    - Irregular verbs: bí, abair, beir, clois, déan, faigh, feic, ith, tabhair, tar, téigh

    {{ ctx.output_format }}
  "#
}

// Extract noun declension
function ExtractNounDeclension(
  noun: string @description("Noun in any form"),
  language: CelticLanguage @description("Language of the noun")
) -> NounDeclension {
  client Claude
  prompt #"
    Generate the complete declension paradigm for this Celtic noun.

    Noun: {{ noun }}
    Language: {{ language }}

    Provide:
    - Gender (masculine/feminine)
    - Declension class
    - All case forms (nominative, genitive, vocative, dative if applicable)
    - Singular and plural forms

    For Irish, note:
    - First declension: masculine, ends in consonant (fear -> fir)
    - Second declension: feminine, ends in consonant (cos -> coise)
    - Third declension: mostly feminine, -(e)acht (bliain -> bliana)
    - Fourth declension: ends in vowel (dalta -> daltaí)
    - Fifth declension: irregular feminines (bean -> mná)

    {{ ctx.output_format }}
  "#
}

// Identify conjugation/declension class
function IdentifyMorphologicalClass(
  word: string @description("Word to classify"),
  pos: PartOfSpeech @description("Part of speech"),
  language: CelticLanguage @description("Language")
) -> string {
  client ClaudeHaiku
  prompt #"
    Identify the morphological class of this {{ language }} {{ pos }}.

    Word: {{ word }}

    For verbs, identify:
    - First or Second conjugation
    - Whether it's irregular

    For nouns, identify:
    - First through Fifth declension
    - Gender

    Return the class name (e.g., "First Declension, Masculine" or "Second Conjugation").

    {{ ctx.output_format }}
  "#
}

// Compare adjectives
function CompareAdjective(
  adjective: string @description("Adjective in positive form"),
  language: CelticLanguage @description("Language")
) -> AdjectiveComparison {
  client ClaudeHaiku
  prompt #"
    Provide the comparison forms for this {{ language }} adjective.

    Adjective: {{ adjective }}

    For Irish adjectives:
    - Comparative: níos + adjective (or irregular form)
    - Superlative: is + adjective (or irregular form)

    Examples:
    - mór -> níos mó -> is mó
    - beag -> níos lú -> is lú
    - maith -> níos fearr -> is fearr

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// CANONICAL EXTRACTION FUNCTION (added 2026-07-17 for the gaois-celtic-language-pipeline-v1 change)
// Re-activates the 4 archived morphology functions by providing a canonical
// per-language morphology extraction entrypoint.
// ============================================================================

// Morphological specification for a Celtic-language word
class CelticMorphologySpec {
  language CelticLanguageCurriculum @description("Which Celtic language")
  word string @description("The word being analysed")
  word_class string @description("Part of speech: noun, verb, adjective, etc.")
  inflection_class string @description("Conjugation/declension class")
  paradigm CelticForm[] @description("Full paradigm (all forms)")
  morphology_notes string @description("Detailed morphology notes")
  related_words string[] @description("Cognates or related forms in other Celtic languages")
  difficulty int @description("1-5 difficulty scale")
}

// A single inflected form within a paradigm
class CelticForm {
  form string @description("The inflected form")
  features string[] @description("Morphological features: case, number, person, tense, etc.")
  ipa_pronunciation string? @description("IPA pronunciation guide")
  mutation MutationType? @description("Initial mutation if any")
  notes string? @description("Notes about this specific form")
}

// Extract morphology from a Celtic-language word or text. Per-language
// routing via LlamaSwap (Irish → uccix-mistral-24b, others → gemma-4-26B-A4B).
function ExtractCelticMorphology(
  text: string,
  language: CelticLanguageCurriculum,
  word_class_hint: string?
) -> CelticMorphologySpec[] {
  client LlamaSwapReasoningClient
  prompt #"
    Extract morphology from this {{ language }} text.

    {{ ctx.output_format }}

    Text:
    {{ text }}

    {% if word_class_hint %}
    Focus on: {{ word_class_hint }} words
    {% endif %}

    For each significant word (nouns, verbs, adjectives), identify:
    - The word being analysed
    - The word class (noun, verb, adjective, etc.)
    - The inflection class (1st/2nd conjugation for verbs; 1st/2nd/3rd/5th declension for nouns)
    - The full paradigm (all inflected forms with features)
    - IPA pronunciation for each form
    - Initial mutations (if any)
    - Morphology notes
    - Cognates in other Celtic languages
    - Difficulty 1-5

    Important:
    - Preserve Celtic-language text with fadas / circumflexes
    - For Irish (IRISH), dispatch via `uccix-mistral-24b` (UCCIX)
    - For Welsh/Scottish/Breton/Manx/Cornish, dispatch via `gemma-4-26B-A4B`
  "#
}
