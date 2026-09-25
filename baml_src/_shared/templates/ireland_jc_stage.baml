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
// Phase 1.5 (2026-09-25 5-phase Celtic overhaul): the template now
// calls `StandardizeIrish` (from baml_src/celtic/standardize.baml)
// pre-extraction to normalise pre-1936 / dialectal Irish spellings
// into modern standard Irish. The before/after transformation is
// recorded in `dialect_variants` on the output document.
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

    Pre-extraction standardisation (Phase 1.5):
      The `text` argument has been pre-processed by StandardizeIrish
      (see baml_src/celtic/standardize.baml:StandardizeIrish):
        1. Wikitext markup stripped (ref, template, image, span)
        2. TN6 hyperlinks stripped (markdown + HTML + bare URLs)
        3. Teanglann audio links captured (separate field on output)
        4. Caighdean Oifigiúil standardisation applied (pre-1936 → modern)
        5. Per-segment diffs recorded in dialect_variants[]

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
