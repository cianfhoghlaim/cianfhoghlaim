// BAML schema: gov.ie Education Circulars Extraction (BIEP v1)
//
// Used by the BIEP v1 government_circulars DLT source +
// Dagster gov.ie circulars asset to extract structured data from
// Department-of-Education-and-Skills (DES), NCCA, State Examinations
// Commission (SEC), and Department-of-Education (DoE / NI) circulars
// scraped from gov.ie/en/circulars and gov.ie/ga/ciorcláin.
//
// Per the BIEP v1 spec (openspec/specs/british-isles-education-pipeline/spec.md)
// and the canonical `cianfhoghlaim-baml-schemas` spec. Uses the canonical
// `ExtractEn` (default) + `ExtractEnStrong` (cross-archive link) + `LocalVision`
// (multimodal PDF) clients.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

// ============================================================================
// Enums
// ============================================================================

enum CircularDepartment {
  DES      @description("Department of Education and Skills (Ireland)")
  NCCA     @description("National Council for Curriculum and Assessment")
  SEC      @description("State Examinations Commission")
  DOE_NI   @description("Department of Education (Northern Ireland)")
  JMB      @description("Irish Universities Association / Joint Matriculation Board legacy")
  OTHER
}

enum CircularSubjectArea {
  MATHEMATICS
  APPLIED_MATHEMATICS
  CHEMISTRY
  PHYSICS
  BIOLOGY
  GEOGRAPHY
  GAEILGE
  ENGLISH
  FRENCH
  HISTORY
  BUSINESS
  ACCOUNTING
  ART
  MUSIC
  COMPUTER_SCIENCE
  CROSS_SUBJECT
  SCHOOL_ADMINISTRATION
  INFRASTRUCTURE
  GENERAL
}

// ============================================================================
// Core value types
// ============================================================================

class EducationCircular {
  circular_id string            @description("Deterministic; e.g. 'DES-2024-0042'")
  circular_number int
  dept CircularDepartment
  subject_area CircularSubjectArea
  year int                      @description("Issued year (e.g. 2024)")
  language string               @description("en or ga")
  title_en string
  title_ga string?              @description("Irish title; null for EN-only circulars")
  summary string                @description("200-500 char summary")
  full_text string              @description("Verbatim text (truncated to 24,000 chars)")
  url string                    @description("Source URL on gov.ie")
  published_at string           @description("ISO 8601 date of publication")
  extraction_confidence float   @description("0.0-1.0; 1.0 = perfect parse")
  extracted_at string           @description("ISO 8601 datetime of BAML extraction")
}

class CircularToSyllabusLink {
  circular_id string            @description("Foreign key to EducationCircular")
  syllabus_subject string       @description("subject code; e.g. 'chemistry'")
  syllabus_stage string         @description("JC / LC_OL / LC_HL / LC_FDN")
  syllabus_language string      @description("en or ga")
  link_type string              @description("REFERENCES / AMENDS / SUPERSEDES")
  syllabus_pdf string           @description("Path to the NCCA syllabus PDF")
  syllabus_page int?            @description("Page number in the syllabus (1-indexed)")
  confidence float              @description("0.0-1.0; 1.0 = explicit reference")
  rationale string              @description("Plain-English explanation of the link")
}

// ============================================================================
// BAML functions
// ============================================================================

function ExtractCircular(
  url: string,
  html: string,
  pdf_text: string,
  language: string,
) -> EducationCircular {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function LinkCircularToSyllabus(
  circular: EducationCircular,
  candidate_syllabi: string[]   @description("List of syllabus PDF paths to consider"),
) -> CircularToSyllabusLink[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ClassifyCircular(
  pdf_text: string,
  url: string,
) -> CircularDepartment {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
