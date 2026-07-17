// BAML schema: Wales subject taxonomy (WJEC awarding body)
//
// Per the 2026-07-30-biep-v3-sct-wls-ni-v1 change.
//
// WJEC (Welsh Joint Education Committee) is the awarding body for
// Wales. The Curriculum for Wales uses 2 main qualification levels:
//   - GCSE
//   - A-Level
//
// Welsh-medium subjects are flagged via the language field
// (cy = Cymraeg / Welsh).
//
// Reference: openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/

enum WJECLevel {
  GCSE
  A_LEVEL
  AS_LEVEL
  WELSH_BACCALAUREATE
}

enum WJECSubject {
  // Core STEM
  MATHEMATICS
  FURTHER_MATHEMATICS
  BIOLOGY
  CHEMISTRY
  PHYSICS
  COMPUTER_SCIENCE
  // English + Lit
  ENGLISH_LANGUAGE
  ENGLISH_LITERATURE
  // Welsh-medium
  WELSH_LANGUAGE
  WELSH_LITERATURE
  // Humanities
  HISTORY
  GEOGRAPHY
  WELSH_HISTORY
  WELSH_GEOGRAPHY
  RELIGIOUS_STUDIES
  PHILOSOPHY
  // Languages
  FRENCH
  GERMAN
  SPANISH
  ITALIAN
  LATIN
  // Arts
  ART_AND_DESIGN
  MUSIC
  DRAMA
  MEDIA_STUDIES
  // Business
  BUSINESS
  ECONOMICS
  LAW
  // PE
  PHYSICAL_EDUCATION
  // Other
  PSYCHOLOGY
  SOCIOLOGY
  POLITICS
  HEALTH_AND_SOCIAL_CARE
  ENGINEERING
  DESIGN_AND_TECHNOLOGY
  FOOD_TECHNOLOGY
  TEXTILES
  OTHER
}