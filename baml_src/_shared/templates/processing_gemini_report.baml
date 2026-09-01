// BAML template: Gemini Deep Research Report Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 10 stub prompts in
// `processing/gemini_deep_research/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 10 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor_ProcessingGeminiReport(
  text: string
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured metadata from a Gemini deep research report PDF.

    Source type: PDF text (gemini_deep_research_*.pdf)

    Extract:
    - title: the report title
    - summary: 2-3 sentence executive summary
    - findings: list of key findings with section headings
    - citations: list of cited URLs with section context
    - methodology: description of the research methodology used

    

    The Gemini reports are typically 20-50 page PDFs with rich citation networks. Preserve citation context (page number + section).

    {{ ctx.output_format }}

    {{ text }}
  "#
}
