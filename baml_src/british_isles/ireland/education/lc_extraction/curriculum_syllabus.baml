// BAML schema: Curriculum Syllabus Extraction
//
// Used by the LC5-subject pipeline (chem/CS/gaeilge/geography/maths)
// to extract structured data from a NCCA Leaving Certificate syllabus PDF.
// The same schema works for both English (en) and Irish (ga) syllabi;
// the `language` field tracks which is present.
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate
//
// Per R28 of `2026-07-19-leaving-cert-pdf-lineage-and-schema-codegen-v1`:
// composes `LineageTrace` from `lc_extraction/_shared/lineage_trace.baml`
// for the lineage viewer.

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
  module_id string
  name_en string
  name_ga string?
  type ModuleType
  // Learning outcomes (specific, measurable)
  learning_outcomes string[]
  estimated_hours int?
}

class LcLearningOutcome {
  lo_id string
  statement_en string
  statement_ga string?
  blooms_taxonomy_level string?
}

class SyllabusDocument {
  // Document-level metadata
  subject string
  language SyllabusLanguage
  stage NCCAStage
  source_pdf string
  // Nullable (2026-08-06 token-plan-apis change, Phase 2b): the model
  // cannot know the PDF page count from extracted text alone. Matches
  // the already-nullable LCSyllabus.source_pages in
  // british_isles/_cross/unified_extraction.baml.
  source_pages int?

  // Document content
  module_topics ModuleTopic[]
  total_learning_outcomes int

  // Cross-cutting
  cross_curricular string[]
  assessment_objectives string[]

  // Lineage provenance (R28). Composed from
  // `lc_extraction/_shared/lineage_trace.baml`. The Python caller (Dagster
  // asset + Conway envelope wrapper) populates this at write time —
  // the BAML function itself doesn't need to fill it in for its own
  // prompt, but downstream consumers can rely on it being present.
  lineage LineageTrace?
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
) -> SyllabusDocument {  client ExtractEn
  prompt #"
    You are an expert at reading official NCCA (National Council for
    Curriculum and Assessment) Irish Leaving Certificate syllabus
    documents and extracting their structure with complete fidelity —
    every fact below MUST be grounded in the PDF text given; never invent
    a module, learning outcome, or hour count that isn't actually present.

    Subject: {{ subject }}
    Language of this PDF: {{ language }}

    From the syllabus text below, extract:
    - subject: the subject slug (e.g. 'chemistry', 'mathematics')
    - language: EN, GA, or EN_AND_GA depending on what you observe in the text
    - stage: JC, LC_OL, LC_HL, or LC_FDN — NCCA syllabi usually cover
      multiple levels in one document; pick the stage that best matches
      the section you are reading, or LC_HL if the document does not
      distinguish levels
    - source_pdf: leave as an empty string if not derivable from the text;
      the Python caller fills this in from the actual file path
    - module_topics: every distinct module/unit/strand you can find, each with:
      - module_id (a short stable slug, e.g. 'M1', derived from the
        syllabus's own numbering if present)
      - name_en / name_ga (name_ga only if the Irish-language term
        appears in the text)
      - type: CORE, OPTIONAL, SPECIALISM, PRACTICAL, or ASSESSMENT,
        based on how the syllabus itself describes the module
      - learning_outcomes: the exact (or lightly normalised) learning
        outcome statements listed under that module — do not paraphrase
        away specific verbs ('describe', 'derive', 'evaluate') since
        they are pedagogically load-bearing
      - estimated_hours: only if the syllabus states a number of hours
        or class periods for the module; otherwise omit
    - total_learning_outcomes: the count of all learning_outcomes across
      all module_topics
    - cross_curricular: any explicitly named links to other subjects or
      cross-curricular themes (e.g. literacy, numeracy, key competencies)
    - assessment_objectives: the syllabus's own stated assessment
      objectives / aims for how students will be examined

    If a field has no support in the text, leave it empty rather than
    fabricating content — an empty list is a correct and expected answer
    for a syllabus section that doesn't mention cross-curricular links.

    Syllabus PDF text:
    {{ pdf_text }}

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}

// ============================================================================
// LineageTrace composer helper
// ============================================================================
// Helper that downstream Python callers (Dagster asset + DLT destination
// wrapper) invoke to populate the `lineage` field of every row emitted by
// `ExtractCurriculumSyllabus`. Centralised here so the contract is defined
// next to the consumer.
//
// Per openspec R28 (BAML LineageTrace extension).

// ============================================================================
// Backward-compatibility alias (BIEP v1 — Phase 1.3 migration)
// ============================================================================
// The 8 per-subject DLT sources historically called
// `b.ExtractLeavingCertSyllabus` from `baml/education/pdfs/leaving_cert_syllabus.baml`.
// That legacy function is now `## REMOVED` (per the 1.2.1 task) and
// replaced by this canonical `ExtractCurriculumSyllabus`. Any caller that
// still passes legacy kwargs will be transparently routed here.
