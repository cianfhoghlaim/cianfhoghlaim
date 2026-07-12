// Netherlands education extraction BAML schema.

class NetherlandsSubjectCurriculum {
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("Official language of the row (nl)")
  subject string @description("Subject slug (mathematics, chemistry, biology, physics, language, computing_science)")
  grade_level string? @description("Stage or grade (e.g. primary, lower-secondary, upper-secondary, vocational)")
  title string
  learning_outcomes string[] @description("Bulleted learning-outcome statements")
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractNetherlandsSubjectCurriculum(
  nation: string,
  language: string,
  subject: string,
  text: string
) -> NLDSubjectCurriculum {
  client Claude
  prompt #"
    Extract the canonical subject curriculum record from the following
    Netherlands text. Preserve the subject slug, grade level,
    and the bulleted learning-outcome statements exactly.

    Nation: { nation }
    Language: { language }
    Subject: { subject }
    Text: { text }

    { ctx.output_format }
  "#
}
