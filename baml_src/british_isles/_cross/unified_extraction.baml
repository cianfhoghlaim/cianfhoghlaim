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
// Per the british-isles-education-pipeline (BIEP) v1 spec
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
//   "mathematics", "chemistry", "geography", "gaeilge"
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
) -> LCSyllabus {  client ExtractEn
  // Real extraction prompt (2026-08-06 token-plan-apis change, Phase 2b).
  // The previous placeholder rendered a
  // system-only chat with no user content, which the MiniMax-M3 endpoint
  // rejects with 400 "chat content is empty". Style follows the working
  // ExtractUKQualSpec prompt in british_isles/england/education/
  // curriculum_syllabus.baml.
  prompt #"
    You are extracting the official NCCA Leaving Certificate syllabus for the
    subject {{ subject }} from the document text below (language: {{ language }}).

    Extract:
    - subject: the LC6Subject enum value matching {{ subject }}
      (mathematics -> MATHEMATICS, chemistry -> CHEMISTRY,
      geography -> GEOGRAPHY, gaeilge -> GAEILGE, english -> ENGLISH,
      computer_science -> COMPUTER_SCIENCE).
    - language: EN if {{ language }} is "en", GA if {{ language }} is "ga".
    - source_pdf: the PDF filename if it appears in the text; otherwise "".
    - source_pages: the PDF page count if stated in the text; otherwise null.
    - level: the NCCA stage if stated (LC_FL / LC_OL / LC_HL / JC); otherwise null.
    - topic_count: the total number of top-level topics / modules / strands
      in the syllabus, counted from the actual text.
    - learning_outcome_count: the total number of learning outcomes across
      all topics, counted from the actual text.
    - document: the full SyllabusDocument (module_topics with their learning
      outcomes, cross_curricular themes, assessment_objectives).
    - extracted_at: the current ISO datetime.
    - extracted_by: always "lc6_unified_extractor".

    Count carefully from the actual text; do not invent topics or outcomes.
    Output exactly one complete JSON object. Never use ellipses (...) or
    comments; list every module_topic in full with all of its
    learning_outcomes, however long the list is.
    document.stage MUST be one of JC / LC_OL / LC_HL / LC_FDN, never null —
    for a combined Ordinary+Higher syllabus document use LC_HL.
    document.source_pages: the page count if stated in the text, else null.

    {{ _.role("user") }}
    Document text (subject: {{ subject }}, language: {{ language }}):

    {{ text }}

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

function ExtractMathSyllabus(
  text: string,
  language: string
) -> LCSyllabus {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#

}

function ExtractChemSyllabus(text: string, language: string) -> LCSyllabus {  client ExtractEn
  // Real extraction prompt (2026-08-06 token-plan-apis change, Phase 2b) —
  // behaves exactly like ExtractLC6Syllabus with subject pinned to chemistry.
  // The previous placeholder rendered a system-only chat that the MiniMax-M3
  // endpoint rejects with 400 "chat content is empty".
  prompt #"
    You are extracting the official NCCA Leaving Certificate CHEMISTRY
    syllabus from the document text below (language: {{ language }}).

    Extract:
    - subject: CHEMISTRY (pinned).
    - language: EN if {{ language }} is "en", GA if {{ language }} is "ga".
    - source_pdf: the PDF filename if it appears in the text; otherwise "".
    - source_pages: the PDF page count if stated in the text; otherwise null.
    - level: the NCCA stage if stated (LC_OL / LC_HL); otherwise null.
    - topic_count: the total number of top-level topics / modules / strands
      in the syllabus, counted from the actual text.
    - learning_outcome_count: the total number of learning outcomes across
      all topics, counted from the actual text.
    - document: the full SyllabusDocument (module_topics with their learning
      outcomes, cross_curricular themes, assessment_objectives).
    - extracted_at: the current ISO datetime.
    - extracted_by: always "lc6_unified_extractor".

    Count carefully from the actual text; do not invent topics or outcomes.
    Output exactly one complete JSON object. Never use ellipses (...) or
    comments; list every module_topic in full with all of its
    learning_outcomes, however long the list is.
    document.stage MUST be one of JC / LC_OL / LC_HL / LC_FDN, never null —
    for the combined Ordinary+Higher chemistry syllabus use LC_HL.
    document.source_pages: the page count if stated in the text, else null.

    {{ _.role("user") }}
    Document text (subject: chemistry, language: {{ language }}):

    {{ text }}

    {{ ctx.output_format }}
  "#

}

function ExtractGeogSyllabus(
  text: string,
  language: string
) -> LCSyllabus {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#

}

function ExtractGaelSyllabus(
  text: string,
  language: string
) -> LCSyllabus {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#

}

function ExtractEnglSyllabus(
  text: string,
  language: string
) -> LCSyllabus {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#

}

function ExtractCompSyllabus(
  text: string,
  language: string
) -> LCSyllabus {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#

}
