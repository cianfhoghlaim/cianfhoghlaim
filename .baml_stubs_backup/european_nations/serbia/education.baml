// SRB education extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class SerbiaSubjectCurriculum {
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  subject string @description("Subject slug (e.g. mathematics, chemistry)")
  language string @description("Official language of Serbia")
  grade_level string @description("The canonical grade level for Serbia")
  learning_outcomes string @description("Per-subject learning outcomes extracted from the syllabus")
  source_url string @description("Canonical syllabus URL")
  publication_date string?
  content_hash string?
}

function ExtractSerbiaSubjectCurriculum(
  nation: string,
  language: string,
  subject: string,
  text: string
) -> SerbiaSubjectCurriculum {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
