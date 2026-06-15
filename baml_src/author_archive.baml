// BAML Schema for Author Archive Extraction
//
// Structured extraction of three personal-archive document types:
//   1. Gemini Deep Research PDFs (agentic-research output)
//   2. University of Galway academic artefacts (assignments, placements, etc.)
//   3. Handwritten equations from OCR'd pages
//
// English-only for this change (per the user). All extractions route through
// the canonical LiteLLM gateway via the `extract_en` client alias.

enum GeminiDomain {
  LAW            @description("Legal / citizenship / justice topics")
  MEDICAL        @description("Healthcare / medical access / disability")
  POLITICS       @description("Political parties / elections / policy")
  TECHNOLOGY     @description("Tech industry / regulation / diplomacy")
  CULTURE        @description("Cultural identity / heritage / arts")
  OTHER          @description("None of the above")
  IDENTITY       @description("Personal / familial / identity documents")
  EDUCATION      @description("Education policy / academic / curriculum")
}

enum UoGArtifactKind {
  ASSIGNMENT         @description("Coursework assignment (B.Ed, PGCE, B.A., etc.)")
  EXAM               @description("Exam paper or revision material")
  LECTURE_NOTES      @description("Lecture notes or class handouts")
  ACTION_RESEARCH    @description("Action-research project (B.Ed, PGCE)")
  PLACEMENT          @description("School placement / internship portfolio")
  CODE_FILE          @description("Code file (software_development/)")
  SCANNED_PAGES      @description("Scanned PDF or Apple Pages file (handwriting candidate)")
  PRESENTATION       @description("PowerPoint / Keynote presentation")
  TRANSCRIPT         @description("Academic transcript or record")
  OTHER              @description("None of the above")
}

enum UoGStage {
  UNDERGRADUATE      @description("Undergraduate (B.A., B.Sc., etc.)")
  PGCE               @description("Professional Master of Education")
  MASTERS            @description("Taught or research Masters")
  PHD                @description("Doctoral research")
  PROFESSIONAL       @description("Professional development / CPD")
  UNKNOWN            @description("Stage cannot be inferred from the file")
}

enum UoGLanguage {
  EN                 @description("English (only language for this change)")
  GA                 @description("Irish (Gaeilge)")
  MIXED              @description("Bilingual English/Irish content")
  UNKNOWN            @description("Language cannot be inferred")
}

enum EquationConfidence {
  HIGH               @description("OCR + VLM agree, LaTeX is well-formed")
  MEDIUM             @description("One back-end available, LaTeX is plausible")
  LOW                @description("Best-effort LaTeX, may be incomplete")
  UNREADABLE         @description("OCR produced no usable signal")
}

// =============================================================================
// Cited URL
// =============================================================================

class CitedUrl {
  url string @description("The cited URL (https/http)")
  anchor_text string? @description("Anchor text from a markdown link, if any")
  source string @description("Where the URL was found: pymupdf_link, markdown_inline, first_page_header")
}

// =============================================================================
// Gemini Deep Research Report
// =============================================================================

