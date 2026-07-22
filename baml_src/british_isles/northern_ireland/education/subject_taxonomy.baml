// BAML schema: Northern Ireland subject taxonomy (CCEA awarding body)
//
// Per the 2026-07-30-biep-v3-sct-wls-ni-v1 change.
//
// CCEA (Council for the Curriculum, Examinations and Assessment) is
// the awarding body for Northern Ireland. CCEA has its own GCSE +
// A-Level specifications (parallel to AQA / OCR / Edexcel in
// England, WJEC in Wales, SQA in Scotland).
//
// Northern Ireland has an Irish-medium (Gaeltacht) overlay:
//   - Irish-medium schools teach through the medium of Irish
//   - The CCEA Irish language GCSE is a unique NI subject
//
// Reference: openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/

enum CCEALevel {
  GCSE
  A_LEVEL
  AS_LEVEL
  OTHER
}

enum CCEASubject {
  // Core STEM
  MATHEMATICS
  FURTHER_MATHEMATICS
  BIOLOGY
  CHEMISTRY
  PHYSICS
  COMPUTING_SCIENCE
  // English + Lit
  ENGLISH_LANGUAGE
  ENGLISH_LITERATURE
  // Irish (Gaeltacht overlay)
  IRISH
  IRISH_LANGUAGE
  // Humanities
  HISTORY
  GEOGRAPHY
  RELIGIOUS_STUDIES
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
  NUTRITION_AND_FOOD_SCIENCE
  OTHER
}