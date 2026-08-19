// BAML template: Ireland Web Content Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 18 stub prompts in
// `british_isles/ireland/education/web/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 18 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor(input: string) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured data from Irish education web pages.

    Source type: markdown from a scraped web page (NCCA, gov.ie, examinations.ie)

    Extract:
    - title: the page title
    - publication_date: ISO 8601 publication date
    - subject_area: the subject area covered (if any)
    - key_findings: list of key findings or facts
    - links: list of related URLs

    {% if domain == 'ncca' %}
    - Cross-link to the canonical NCCA LO code
    {% elif domain == 'examinations_ie' %}
    - Capture the chief examiner's report insights
    {% endif %}

    The web content extractor handles pages from NCCA, gov.ie, examinations.ie, and Scoilnet. Always preserve the canonical URL.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
