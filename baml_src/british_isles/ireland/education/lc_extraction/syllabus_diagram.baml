// BAML schema: Syllabus Diagram Extraction (molmo2-8b pointing)
//
// Used by the LC5-subject pipeline to extract diagrams / figures / charts
// from syllabi that are not pure text. The 06_diagram_detection
// notebook (and the LC5 layer-2 materials pipeline) routes diagram
// extraction through `molmo2-8b` (Transformers backend, specialist
// for diagram pointing per v4 registry).
//
// Particularly relevant for:
//   - chemistry: molecular structure diagrams, apparatus diagrams
//   - geography: maps, climate graphs, cross-sections
//   - computer_science: flowcharts, logic gates, network topology
//   - mathematics: geometric shapes, function graphs (less common in syllabus)
//   - gaeilge: rare; mostly text
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate

enum DiagramKind {
  EXTRACTED_FROM_DOCUMENT
}

enum RegionRole {
  TITLE
  CAPTION
  AXIS_LABEL
  KEY_COMPONENT          @description("Pointed at by molmo2-8b")
  DATA_POINT
  LEGEND_ENTRY
  ANNOTATION
  BACKGROUND
}

class DiagramRegion {
  // Bounding box in PDF coordinates (PDF uses bottom-left origin; we keep raw)
  bbox_x_min float
  bbox_y_min float
  bbox_x_max float
  bbox_y_max float
  page_number int
  role RegionRole
  text_content string?     @description("Any text inside this region")
}

class SyllabusDiagram {
  diagram_id string
  kind DiagramKind
  caption_en string?
  caption_ga string?
  page_number int
  source_pdf string
  subject string

  // Pointing-data from molmo2-8b (the v4 registry's specialist for this task)
  pointing_model string        @description("e.g. 'allenai/Molmo2-8B'")
  confidence_score float       @description("0.0 - 1.0; per-page confidence")

  // The region decomposition (bounding boxes + roles)
  regions DiagramRegion[]

  // Cross-link to the syllabus Learning Outcome(s) the diagram illustrates
  related_lo_ids string[]

  // Lineage provenance (R28). Composed from
  // `lc_extraction/_shared/lineage_trace.baml`.
  lineage LineageTrace?
}

// ============================================================================
// BAML function: Syllabus Diagram Extraction (BIEP v3)
// ============================================================================
//
// Per the 2026-08-13-biep-v3-systematic-download-ireland-england-v1 change,
// this `ExtractSyllabusDiagram` function is the v3 canonical entry point.
// The `SyllabusDiagram` class above is the return type.
//
// The function is invoked by the 4-path OCR ensemble's Diagram Path
// (which uses `molmo2-8b` for pointing); the result is written to
// `cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.syllabus_diagram`.
//
// Per the 2026-08-08-lakehouse-extensive-hydration-v1 change: this
// function used to be declared `client BIEPV3Vision` (a real,
// correctly-configured vision client routing through litellm ->
// llama-swap -> qwen3-vl-8b) but had no `image` parameter at all --
// vision framing with no pixels behind it, confirmed by the one real
// caller's own code comment (`tuatha/asset_generation/fibo/assets.py::
// fibo_configs_from_syllabus_diagrams`). `image` is now optional
// (`image[]?`) rather than required so existing text-only callers keep
// working unchanged; callers that render and pass real page images get
// genuine vision-based diagram detection instead of caption-only
// text inference. See `meaisinfhoghlaim/document_factory/
// pdf_to_image_bridge.py` for the PDF-page-to-`baml_py.Image` adapter.

function ExtractSyllabusDiagram(
  pdf_text: string,
  page_text: string?,
  page_number: int?,
  subject: string?,
  subject_language: string?,
  image: image[]?,
) -> SyllabusDiagram[] {
  client BIEPV3Vision
  prompt #"
    You are an expert at identifying diagrams in Irish Leaving Certificate
    {{ subject }} syllabi in {{ subject_language }}.

    For each diagram on this page, extract:
    - A diagram_id (e.g. 'diagram_001')
    - The diagram kind (always EXTRACTED_FROM_DOCUMENT)
    - Caption in English (caption_en) if any
    - Caption in Irish (caption_ga) if any
    - The page number
    - The subject slug
    - The bounding box regions (in PDF coordinates; bottom-left origin)
    - Any text content within the regions
    - The pointing model (e.g. 'allenai/Molmo2-8B')
    - A confidence score (0.0 - 1.0)

    {% if image %}
    The rendered page image(s) follow -- use them as the primary source
    for diagram detection and bounding-box regions; the extracted text
    below is secondary context (captions, figure references) that may
    help you label what you see, but the image is ground truth for
    anything visual (shapes, layout, axes, apparatus, maps).
    {% for img in image %}
    {{ img }}
    {% endfor %}
    {% else %}
    No page image was provided for this call -- detect diagrams from
    textual evidence only (figure captions, "Figure N:" references in
    the text below). Do not fabricate bounding-box coordinates you
    cannot actually see; set a lower confidence_score to reflect that
    this is text-inferred, not vision-detected.
    {% endif %}

    PDF text:
    {{ pdf_text }}

    Page text:
    {{ page_text }}

    Page number:
    {{ page_number }}

    {{ _.role("user") }}
    {{ ctx.output_format }}
  "#
}
