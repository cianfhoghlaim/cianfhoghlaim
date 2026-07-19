// EN education extraction BAML schema (BIEP parity).

class ENEducationDocument {
  url string @description("Canonical syllabus / document URL")
  language string @description("The official language of the row")
  nation string @description("ISO 3166-1 alpha-3 or British Isles legacy slug")
  subject string? @description("Subject slug (e.g. mathematics, chemistry)")
  exam_board string? @description("Awarding body (AQA)")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractENEducationDocument(
  nation: string,
  language: string,
  text: string
) -> ENEducationDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
