// BAML schema: Jersey subject taxonomy (Crown Dependency)
//
// Per the 2026-07-31-biep-v3-crown-dependencies-v1 change.
//
// Jersey has its own curriculum (a hybrid of English GCSE + French
// Baccalauréat). The Jersey Curriculum is administered by the
// States of Jersey Education Department.
//
// Reference: openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/

enum JerseyLevel {
  GCSE
  A_LEVEL
  INTERNATIONAL_BACCALAUREATE
  FRENCH_BACCALAUREAT
}

enum JerseySubject {
  // Core STEM (mirrors English GCSE)
  MATHEMATICS
  FURTHER_MATHEMATICS
  BIOLOGY
  CHEMISTRY
  PHYSICS
  COMPUTER_SCIENCE
  // English + Lit
  ENGLISH_LANGUAGE
  ENGLISH_LITERATURE
  // French (mandatory in Jersey)
  FRENCH
  // Humanities
  HISTORY
  GEOGRAPHY
  RELIGIOUS_STUDIES
  // Other languages
  GERMAN
  SPANISH
  LATIN
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
  OTHER
}