// BAML schema: Scotland subject taxonomy (SQA awarding body)
//
// Per the 2026-07-30-biep-v3-sct-wls-ni-v1 change.
//
// Parallel to the AQA + OCR + Edexcel enums from Phase 3.
// Scotland has 3 qualification levels per subject:
//   - National 5 (Standard Grade successor)
//   - Higher
//   - Advanced Higher
//
// Reference: openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/

enum SCQFLevel {
  NATIONAL_5    @description("Scottish National 5 (SCQF Level 5)")
  HIGHER        @description("Scottish Higher (SCQF Level 6)")
  ADVANCED_HIGHER @description("Scottish Advanced Higher (SCQF Level 7)")
}

enum SCQFSubject {
  // Core STEM
  MATHEMATICS
  APPLICATIONS_OF_MATHEMATICS
  PURE_MATHEMATICS
  STATISTICS
  BIOLOGY
  CHEMISTRY
  PHYSICS
  HUMAN_BIOLOGY
  COMPUTING_SCIENCE
  // English + Lit
  ENGLISH
  ENGLISH_FOR_WORK_AND_LEISURE
  // Humanities
  HISTORY
  GEOGRAPHY
  MODERN_STUDIES
  POLITICS
  PHILOSOPHY
  RELIGIOUS_MORAL_EDUCATION
  // Languages
  FRENCH
  GERMAN
  SPANISH
  ITALIAN
  LATIN
  GAEILC
  // Arts
  ART_AND_DESIGN
  MUSIC
  MUSIC_TECHNOLOGY
  DRAMA
  // Business
  BUSINESS_MANAGEMENT
  ACCOUNTING
  ECONOMICS
  // VocTech
  DESIGN_AND_MANUFACTURE
  GRAPHIC_COMMUNICATION
  ENGINEERING_SCIENCE
  // PE
  PHYSICAL_EDUCATION
  // Other
  PSYCHOLOGY
  SOCIOLOGY
  LAW
  MEDIA_STUDIES
  HEALTH_AND_FOOD_TECHNOLOGY
  HOSPITALITY
  TRAVEL_AND_TOURISM
  EARLY_YEARS_AND_CHILDCARE
  CHILD_CARE_AND_DEVELOPMENT
  OTHER
}