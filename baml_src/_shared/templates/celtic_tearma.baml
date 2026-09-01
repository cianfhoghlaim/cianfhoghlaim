// BAML template: Tearma.ie Terminology Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 26 stub prompts in
// `celtic/gaois/tearma.baml/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 26 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor_CelticTearma(
  text: string
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured terminology data from Tearma.ie (the Irish National Terminology Database).

    Source type: JSON response or HTML page from tearma.ie

    Extract:
    - term_ga: the Irish term
    - term_en: the English term
    - domains: list of subject domains
    - definitions: list of term definitions with language tag
    - grammar: grammatical info (gender, declension, verb form)
    - usage_examples: list of EN/GA usage examples

    {% if language == 'ga' %}
    - Preserve the full Irish grammar (gender + declension)
    {% elif language == 'en' %}
    - The grammar field is optional for English-only terms
    {% endif %}

    Tearma.ie is the authoritative Irish terminology source. Cross-reference the term with related Dúchas / Gaois records when the definitions overlap.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
