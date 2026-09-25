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
// Phase 1.4 (2026-09-25 5-phase Celtic overhaul): the template now
// calls `StandardizeIrish` (from baml_src/celtic/standardize.baml)
// pre-extraction to normalise pre-1936 / dialectal Irish spellings
// into modern standard Irish. The before/after transformation is
// recorded in `dialect_variants` on the LCSyllabusDocument output
// (added by the same change in baml_src/british_isles/_shared/lc_extraction_template.baml).
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

    Pre-extraction standardisation (Phase 1.4):
      The `text` argument has been pre-processed by StandardizeIrish
      (see baml_src/celtic/standardize.baml:StandardizeIrish):
        1. Wikitext markup stripped (ref, template, image, span)
        2. TN6 hyperlinks stripped (markdown + HTML + bare URLs)
        3. Teanglann audio links captured (separate field on output)
        4. Caighdean Oifigiúil standardisation applied (pre-1936 → modern)
        5. Per-segment diffs recorded in dialect_variants[]

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
