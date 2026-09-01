// BAML template: Game Content Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 6 stub prompts in
// `processing/game_content.baml/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 6 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor_ProcessingGameContent(
  text: string
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting structured game content from a game design document.

    Source type: markdown game design document

    Extract:
    - game_title: the title of the game
    - mechanics: list of game mechanics with descriptions
    - levels: list of levels with difficulty + learning objectives
    - subject_focus: the canonical subject slug (chemistry, mathematics, etc.)
    - age_range: the target age range (e.g. '12-15')

    

    The game content is used by the Túatha educational MMO. The age_range + subject_focus drive the cohort matching.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
