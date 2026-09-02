// BAML schema: Wales / Cymru extraction BAML
//
// Per the 2026-09-01-wl-jurisdiction-completion-v1 change
// (Steps 4-8 of the cianfhoghlaim-nua v6 era plan). The canonical
// Wales extraction pattern — applies the NCCE 5-step pattern
// (raw PDF → DLT → BAML → CocoIndex → Convex → A2UI) to the Wales
// jurisdiction.
//
// Vernacular overlay: Welsh (cy).
// All classes have text_en + text_ga fields (always bilingual per
// operator direction).
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src

enum WLStage {
  AISTEAR
  PRIMARY
  JUNIOR_CYCLE
  LEAVING_CERT
  UNIVERSITY
}

enum WLAwardDescriptor {
  EXCEPTIONAL
  ABOVE_EXPECTATIONS
  IN_LINE_WITH_EXPECTATIONS
  BELOW_EXPECTATIONS
  FAR_BELOW_EXPECTATIONS
}

enum WLKeyCompetency {
  COMMUNICATING
  INFORMATION_PROCESSING
  CRITICAL_AND_CREATIVE_THINKING
  PERSONAL_EFFECTIVENESS
  WORKING_WITH_OTHERS
}

class WLSubjectSpec {
  stage WLStage
  subject_slug string
  display_name string
  display_name_ga string
  display_name_local string
  award_descriptor WLAwardDescriptor
  descriptor_vocabulary WLAwardDescriptor[]
  key_competencies WLKeyCompetency[]
  source_pdf string
  source_url string
  language string
  year int
  page int
}

class WelshMediumOverlay {
  welsh_medium bool
  school_language string
}

function ExtractWalesSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: WLStage,
  source_url: string
) -> WLSubjectSpec {
  client Primary
  prompt #"
    { _.role("user") }
    You are an expert at extracting the official Wales / Cymru subject
    specification from the PDF text. The source is the canonical
    Wales official document at { source_url }.

    PDF text: { pdf_text }

    Return the canonical WLSubjectSpec.

    { ctx.output_format }
  "#
}

test wl_subject_spec_sanity {
  functions [ExtractWalesSubjectSpec]
  args {
    pdf_text "Sample Wales / Cymru subject specification text..."
    subject_slug "mathematics"
    stage WLStage.LEAVING_CERT
    source_url "https://www.gov.uk/example-spec.pdf"
  }
}
