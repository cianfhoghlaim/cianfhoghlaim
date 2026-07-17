// BAML schema: Isle of Man subject taxonomy (Crown Dependency)
//
// Per the 2026-07-31-biep-v3-crown-dependencies-v1 change.
//
// The Isle of Man uses the English GCSE + A-Level system. Administered
// by the Isle of Man Department of Education, Sport and Culture.
//
// Reference: openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/

enum IsleOfManLevel {
  GCSE
  A_LEVEL
  AS_LEVEL
  BTEC
}

enum IsleOfManSubject {
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
  CONSTRUCTION
  ENGINEERING
  HEALTH_AND_SOCIAL_CARE
  OTHER
}