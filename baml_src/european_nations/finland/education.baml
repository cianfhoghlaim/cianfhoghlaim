// Finland education extraction BAML schema.

class FinlandSubjectCurriculum {
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("Official language of the row (fi,sv)")
  subject string @description("Subject slug (mathematics, chemistry, biology, physics, language, computing_science)")
  grade_level string? @description("Stage or grade (e.g. primary, lower-secondary, upper-secondary, vocational)")
  title string
  learning_outcomes string[] @description("Bulleted learning-outcome statements")
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractFinlandSubjectCurriculum(
  nation: string,
  language: string,
  subject: string,
  text: string
) -> FinlandSubjectCurriculum {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
