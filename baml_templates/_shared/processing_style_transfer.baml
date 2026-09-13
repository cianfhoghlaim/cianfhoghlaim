// BAML template: Style Transfer Spec Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 7 stub prompts in
// `processing/style_transfer.baml/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 7 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor(input: string) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at generating a style transfer specification from a reference prompt.

    Source type: free-form reference prompt text

    Extract:
    - style_name: the canonical style name (e.g. 'ukiyo-e', 'watercolor')
    - palette: list of hex colour codes for the style
    - line_work: description of the line work characteristics
    - era: the era or time period the style evokes
    - subject_matter: the typical subject matter for this style

    

    The style transfer spec drives a downstream image generation flow. The palette + line_work are the most critical fields.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
