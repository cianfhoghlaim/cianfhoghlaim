// BAML template: European Nations Curriculum Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 13 stub prompts in
// `european_nations/_shared/curriculum/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 13 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor(input: string) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting curriculum data from a European national education authority.

    Source type: PDF text from a European national education ministry

    Extract:
    - country: the country code (alpha-2)
    - stage: the educational stage (primary, lower-secondary, upper-secondary)
    - subject: the subject slug
    - learning_outcomes: list of LOs with country-specific codes
    - assessment_methods: list of assessment methods used

    {% if country == 'FR' %}
    - French cycle nomenclature: primaire / collège / lycée
    {% elif country == 'DE' %}
    - German Land-specific Länder codes
    {% endif %}

    European curriculum structures vary widely. Use the country code as the primary branching signal.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
