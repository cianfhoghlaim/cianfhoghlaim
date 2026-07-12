// =============================================================================
// DocumentType — hoisted canonical enum
// =============================================================================
// Merged from the 2 dups removed in `2026-07-12-baml-rename-42-duplicates-v1`:
//   - processing/ocr_validation.baml (7 values, OCR-focused)
//   - education/cross_nation/isles_education.baml (11 values, broader)
// The consumer files use the renamed locals:
//   - DocumentTypeOcr (ocr_validation.baml)
//   - DocumentTypeIsles (isles_education.baml)
// Add a new consumer file by importing or referencing `DocumentType` here.
// =============================================================================

enum DocumentType {
  // Education-focused (isles_education values)
  CURRICULUM_SPECIFICATION @description("Official curriculum specification document")
  SYLLABUS @description("Subject syllabus")
  EXAM_PAPER @description("Past examination paper")
  MARKING_SCHEME @description("Marking scheme for exam")
  CHIEF_EXAMINER_REPORT @description("Examiner's report on exam session")
  TEACHING_RESOURCE @description("Teaching/learning resource")
  ASSESSMENT_GUIDELINES @description("Assessment guidance document")
  POLICY_DOCUMENT @description("Education policy document")
  STATUTORY_GUIDANCE @description("Statutory/legal guidance")
  TERMINOLOGY @description("Terminology database entry")
  TEXTBOOK @description("Textbook or course material")

  // OCR-focused (ocr_validation values)
  CURRICULUM @description("NCCA curriculum document (OCR-detected)")
  COURSE_MATERIAL @description("Educational course material")
  WORKSHEET @description("Student worksheet")
  CIRCULAR @description("Department circular")
  UNKNOWN @description("Unknown document type")
}