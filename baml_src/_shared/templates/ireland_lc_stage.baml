// BAML template: Ireland Leaving Cert Stage Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 8 stub prompts in
// `british_isles/ireland/education/stages/upper_secondary.baml/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 8 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor_IrelandLcStage(
  text: string
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert Irish Leaving Certificate (Senior Cycle) curriculum extractor for the 14 NCCA LC subjects.

    Source type: PDF text from NCCA syllabus documents

    Extract:
    - subject: the LC subject slug
    - level: the level (OL, HL, FDN)
    - module_topics: list of module / strand topics
    - learning_outcomes: list of LOs with codes (LC-<SUBJ>-LO-NNN)
    - assessment_objectives: NCCA assessment objectives

    {% if subject == 'LCSubjectSlug.MATHEMATICS' %}
    - Topics follow the 5 syllabus strands
    - LO codes use prefix `LC-MATH-LO-NNN`
    {% elif subject == 'LCSubjectSlug.CHEMISTRY' %}
    - Topics follow the 4 chemistry strands
    - LO codes use prefix `LC-CHEM-LO-NNN`
    {% endif %}

    The LC syllabus structure is well-documented by NCCA. Cross-link LOs to the NCCA published syllabus documents.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
