// BAML schema: Isle of Man extraction BAML
//
// Per the 2026-09-01-im-jurisdiction-completion-v1 change
// (Steps 4-8 of the cianfhoghlaim-nua v6 era plan). The canonical
// IsleOfMan extraction pattern — applies the NCCE 5-step pattern
// (raw PDF → DLT → BAML → CocoIndex → Convex → A2UI) to the IsleOfMan
// jurisdiction.
//
// Vernacular overlay: Manx (gv).
// All classes have text_en + text_ga fields (always bilingual per
// operator direction).
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src

enum IMStage {
  AISTEAR
  PRIMARY
  JUNIOR_CYCLE
  LEAVING_CERT
  UNIVERSITY
}

enum IMAwardDescriptor {
  EXCEPTIONAL
  ABOVE_EXPECTATIONS
  IN_LINE_WITH_EXPECTATIONS
  BELOW_EXPECTATIONS
  FAR_BELOW_EXPECTATIONS
}

enum IMKeyCompetency {
  COMMUNICATING
  INFORMATION_PROCESSING
  CRITICAL_AND_CREATIVE_THINKING
  PERSONAL_EFFECTIVENESS
  WORKING_WITH_OTHERS
}

class IMSubjectSpec {
  stage IMStage
  subject_slug string
  display_name string
  display_name_ga string
  display_name_local string
  award_descriptor IMAwardDescriptor
  descriptor_vocabulary IMAwardDescriptor[]
  key_competencies IMKeyCompetency[]
  source_pdf string
  source_url string
  language string
  year int
  page int
}

class ManxOverlay {
  manx_medium bool
  bunscoill_gaelgagh bool
}

function ExtractIsleOfManSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: IMStage,
  source_url: string
) -> IMSubjectSpec {
  client Primary
  prompt #"
    { _.role("user") }
    You are an expert at extracting the official Isle of Man subject
    specification from the PDF text. The source is the canonical
    IsleOfMan official document at { source_url }.

    PDF text: { pdf_text }

    Return the canonical IMSubjectSpec.

    { ctx.output_format }
  "#
}

test im_subject_spec_sanity {
  functions [ExtractIsleOfManSubjectSpec]
  args {
    pdf_text "Sample Isle of Man subject specification text..."
    subject_slug "mathematics"
    stage IMStage.LEAVING_CERT
    source_url "https://www.gov.uk/example-spec.pdf"
  }
}
