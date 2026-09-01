// BAML template: British Isles Education Statistics Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 5 stub prompts in
// `british_isles/_shared/statistics/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 5 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor_IslesStatistics(
  text: string
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting education statistics from a British Isles statistical bulletin.

    Source type: PDF text from a government statistics office (CSO, ONS, NRS, NISRA)

    Extract:
    - publication: the canonical publication name
    - publication_date: ISO 8601 publication date
    - cohort: the cohort year(s) covered
    - data_points: list of data points with year + value + jurisdiction
    - methodology: link or description of the methodology

    {% if jurisdiction == 'ireland' %}
    - Use CSO.ie source URL pattern
    {% elif jurisdiction == 'england' %}
    - Use explore-education-statistics.service.gov.uk
    {% endif %}

    Statistics are versioned by year. Always capture the publication_date + the cohort year separately.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
