// SCT law extraction BAML schema (BIEP parity).

class SCTLawDocument {
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

function ExtractSCTLawDocument(
  nation: string,
  language: string,
  text: string
) -> SCTLawDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
