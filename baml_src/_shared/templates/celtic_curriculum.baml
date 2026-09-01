// BAML template: Celtic Curriculum Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 7 stub prompts in
// `celtic/curriculum/celtic_curriculum.baml/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 7 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor_CelticCurriculum(
  text: string
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting Celtic-language curriculum data from a national curriculum document.

    Source type: PDF text from a Celtic-nation curriculum authority

    Extract:
    - language: the Celtic language
    - stage: the educational stage (primary, secondary, etc.)
    - learning_outcomes: list of learning outcomes with codes
    - assessment_objectives: list of assessment objectives
    - cross_curricular: cross-subject links

    {% if language == 'ga' %}
    - NCCA LO codes use prefix `JC-GAEL-LO-NNN`
    {% elif language == 'cy' %}
    - CBAC (Welsh) LO codes use prefix `CBAC-CYM-LO-NNN`
    {% endif %}

    The 6 Celtic languages are: ga (Irish), cy (Welsh), gd (Scottish Gaelic), br (Breton), kw (Cornish), gv (Manx). Each has its own national curriculum authority.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
