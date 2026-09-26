// extract_syllabus_diagram.baml
// The Plan 4 BAML contract for extracting typed FIBOSyllabusDiagram records
// from REAL NCCA syllabus PDFs.
//
// Per the 2026-10-04-fibo-asset-pipeline-v1 saga change (Plan 4 of
// openspec/plans/2026-10-01-convergence-saga-v1.md).
//
// The 3 pipeline paths that share this contract:
// 1. `fibo_json_configs` (asset_generation/assets.py) — sample-concept fallback
// 2. `fibo_configs_from_syllabus_diagrams` (asset_generation/assets.py) —
//    docs-informed alternative that uses REAL NCCA syllabus figures
// 3. `tuatha/asset_generation/fibo/render.py` — the canonical render helper
//
// All extracts MUST carry full provenance (source_pdf + page_number +
// diagram_id) so diagrams can be traced back to the source figure.
//
// Note: class renamed to FIBOSyllabusDiagram to avoid the collision with the
// pre-existing `type SyllabusDiagram = LCSyllabusDiagram` alias in
// baml_src/british_isles/_shared/lc_extraction_template.baml.

class FIBOSyllabusDiagram {
  diagram_id string          @description("Deterministic: sha256(subject + page_number + caption)[:16]")
  subject string             @description("The NCCA subject (e.g. 'chemistry')")
  language string            @description("en | ga")
  page_number int            @description("The page where the diagram was found in the syllabus PDF")
  caption string             @description("The figure caption text (verbatim from the syllabus)")
  description string          @description("A 1-2 sentence description of what the diagram depicts")
  source_pdf string           @description("The path to the source PDF (absolute or relative to stedding/)")
  extraction_method string   @description("fibo_pdf_extract | manual | other")
  extracted_at string         @description("ISO 8601 timestamp of extraction")
}

function ExtractFIBOSyllabusDiagram(
  pdf_text string         @description("The raw text content of the syllabus PDF (from pdfplumber or pypdf)"),
  pdf_page_images string[]  @description("Optional list of base64-encoded page images (used for the VLM)"),
  source_pdf_path string   @description("The source PDF path"),
  subject string           @description("The NCCA subject (mathematics, chemistry, geography, etc.)"),
  language string          @description("en | ga"),
) -> FIBOSyllabusDiagram[] {
  client "Primary"
  prompt #"
    You are cataloguing diagrams in an NCCA syllabus PDF for the
    Cianfhoghlaim British Isles MMO asset pipeline.

    For each figure (diagram + chart + table-as-diagram) you find in the
    PDF text, produce one FIBOSyllabusDiagram record:
      - diagram_id: deterministic id (the system generates this)
      - subject: the NCCA subject (e.g. 'chemistry')
      - language: 'en' or 'ga'
      - page_number: the page where the figure was found
      - caption: the figure caption text verbatim
      - description: 1-2 sentences describing what the diagram depicts
      - source_pdf_path: the path argument

    NEVER fabricate diagrams. NEVER invent captions. If you cannot
    find any figures, return an empty list.
  "
}

function GenerateFiboConfigsFromSyllabus(
  diagrams FIBOSyllabusDiagram[],
  subject_prompt string   @description("The per-subject FIBO prompt template (from get_fibo_prompt)"),
  subject string,
  language string,
) -> string[] {
  client "Primary"
  prompt #"
    You are generating FIBO 2D educational diagram configs from REAL
    NCCA syllabus diagrams (NOT from sample concepts).

    For each diagram in the list, produce a FIBO JSON config string
    that captures the figure caption + the subject + language + the
    pedagogical intent + the per-element palette + a unique config_id.

    NEVER invent diagrams. Use ONLY the captions + descriptions in the
    input list.
  "
}

__all__ = ["FIBOSyllabusDiagram", "ExtractFIBOSyllabusDiagram", "GenerateFiboConfigsFromSyllabus"]
