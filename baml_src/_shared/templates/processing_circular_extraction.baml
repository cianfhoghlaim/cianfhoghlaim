// BAML template: Government Circular Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 6 stub prompts in
// `processing/circular_extraction.baml/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 6 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor_ProcessingCircularExtraction(
  text: string
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured metadata from an Irish government education circular.

    Source type: PDF text from gov.ie / Department of Education

    Extract:
    - circular_number: the canonical circular number (e.g. '0059/2026')
    - issuing_department: the department that issued the circular
    - issue_date: ISO 8601 date of issue
    - subject: the subject of the circular
    - summary: 2-3 sentence executive summary
    - action_required: what schools/principals are required to do

    

    The circular_number follows the pattern NNNN/YYYY. Cross-link to the affected LC subjects when possible.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
