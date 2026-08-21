// Switzerland education extraction BAML schema.

class SwitzerlandSubjectCurriculum {
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("Official language of the row (de,fr,it,rm)")
  subject string @description("Subject slug (mathematics, chemistry, biology, physics, language, computing_science)")
  grade_level string? @description("Stage or grade (e.g. primary, lower-secondary, upper-secondary, vocational)")
  title string
  learning_outcomes string[] @description("Bulleted learning-outcome statements")
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractSwitzerlandSubjectCurriculum(
  nation: string,
  language: string,
  subject: string,
  text: string
) -> SwitzerlandSubjectCurriculum {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