class GeminiDeepResearchReport {
  topic string @description("One-sentence topic of the report, e.g. 'cross-border medical malpractice'")
  domain GeminiDomain @description("High-level topical domain")
  summary string @description("2-3 sentence summary of the report's main thesis")
  key_findings string[] @description("3-7 bullet-point findings, each a single sentence")
  cited_urls CitedUrl[] @description("Inline citations extracted from the PDF")
  gemini_account string? @description("Gemini account label if known (e.g. 'cian_personal'), else null")
  research_date string? @description("Date the report was generated, ISO-8601 (YYYY-MM-DD) if discernible, else null")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

// =============================================================================
// University of Galway Artefact
// =============================================================================

class UniversityOfGalwayArtifact {
  artifact_kind UoGArtifactKind @description("What kind of academic artefact this is")
  course_code string? @description("Course code if extractable, e.g. 'CT511', 'GA101', 'ED305'")
  module_title string? @description("Module / paper title, e.g. 'History of Irish Education'")
  stage UoGStage @description("Programme stage")
  language UoGLanguage @description("Always 'en' for this change")
  key_topics string[] @description("3-7 topical tags")
  requires_handwriting_ocr bool @description("True if the artefact contains handwriting (handwritten notes, scanned equations, .pages files)")
  word_count int? @description("Approximate word count of the extracted text, if known")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

// =============================================================================
// Handwritten Equation
// =============================================================================

class HandwrittenEquation {
  latex string @description("LaTeX representation of the equation, e.g. '\\\\int_0^1 x^2 \\\\, dx'")
  verbatim string @description("Verbatim character-level transcription of the handwritten text")
  context string @description("Surrounding text (the sentence or paragraph the equation appears in)")
  confidence float @description("OCR + VLM agreement 0.0-1.0")
  equation_confidence EquationConfidence @description("Categorical confidence bucket")
}

// =============================================================================
// Functions
// =============================================================================

function ExtractGeminiReport(pdf_text: string, file_name: string) -> GeminiDeepResearchReport {
  client ExtractEn
  prompt #"
    You are an expert research analyst. Extract a structured summary of a Gemini Deep Research report.

    File name: {{ file_name }}

    The report text follows. Extract the topic (one sentence), the high-level domain,
    a 2-3 sentence summary, 3-7 key findings (each a single sentence), the list of
    cited URLs (with anchor text when present), the Gemini account label if the
    document mentions it (else null), the research date if discernible (else null),
    and your overall confidence 0.0-1.0.

    Report text:
    ---
    {{ pdf_text }}
    ---

    {{ ctx.output_format }}
  "#
}

function ExtractUoGArtifact(pdf_text: string, file_name: string, file_type: string) -> UniversityOfGalwayArtifact {
  client ExtractEn
  prompt #"
    You are an expert archivist of a University of Galway student's academic record.
    Extract a structured summary of a single academic artefact.

    File name: {{ file_name }}
    File type: {{ file_type }}

    Determine: the artefact kind (assignment, exam, lecture notes, action research,
    placement, code file, scanned pages, presentation, transcript, or other), the
    course code if extractable from the file name or contents (e.g. CT511, GA101,
    ED305, GF107), the module / paper title if known, the programme stage
    (undergraduate, PGCE, masters, PhD, professional, unknown), the language
    (always "en" for this change), 3-7 key topics, whether the artefact contains
    handwriting that would need OCR / HTR (true for .pages files, scanned PDFs, or
    any document where you can see reference to handwritten notes), the approximate
    word count if discernible, and your overall confidence 0.0-1.0.

    Artefact text:
    ---
    {{ pdf_text }}
    ---

    {{ ctx.output_format }}
  "#
}

function ExtractHandwrittenEquations(ocr_text: string, file_name: string) -> HandwrittenEquation[] {
  client ExtractEn
  prompt #"
    You are an expert OCR / HTR analyst. The following text was extracted from a
    handwritten page (e.g. an Apple Pages file, a scanned PDF, or a maths
    notebook). Extract every distinct mathematical equation as a separate
    `HandwrittenEquation`.

    File name: {{ file_name }}

    For each equation emit:
      - `latex`: the LaTeX representation, using \\\\ for backslashes inside strings
      - `verbatim`: the verbatim transcription as best you can
      - `context`: the surrounding sentence or paragraph
      - `confidence`: a float 0.0-1.0 reflecting how certain the LaTeX is
      - `equation_confidence`: one of HIGH, MEDIUM, LOW, UNREADABLE

    OCR text:
    ---
    {{ ocr_text }}
    ---

    If the OCR text contains no equations, return an empty list.

    {{ ctx.output_format }}
  "#
}

// =============================================================================
// Tests
// =============================================================================

test ExtractGeminiReportTest {
  functions [ExtractGeminiReport]
  args {
    pdf_text #"
      # Cross-border Medical Malpractice: A Comparative Study

      This report examines the legal recourse available to dual British-Irish
      citizens who experience medical malpractice in either jurisdiction.

      Key findings:
      1. The Common Travel Area provides limited reciprocal enforcement.
      2. Statute of limitations varies by jurisdiction.
      3. Expert witness requirements differ significantly.
    "#
    file_name "cross_border_medical_malpractice_and_data_breach.pdf"
  }
}

test ExtractUoGArtifactTest {
  functions [ExtractUoGArtifact]
  args {
    pdf_text #"
      ED305 Assignment 2: A reflective account of a 4th-year B.Ed placement
      at an urban DEIS school. Topics: lesson planning, classroom management,
      inclusive education, assessment for learning.
    "#
    file_name "ed305_assignment_2.pdf"
    file_type "pdf"
  }
}

test ExtractHandwrittenEquationsTest {
  functions [ExtractHandwrittenEquations]
  args {
    ocr_text #"
      Q1. Compute the definite integral
        \int_0^1 x^2 \, dx
      using the Fundamental Theorem of Calculus.
    "#
    file_name "measurements.pages"
  }
}
