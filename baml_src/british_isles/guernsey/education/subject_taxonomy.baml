// BAML schema: Guernsey subject taxonomy (Crown Dependency)
//
// Per the 2026-07-31-biep-v3-crown-dependencies-v1 change.
//
// Guernsey uses the English GCSE + A-Level system (with a small
// number of additional local qualifications). Administered by the
// States of Guernsey Education Services.
//
// Reference: openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/

enum GuernseyLevel {
  GCSE
  A_LEVEL
  AS_LEVEL
  BTEC
}

enum GuernseySubject {
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
  // Humanities
  HISTORY
  GEOGRAPHY
  RELIGIOUS_STUDIES
  // Languages
  FRENCH
  GERMAN
  SPANISH
  // Arts
  ART_AND_DESIGN
  MUSIC
  DRAMA
  MEDIA_STUDIES
  // Business
  BUSINESS
  ECONOMICS
  // PE
  PHYSICAL_EDUCATION
  // Other
  PSYCHOLOGY
  SOCIOLOGY
  LAW
  DESIGN_AND_TECHNOLOGY
  CHILD_DEVELOPMENT
  HEALTH_AND_SOCIAL_CARE
  OTHER
}