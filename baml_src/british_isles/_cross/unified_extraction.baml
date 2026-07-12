// BAML unified extractor: ExtractLC6Syllabus
//
// The canonical BIEP v1 unified syllabus extractor. Routes the
// per-subject NCCA syllabus extraction through a single
// `ExtractLC6Syllabus(subject, text, language) -> LCSyllabus`
// function, then dispatches to the per-subject extractor based
// on the `subject` argument.
//
// This is the foundation for the BIEP v1 per-subject agent +
// dashboard + study-tool work (Picks 2-5): a single call site
// replaces six different `b.ExtractCurriculumSyllabus(text)`
// invocations and gives the caller a discriminated
// `LCSyllabus` return type that carries the per-subject
// discriminator.
//
// Per the british-isles-education-pipeline (BIEP) v1 spec,
// the 6 in-scope subjects are: Mathematics, Chemistry,
// Geography, Gaeilge, English, Computer Science (the user's
// locked plan). Applied Mathematics and History are out of
// scope per the user.
//
// Routes to the `Default` client (minimax-m3 per commit
// `667635dfd`).
//
// Re-gen: `cd cianfhoghlaim && mise run baml:generate`

// ============================================================================
// LCSyllabus (the unified return type)
// ============================================================================
//
// A discriminated Pydantic class that carries the per-subject
// discriminator. The `discriminator` field is one of:
//   "mathematics", "chemistry", "geography", "gaeilge",
//   "english", "computer_science"
// and selects which per-subject syllabus class is present in
// the `payload` field.
//
// The legacy per-subject extractors (ExtractMathSyllabus /
// ExtractChemSyllabus / etc.) still work for backwards
// compatibility; the unified `ExtractLC6Syllabus` is the
// canonical entry point for the BIEP v1 per-subject pipeline.

enum LC6Subject {
  MATHEMATICS      @description("Leaving Certificate Mathematics (LC-2015 spec)")
  CHEMISTRY        @description("Leaving Certificate Chemistry (OL + HL)")
  GEOGRAPHY        @description("Leaving Certificate Geography (OL + HL)")
  GAEILGE          @description("Leaving Certificate Gaeilge (FL + OL + HL, taught in Irish)")
  ENGLISH          @description("Leaving Certificate English (OL + HL)")
  COMPUTER_SCIENCE @description("Leaving Certificate Computer Science (OL + HL, introduced 2020)")
}

enum LC6Language {
  EN @description("English-language syllabus")
  GA @description("Irish (Gaeilge) language syllabus")
}

class LCSyllabus {
  subject LC6Subject @description("The per-subject discriminator; selects the active payload")
  language LC6Language @description("The source language of the syllabus PDF")
  source_pdf string @description("Path or filename of the source NCCA syllabus PDF")
  source_pages int? @description("PDF page count, when known")
  level string? @description("NCCA stage: 'LC_FL' / 'LC_OL' / 'LC_HL' / 'JC' (Foundation / Ordinary / Higher / Junior Cycle)")
  topic_count int @description("Total number of topics / modules extracted from the syllabus")
  learning_outcome_count int @description("Total number of learning outcomes across all topics")
  // Per-subject syllabus body — the canonical SyllabusDocument
  // (from baml/education/lc_extraction/curriculum_syllabus.baml)
  // is the typed return of `ExtractCurriculumSyllabus`; we embed
  // it here so downstream agents have one stable shape.
  document SyllabusDocument
  // When did this syllabus snapshot come into the lakehouse?
  extracted_at string @description("ISO datetime the extraction ran")
  extracted_by string @description("Always 'lc6_unified_extractor' for this file")
}

// ============================================================================
// Unified extractor
// ============================================================================

function ExtractLC6Syllabus(
  subject: string,
  text: string,
  language: string,
) -> LCSyllabus {
  client Default
  prompt #"
    You are an Irish Leaving Certificate syllabus expert for the
    {{ subject }} subject. Given the text of a NCCA Leaving
    Certificate syllabus PDF (one of: Mathematics, Chemistry,
    Geography, Gaeilge, English, Computer Science), extract the
    structured syllabus and return it in the canonical LCSyllabus
    shape.

    Language: {{ language }} (en or ga)
    Source text:
    ---
    {{ text }}
    ---

    Required fields:
      - subject: the canonical LC6Subject slug (lowercase string)
      - language: 'en' or 'ga'
      - topic_count: integer
      - learning_outcome_count: integer
      - document: the full SyllabusDocument (modules, LOs, etc.)
      - level: 'LC_FL' / 'LC_OL' / 'LC_HL' / 'JC' when known

    Preserve Irish-language fidelity: every syllabus must keep its
    bilingual character where attested. Do NOT translate the
    Irish names to English in `name_ga`.

    {{ ctx.output_format }}
  "#
}

// -----------------------------------------------------------------------------
// Per-subject thin wrappers (the canonical dispatcher pattern)
// -----------------------------------------------------------------------------
//
// The BAML language does not support dynamic dispatch from
// inside a `function` prompt, so we expose six thin wrappers
// for the common case where the caller already knows the
// subject. Each is a one-line alias for ExtractLC6Syllabus
// with the `subject` argument pinned.

function ExtractMathSyllabus(text: string, language: string) -> LCSyllabus {
  client Default
  prompt #"
    {{ ExtractLC6Syllabus(subject="mathematics", text=text, language=language) }}
  "#
}

function ExtractChemSyllabus(text: string, language: string) -> LCSyllabus {
  client Default
  prompt #"
    {{ ExtractLC6Syllabus(subject="chemistry", text=text, language=language) }}
  "#
}

function ExtractGeogSyllabus(text: string, language: string) -> LCSyllabus {
  client Default
  prompt #"
    {{ ExtractLC6Syllabus(subject="geography", text=text, language=language) }}
  "#
}

function ExtractGaelSyllabus(text: string, language: string) -> LCSyllabus {
  client Default
  prompt #"
    {{ ExtractLC6Syllabus(subject="gaeilge", text=text, language=language) }}
  "#
}

function ExtractEnglSyllabus(text: string, language: string) -> LCSyllabus {
  client Default
  prompt #"
    {{ ExtractLC6Syllabus(subject="english", text=text, language=language) }}
  "#
}

function ExtractCompSyllabus(text: string, language: string) -> LCSyllabus {
  client Default
  prompt #"
    {{ ExtractLC6Syllabus(subject="computer_science", text=text, language=language) }}
  "#
}