// BAML template: Ireland Junior Cycle Stage Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 8 stub prompts in
// `british_isles/ireland/education/stages/junior_cycle.baml/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 8 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor_IrelandJcStage(
  text: string
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert Irish Junior Cycle (ages 12-15) curriculum extractor for the 8 NCCA JC subjects.

    Source type: PDF text from NCCA Junior Cycle specifications

    Extract:
    - subject: the JC subject slug
    - learning_outcomes: list of LOs with codes (JC-<SUBJ>-LO-NNN)
    - strand_elements: list of strand elements
    - cba_objectives: Classroom-Based Assessment objectives
    - assessment_objectives: final exam assessment objectives

    {% if subject == 'JCSubjectSlug.MATHEMATICS' %}
    - Topics span Number, Algebra, Functions, Geometry, Statistics
    - LO codes use prefix `JC-MATH-LO-NNN`
    {% elif subject == 'JCSubjectSlug.ENGLISH' %}
    - Capture the prescribed texts under `prescribed_texts`
    {% endif %}

    Junior Cycle has a different assessment structure (CBA + final exam) than Leaving Cert. Always capture both the CBA objectives and the final exam objectives.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
