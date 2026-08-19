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
) -> VerbConjugation {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Extract noun declension
function ExtractNounDeclension(
  noun: string @description("Noun in any form"),
  language: CelticLanguage @description("Language of the noun")
) -> NounDeclension {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Identify conjugation/declension class
function IdentifyMorphologicalClass(
  word: string @description("Word to classify"),
  pos: PartOfSpeech @description("Part of speech"),
  language: CelticLanguage @description("Language")
) -> string {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}

// Compare adjectives
function CompareAdjective(
  adjective: string @description("Adjective in positive form"),
  language: CelticLanguage @description("Language")
) -> AdjectiveComparison {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
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
) -> CelticMorphologySpec[] {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    CelticMorphologySpec[] {}
  }
}
