// BAML schema: Scotland / Alba extraction BAML
//
// Per the 2026-09-01-sc-jurisdiction-completion-v1 change
// (Steps 4-8 of the cianfhoghlaim-nua v6 era plan). The canonical
// Scotland extraction pattern — applies the NCCE 5-step pattern
// (raw PDF → DLT → BAML → CocoIndex → Convex → A2UI) to the Scotland
// jurisdiction.
//
// Vernacular overlay: Scottish Gaelic (gd).
// All classes have text_en + text_ga fields (always bilingual per
// operator direction).
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src

enum SCStage {
  AISTEAR
  PRIMARY
  JUNIOR_CYCLE
  LEAVING_CERT
  UNIVERSITY
}

enum SCAwardDescriptor {
  EXCEPTIONAL
  ABOVE_EXPECTATIONS
  IN_LINE_WITH_EXPECTATIONS
  BELOW_EXPECTATIONS
  FAR_BELOW_EXPECTATIONS
}

enum SCKeyCompetency {
  COMMUNICATING
  INFORMATION_PROCESSING
  CRITICAL_AND_CREATIVE_THINKING
  PERSONAL_EFFECTIVENESS
  WORKING_WITH_OTHERS
}

class SCSubjectSpec {
  stage SCStage
  subject_slug string
  display_name string
  display_name_ga string
  display_name_local string
  award_descriptor SCAwardDescriptor
  descriptor_vocabulary SCAwardDescriptor[]
  key_competencies SCKeyCompetency[]
  source_pdf string
  source_url string
  language string
  year int
  page int
}

class ScottishGaelicOverlay {
  gaelic_medium bool
  cfe_gaelic bool
}

function ExtractScotlandSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: SCStage,
  source_url: string
) -> SCSubjectSpec {
  client Primary
  prompt #"
    { _.role("user") }
    You are an expert at extracting the official Scotland / Alba subject
    specification from the PDF text. The source is the canonical
    Scotland official document at { source_url }.

    PDF text: { pdf_text }

    Return the canonical SCSubjectSpec.

    { ctx.output_format }
  "#
}

test sc_subject_spec_sanity {
  functions [ExtractScotlandSubjectSpec]
  args {
    pdf_text "Sample Scotland / Alba subject specification text..."
    subject_slug "mathematics"
    stage SCStage.LEAVING_CERT
    source_url "https://www.gov.uk/example-spec.pdf"
  }
}
