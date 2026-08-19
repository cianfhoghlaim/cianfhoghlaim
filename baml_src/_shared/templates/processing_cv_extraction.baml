// BAML template: CV Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 5 stub prompts in
// `processing/cv_extraction.baml/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 5 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor(input: string) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured CV / resume data from a PDF.

    Source type: PDF text from a CV or resume

    Extract:
    - name: the full name of the candidate
    - email: primary email address
    - education: list of education entries (degree, institution, year)
    - experience: list of work experience entries
    - publications: list of publications (if present)

    

    The CV is used for portfolio/agent attribution. Preserve the canonical ordering of education + experience entries.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
