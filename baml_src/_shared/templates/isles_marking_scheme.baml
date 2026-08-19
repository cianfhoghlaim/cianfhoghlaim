// BAML template: British Isles Marking Scheme Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 6 stub prompts in
// `british_isles/_shared/marking/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 6 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor(input: string) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured marking scheme guidelines from a British Isles exam marking PDF.

    Source type: PDF text from a marking scheme / chief examiner report

    Extract:
    - exam_board: the exam board (AQA, OCR, Edexcel, NCCA, SQA, CBAC, CCEA)
    - subject: the subject slug
    - year: the exam year
    - marking_bands: list of marking bands with mark ranges
    - common_mistakes: list of common student mistakes
    - model_answers: list of model answers for high-mark questions

    {% if exam_board == 'AQA' %}
    - AQA marking bands are 5-level (1-5)
    {% elif exam_board == 'OCR' %}
    - OCR marking bands are A-E
    {% endif %}

    Marking schemes differ by exam board. Always capture the board-specific band naming convention.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
