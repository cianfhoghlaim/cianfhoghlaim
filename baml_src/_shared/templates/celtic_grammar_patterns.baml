// BAML template: Celtic Grammar Pattern Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 7 stub prompts in
// `celtic/grammar_patterns.baml/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 7 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor_CelticGrammarPatterns(
  text: string
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting Celtic-language grammar patterns from a pedagogical text.

    Source type: markdown pedagogical text

    Extract:
    - language: the Celtic language (ga, cy, gd, br, kw, gv)
    - pattern_name: the name of the grammar pattern (e.g. 'Irish mutations')
    - examples: list of example sentences demonstrating the pattern
    - rules: list of formal rules for the pattern
    - related_patterns: list of cross-references to related patterns

    {% if language == 'ga' %}
    - Capture the 4 Irish mutations (séimhiú + urú + eclipsis + lenition)
    {% elif language == 'cy' %}
    - Capture the Welsh soft + nasal + aspirate mutations
    {% endif %}

    Celtic mutations are the most distinctive feature. Always capture the input → output transformation explicitly.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
