// GEO education extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class GeorgiaSubjectCurriculum {
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  subject string @description("Subject slug (e.g. mathematics, chemistry)")
  language string @description("Official language of Georgia")
  grade_level string @description("The canonical grade level for Georgia")
  learning_outcomes string @description("Per-subject learning outcomes extracted from the syllabus")
  source_url string @description("Canonical syllabus URL")
  publication_date string?
  content_hash string?
}

function ExtractGeorgiaSubjectCurriculum(
  nation: string,
  language: string,
  subject: string,
  text: string
) -> GeorgiaSubjectCurriculum {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
