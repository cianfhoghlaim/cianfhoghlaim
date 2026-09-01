// BAML template: Ireland University Module Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 21 stub prompts in
// `british_isles/ireland/education/university/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 21 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor_IrelandUniversityModule(
  text: string
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway (or Irish university) module syllabus data from PDF.

    Source type: PDF text from a university module descriptor

    Extract:
    - module_code: the canonical module code (e.g. 'MA216')
    - module_title: the module title
    - credits: ECTS credits
    - learning_outcomes: list of LOs
    - assessment_breakdown: breakdown of assessment weightings
    - prerequisites: list of prerequisite modules

    

    University module descriptors follow a common template. The module_code is the canonical identifier (cross-reference with the University of Galway module registry).

    {{ ctx.output_format }}

    {{ text }}
  "#
}
