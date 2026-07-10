// BAML schema: Curriculum Syllabus Extraction
//
// Used by the LC5-subject pipeline (chem/CS/gaeilge/geography/maths)
// to extract structured data from a NCCA Leaving Certificate syllabus PDF.
// The same schema works for both English (en) and Irish (ga) syllabi;
// the `language` field tracks which is present.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

enum SyllabusLanguage {
  EN
  GA
  EN_AND_GA
}

enum NCCAStage {
  JC      @description("Junior Cycle (Years 1-3)")
  LC_OL   @description("Leaving Certificate Ordinary Level (Year 4-5)")
  LC_HL   @description("Leaving Certificate Higher Level (Year 5-6)")
  LC_FDN  @description("Leaving Certificate Foundation Level")
}

enum ModuleType {
  CORE               @description("Mandatory for all students")
  OPTIONAL           @description("Student choice from a list")
  SPECIALISM         @description("Higher-Level-only advanced topic")
  PRACTICAL          @description("Mandatory experiment / lab work")
  ASSESSMENT         @description("Exam technique, marking, etc.")
}

class ModuleTopic {
  module_id: string
  name_en: string
  name_ga: string?
  type: ModuleType
  // Learning outcomes (specific, measurable)
  learning_outcomes: string[]
  estimated_hours: int?
}

class LcLearningOutcome {
  lo_id: string
  statement_en: string
  statement_ga: string?
  blooms_taxonomy_level: string?
}

class SyllabusDocument {
  // Document-level metadata
  subject: string
  language: SyllabusLanguage
  stage: NCCAStage
  source_pdf: string
  source_pages: int

  // Document content
  module_topics: ModuleTopic[]
  total_learning_outcomes: int

  // Cross-cutting
  cross_curricular: string[]
  assessment_objectives: string[]
}

// ============================================================================
// BAML function — the canonical extractor (BIEP v1)
// ============================================================================
// Replaces the legacy `b.ExtractLeavingCertSyllabus` from
// `baml/education/pdfs/leaving_cert_syllabus.baml`.
//
// Returns the canonical `SyllabusDocument` Pydantic class.
// NCCA publishes the syllabus for each LC subject as a single combined PDF
// (Higher + Ordinary + Foundation sections in one document). The
// `language` enum distinguishes EN / GA / bilingual PDFs.

function ExtractCurriculumSyllabus(
  pdf_text: string,
  subject: string?,
  language: string?,
) -> SyllabusDocument {
  client ExtractEn
  prompt #"
    You are an Irish Leaving Certificate syllabus expert. Given the
    text of a NCCA Leaving Certificate syllabus PDF (one of the 6
    priority subjects: Mathematics, Chemistry, Geography, Gaeilge,
    English, Computer Science), extract the structured syllabus.

    Subject context: {{ subject }}
    Language context: {{ language }} (en or ga)

    For each module/topic in the syllabus, populate:
      - module_id: a deterministic slug, e.g. "maths_algebra", "chem_acids_bases"
      - name_en: short English display name
      - name_ga: short Irish display name (null if English-only)
      - type: CORE / OPTIONAL / SPECIALISM / PRACTICAL / ASSESSMENT
      - learning_outcomes: array of full NCCA LO statements (verbatim)
      - estimated_hours: integer (null if not stated)

    Document-level fields:
      - subject: canonical subject slug ("mathematics", "chemistry", ...)
      - language: EN / GA / EN_AND_GA based on the PDF's primary language
      - stage: JC / LC_OL / LC_HL / LC_FDN based on the PDF's level
      - source_pdf: filename or path
      - source_pages: integer page count
      - module_topics: the populated topics
      - total_learning_outcomes: sum of all LOs across topics
      - cross_curricular: array of cross-curricular links (e.g. "Science",
        "Digital Literacy"); empty if not present
      - assessment_objectives: array of assessment aim statements

    Preserve Irish-language fidelity: every syllabus must keep its
    bilingual character where attested. Do NOT translate the Irish
    names to English in `name_ga`.

    Syllabus PDF text:
    ---
    {{ pdf_text }}
    ---

    {{ ctx.output_format }}
  "#
}

// ============================================================================
// Backward-compatibility alias (BIEP v1 — Phase 1.3 migration)
// ============================================================================
// The 8 per-subject DLT sources historically called
// `b.ExtractLeavingCertSyllabus` from `baml/education/pdfs/leaving_cert_syllabus.baml`.
// That legacy function is now `## REMOVED` (per the 1.2.1 task) and
// replaced by this canonical `ExtractCurriculumSyllabus`. Any caller that
// still passes legacy kwargs will be transparently routed here.
