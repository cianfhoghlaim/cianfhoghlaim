// =============================================================================
// LanguageCode — hoisted canonical enum
// =============================================================================
// Merged from the 2 dups removed in `2026-07-12-baml-rename-42-duplicates-v1`:
//   - processing/ocr_validation.baml (7 values, including MIXED + UNKNOWN)
//   - education/cross_nation/isles_education.baml (6 Celtic-only values)
// The consumer files use the renamed locals:
//   - LanguageCodeOcr (ocr_validation.baml)
//   - LanguageCodeIsles (isles_education.baml)
// Add a new consumer file by importing or referencing `LanguageCode` here.
// =============================================================================

enum LanguageCode {
  EN @description("English")
  GA @description("Irish / Gaeilge")
  GD @description("Scottish Gaelic / Gàidhlig")
  CY @description("Welsh / Cymraeg")
  GV @description("Manx / Gaelg")
  KW @description("Cornish / Kernewek")
  MIXED @description("Multiple languages detected")
  UNKNOWN @description("Could not detect")
}
