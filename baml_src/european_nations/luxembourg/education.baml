// Luxembourg education extraction BAML schema.

class LuxembourgSubjectCurriculum {
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("Official language of the row (lb,fr,de)")
  subject string @description("Subject slug (mathematics, chemistry, biology, physics, language, computing_science)")
  grade_level string? @description("Stage or grade (e.g. primary, lower-secondary, upper-secondary, vocational)")
  title string
  learning_outcomes string[] @description("Bulleted learning-outcome statements")
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractLuxembourgSubjectCurriculum(
  nation: string,
  language: string,
  subject: string,
  text: string
) -> LuxembourgSubjectCurriculum {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
