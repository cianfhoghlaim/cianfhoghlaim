// BAML template: American Nations Law Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 7 stub prompts in
// `american_nations/_shared/law/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 7 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor_AmericanNationsLaw(
  text: string
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured legal data from an American (USA / Brazil / California) legal document.

    Source type: PDF text from a state or federal legal document

    Extract:
    - jurisdiction: the jurisdiction (US-Federal, US-CA, BR-Federal, BR-State, MX-Federal)
    - code_section: the canonical code section (e.g. 'Cal. Penal Code § 187')
    - title: the section title
    - effective_date: ISO 8601 effective date
    - summary: 2-3 sentence executive summary
    - amendments: list of amendments (if any)

    {% if jurisdiction == 'US-CA' %}
    - California codes are organized by subject area (Penal, Civil, etc.)
    {% elif jurisdiction == 'BR-Federal' %}
    - Brazilian federal laws use the LEI N pattern
    {% endif %}

    Legal documents have a strict citation convention. Always capture the canonical code_section as the primary identifier.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
