// NI law extraction BAML schema (BIEP parity).

class NILawDocument {
  url string @description("Canonical syllabus / document URL")
  language string @description("The official language of the row")
  nation string @description("ISO 3166-1 alpha-3 or British Isles legacy slug")
  subject string? @description("Subject slug (e.g. mathematics, chemistry)")
  exam_board string? @description("Awarding body (CCEA)")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractNILawDocument(
  nation: string,
  language: string,
  text: string
) -> NILawDocument {
  client Claude
  prompt #"
    Extract the canonical law record from the following Northern Ireland
    text. Preserve the canonical URL + the awarding body identifier.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
