// BAML schema: England extraction BAML
//
// Per the 2026-09-01-en-jurisdiction-completion-v1 change
// (Steps 4-8 of the cianfhoghlaim-nua v6 era plan). The canonical
// England extraction pattern — applies the NCCE 5-step pattern
// (raw PDF → DLT → BAML → CocoIndex → Convex → A2UI) to the England
// jurisdiction.
//
// Vernacular overlay: None (English-only).
// All classes have text_en + text_ga fields (always bilingual per
// operator direction).
//
// Re-gen: cd cianfhoghlaim && uv run baml-cli generate --from baml_src

enum ENStage {
  AISTEAR
  PRIMARY
  JUNIOR_CYCLE
  LEAVING_CERT
  UNIVERSITY
}

enum ENAwardDescriptor {
  EXCEPTIONAL
  ABOVE_EXPECTATIONS
  IN_LINE_WITH_EXPECTATIONS
  BELOW_EXPECTATIONS
  FAR_BELOW_EXPECTATIONS
}

enum ENKeyCompetency {
  COMMUNICATING
  INFORMATION_PROCESSING
  CRITICAL_AND_CREATIVE_THINKING
  PERSONAL_EFFECTIVENESS
  WORKING_WITH_OTHERS
}

class ENSubjectSpec {
  stage ENStage
  subject_slug string
  display_name string
  display_name_ga string
  display_name_local string
  award_descriptor ENAwardDescriptor
  descriptor_vocabulary ENAwardDescriptor[]
  key_competencies ENKeyCompetency[]
  source_pdf string
  source_url string
  language string
  year int
  page int
}



function ExtractEnglandSubjectSpec(
  pdf_text: string,
  subject_slug: string,
  stage: ENStage,
  source_url: string
) -> ENSubjectSpec {
  client Primary
  prompt #"
    { _.role("user") }
    You are an expert at extracting the official England subject
    specification from the PDF text. The source is the canonical
    England official document at { source_url }.

    PDF text: { pdf_text }

    Return the canonical ENSubjectSpec.

    { ctx.output_format }
  "#
}

test en_subject_spec_sanity {
  functions [ExtractEnglandSubjectSpec]
  args {
    pdf_text "Sample England subject specification text..."
    subject_slug "mathematics"
    stage ENStage.LEAVING_CERT
    source_url "https://www.gov.uk/example-spec.pdf"
  }
}
