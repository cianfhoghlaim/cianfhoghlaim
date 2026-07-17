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
  CHEMISTRY
  GEOGRAPHY
  GAEILGE
  ENGLISH
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
) -> EducationCircular {
  client ExtractEn
  prompt #"
    You are the BIEP v1 gov.ie education-circular extractor. Given
    a scraped circular page (HTML + extracted PDF text), produce a
    structured EducationCircular.

    URL: {{ url }}
    Language: {{ language }} (en or ga)

    HTML (first 6,000 chars):
    ---
    {{ html }}
    ---

    PDF text (first 18,000 chars):
    ---
    {{ pdf_text }}
    ---

    Return an EducationCircular with:
      - circular_id: deterministic "{dept}-{year}-{circular_number padded 4}"
      - circular_number: integer (e.g. 0042)
      - dept: CircularDepartment (DES / NCCA / SEC / DOE_NI / JMB / OTHER)
      - subject_area: CircularSubjectArea (MATHEMATICS / CHEMISTRY /
        GEOGRAPHY / GAEILGE / ENGLISH / COMPUTER_SCIENCE /
        CROSS_SUBJECT / SCHOOL_ADMINISTRATION / INFRASTRUCTURE / GENERAL)
      - year: integer
      - language: en or ga
      - title_en: 5-15 word title
      - title_ga: Irish translation; null if EN-only
      - summary: 200-500 char plain-English summary
      - full_text: verbatim text (truncate to 24,000 chars; preserve
        line breaks)
      - url: the source URL
      - published_at: ISO 8601 date string
      - extraction_confidence: 0.0-1.0
      - extracted_at: current ISO 8601 datetime

    Preserve BILINGUAL nature: every circular should have BOTH
    title_en and title_ga (title_ga may be null for EN-only circulars).

    {{ ctx.output_format }}
  "#
}

function LinkCircularToSyllabus(
  circular: EducationCircular,
  candidate_syllabi: string[]   @description("List of syllabus PDF paths to consider"),
) -> CircularToSyllabusLink[] {
  client ExtractEnStrong
  prompt #"
    You are the BIEP v1 cross-archive linker. Given a government
    education circular and a list of candidate NCCA syllabus PDFs,
    determine WHICH syllabi the circular references, amends, or
    supersedes.

    Circular:
    {{ circular }}

    Candidate syllabi (PDF paths):
    {{ candidate_syllabi }}

    For each syllabus that the circular explicitly references, return
    a CircularToSyllabusLink with:
      - circular_id: from the input circular
      - syllabus_subject: subject code (e.g. 'chemistry', 'gaeilge')
      - syllabus_stage: JC / LC_OL / LC_HL / LC_FDN
      - syllabus_language: en or ga
      - link_type: REFERENCES (mentioned in circular body) /
        AMENDS (changes the syllabus) / SUPERSEDES (replaces)
      - syllabus_pdf: the path
      - syllabus_page: 1-indexed page (null if uncertain)
      - confidence: 0.0-1.0; 1.0 = explicit reference
      - rationale: 1-2 sentence plain-English explanation

    Return an empty list if the circular does not reference any of
    the candidate syllabi. Do NOT fabricate links.

    {{ ctx.output_format }}
  "#
}

function ClassifyCircular(
  pdf_text: string,
  url: string,
) -> CircularDepartment {
  client LocalVision
  prompt #"
    You are a circular-department classifier. Given the PDF text of
    an Irish / Northern Ireland education circular, return the
    issuing department as a CircularDepartment enum value.

    URL: {{ url }}

    PDF text (first 4,000 chars):
    ---
    {{ pdf_text }}
    ---

    Return ONE CircularDepartment value: DES, NCCA, SEC, DOE_NI, JMB, OTHER.

    The classification is based on the letterhead, signatures,
    circular-number prefix, and boilerplate footer text of the
    circular.

    {{ ctx.output_format }}
  "#
}
