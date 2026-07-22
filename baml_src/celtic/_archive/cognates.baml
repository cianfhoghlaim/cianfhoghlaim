// === ARCHIVED 2026-06-24 ===
// The 5 functions in this file (IdentifyCognates,
// CompareCelticVocabulary, IdentifyFalseFriends, ExplainSoundChanges,
// GenerateCognateVocabulary) have no current Python consumer in the
// oideachais quadrant. They are intended for the meaisinfhoghlaim/
// Celtic-linguistic agents and the croilar/ portfolio surface,
// which are not yet built.
//
// To re-activate:
// 1. Implement the consumer (e.g. meaisinfhoghlaim/agents/cognates.py)
// 2. Move this file back to baml_src/ (git mv)
// 3. Remove the ARCHIVED header from the top
// 4. Update STATUS.md to mark the functions as wired
// 5. Update REFACTORING.md to remove the archive entry
//
// Reference: openspec/changes/archive-celtic-baml-orphans/
// =====================================================================

// Cognates - Cross-Celtic Vocabulary Comparison
// Extract cognate relationships across Celtic languages
// December 2024

// ============================================================================
// COGNATE RELATIONSHIPS
// ============================================================================

// A set of cognate words across Celtic languages
class CognateSet {
  concept string @description("The shared meaning in English")
  proto_celtic string? @description("Reconstructed Proto-Celtic form (*)")

  // Goidelic (Q-Celtic)
  irish string? @description("Modern Irish form")
  scottish_gaelic string? @description("Scottish Gaelic form")
  manx string? @description("Manx form")
  old_irish string? @description("Old Irish form")

  // Brythonic (P-Celtic)
  welsh string? @description("Welsh form")
  breton string? @description("Breton form")
  cornish string? @description("Cornish form")

  // Non-Celtic cognates
  latin string? @description("Latin cognate if any")
  english string? @description("English cognate or loan")

  etymology_notes string? @description("Notes on etymology and sound changes")
}

// A single cognate pair
class CognatePair {
  concept string @description("Shared meaning")
  source_language CelticLanguage @description("Source language")
  source_word string @description("Word in source language")
  target_language CelticLanguage @description("Target language")
  target_word string @description("Word in target language")
  confidence float @description("Confidence in relationship (0-1)")
  sound_changes string? @description("Sound changes involved")
}

// Historical sound change
class SoundChange {
  from_stage string @description("Starting stage (Proto-Celtic, Old Irish, etc.)")
  to_stage string @description("Ending stage")
  change_description string @description("Description of the change")
  example string? @description("Example word showing the change")
  phonetic_environment string? @description("Where the change occurs")
}

// False friend warning
class FalseFriend {
  language_a CelticLanguage @description("First language")
  word_a string @description("Word in first language")
  meaning_a string @description("Meaning in first language")
  language_b CelticLanguage @description("Second language")
  word_b string @description("Similar word in second language")
  meaning_b string @description("Different meaning")
  warning string @description("Why this is confusing")
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
function IdentifyCognates(
  word: string @description("Word to find cognates for"),
  language: CelticLanguage @description("Language of the word"),
  meaning: string? @description("Meaning if known")
) -> CognateSet {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Compare vocabulary across two Celtic languages
function CompareCelticVocabulary(
  text: string @description("Text to analyze for cognates"),
  language_a: CelticLanguage @description("First language"),
  language_b: CelticLanguage @description("Second language to compare")
) -> CognatePair[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Identify false friends between Celtic languages
function IdentifyFalseFriends(
  word: string @description("Word to check"),
  language_a: CelticLanguage @description("First language"),
  language_b: CelticLanguage @description("Second language")
) -> FalseFriend? {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Explain sound changes in a cognate set
function ExplainSoundChanges(
  proto_form: string @description("Reconstructed Proto-Celtic form"),
  modern_form: string @description("Modern form in any Celtic language"),
  language: CelticLanguage @description("Language of modern form")
) -> SoundChange[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

// Generate cognate vocabulary for a semantic field
function GenerateCognateVocabulary(
  semantic_field: string @description("Topic: numbers, family, nature, etc."),
  languages: CelticLanguage[] @description("Languages to include")
) -> CognateSet[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
