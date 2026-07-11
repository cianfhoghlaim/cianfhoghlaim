// SCT education extraction BAML schema (BIEP parity).

class SCTEducationDocument {
  url string @description("Canonical syllabus / document URL")
  language string @description("The official language of the row")
  nation string @description("ISO 3166-1 alpha-3 or British Isles legacy slug")
  subject string? @description("Subject slug (e.g. mathematics, chemistry)")
  exam_board string? @description("Awarding body (SQA)")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractSCTEducationDocument(
  nation: string,
  language: string,
  text: string
) -> SCTEducationDocument {
  client Claude
  prompt #"
    Extract the canonical education record from the following Scotland
    text. Preserve the canonical URL + the awarding body identifier.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
