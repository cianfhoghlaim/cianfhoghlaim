// Slovenia education extraction BAML schema (EU nations full-depth).

class SloveniaSubjectCurriculum {
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

function ExtractSloveniaSubjectCurriculum(
  nation: string,
  language: string,
  subject: string,
  text: string
) -> SloveniaSubjectCurriculum {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
