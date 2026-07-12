// Malta education extraction BAML schema (EU nations full-depth).

class MaltaSubjectCurriculum {
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of the curriculum row")
  nation string @description("Country name")
  subject string @description("Subject slug (mathematics, chemistry, biology, physics, language, computing_science)")
  grade_level string @description("Educational stage (primary, lower_secondary, upper_secondary)")
  title string
  learning_outcomes string @description("Comma-separated canonical learning outcomes")
  exam_board string? @description("Awarding body / ministry (e.g. MŠMT, MŠMTŠ, OH, NÚCEM)")
  source_url string
  content_hash string?
}

function ExtractMaltaSubjectCurriculum(
  nation: string,
  language: string,
  subject: string,
  text: string
) -> MLTSubjectCurriculum {
  client Claude
  prompt #"
    Extract the canonical Malta subject curriculum row from the text.
    Preserve the canonical learning outcomes and the grade_level tag.

    Nation: { nation }
    Language: { language }
    Subject: { subject }
    Text: { text }

    { ctx.output_format }
  "#
}
