// BAML template: British Isles Grading System Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 12 stub prompts in
// `british_isles/_shared/grading/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 12 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor(input: string) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting grading system data (boundaries, distributions, comparability) from a British Isles exam board PDF.

    Source type: PDF text from a grade boundaries bulletin

    Extract:
    - exam_board: the exam board
    - subject: the subject slug
    - year: the exam year
    - grade_boundaries: map of grade → minimum mark
    - grade_distribution: list of grade distribution entries (count + percentage)

    {% if exam_board == 'AQA' %}
    - Grades are 1-9 (with 9 being highest)
    {% elif exam_board == 'Edexcel' %}
    - Grades are 1-9 (with 9 being highest)
    {% endif %}

    Grade boundaries are released annually after the exam. Always capture the year explicitly.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
