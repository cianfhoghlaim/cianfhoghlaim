// BAML template: Author Archive Extractor
//
// Per the 2026-12-XX-mega-3d-baml-quality-v1 change (Phase 3:
// BAML bulk-quality). Replaces the 10 stub prompts in
// `processing/author_archive.baml/` with a single canonical extractor.
//
// Each stub function in the parent dir routes through this
// template via `baml_bulk_replace_stubs.py`. The template is
// shared (not duplicated per function) so a single improvement
// benefits all 10 extractors.
//
// Re-gen: `python scripts/baml_generate_templates.py`
// Re-apply: `python scripts/baml_bulk_replace_stubs.py`

function DomainExtractor_ProcessingAuthorArchive(
  text: string
) -> string {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting author/creator metadata from an archival document.

    Source type: PDF text + filename

    Extract:
    - author_name: full name of the primary author/creator
    - author_role: their role/title at time of creation
    - organization: the affiliated organization (if any)
    - publication_year: ISO year of publication or creation
    - archive_collection: the canonical archive collection name
    - shelfmark: the canonical shelfmark / call number

    

    The author archive includes a mix of academics, politicians, and educators. Use the document content (not the filename) to determine role and organization.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
