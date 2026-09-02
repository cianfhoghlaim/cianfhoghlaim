// BAML schema: Northern Ireland extraction BAML
//
// Per the 2026-09-01-ni-jurisdiction-completion-v1 change
// (Steps 4-8 of the cianfhoghlaim-nua v6 era plan). The canonical
// NorthernIreland extraction pattern — applies the NCCE 5-step pattern
// (raw PDF → DLT → BAML → CocoIndex → Convex → A2UI) to the NorthernIreland
// jurisdiction.
//
// Vernacular overlay: Irish (ga) medium (Gaeltacht).
// All classes have text_en + text_ga fields (always bilingual per
// operator direction).
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src

enum NIStage {
  AISTEAR
  PRIMARY
  JUNIOR_CYCLE
  LEAVING_CERT
  UNIVERSITY
}

enum NIAwardDescriptor {
  EXCEPTIONAL
  ABOVE_EXPECTATIONS
  IN_LINE_WITH_EXPECTATIONS
  BELOW_EXPECTATIONS
  FAR_BELOW_EXPECTATIONS
}

enum NIKeyCompetency {
  COMMUNICATING
  INFORMATION_PROCESSING
  CRITICAL_AND_CREATIVE_THINKING
  PERSONAL_EFFECTIVENESS
  WORKING_WITH_OTHERS
}

class NISubjectSpec {
  stage NIStage
  subject_slug string
  display_name string
  display_name_ga string
  display_name_local string
  award_descriptor NIAwardDescriptor
  descriptor_vocabulary NIAwardDescriptor[]
  key_competencies NIKeyCompetency[]
  source_pdf string
  source_url string
  language string
  year int
  page int
}

class GaeltachtOverlay {
  gaeltacht_school bool
  irish_medium_stream bool
}

function ExtractNorthernIrelandSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: NIStage,
  source_url: string
) -> NISubjectSpec {
  client Primary
  prompt #"
    { _.role("user") }
    You are an expert at extracting the official Northern Ireland subject
    specification from the PDF text. The source is the canonical
    NorthernIreland official document at { source_url }.

    PDF text: { pdf_text }

    Return the canonical NISubjectSpec.

    { ctx.output_format }
  "#
}

test ni_subject_spec_sanity {
  functions [ExtractNorthernIrelandSubjectSpec]
  args {
    pdf_text "Sample Northern Ireland subject specification text..."
    subject_slug "mathematics"
    stage NIStage.LEAVING_CERT
    source_url "https://www.gov.uk/example-spec.pdf"
  }
}
