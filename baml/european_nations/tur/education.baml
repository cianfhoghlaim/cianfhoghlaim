// TUR education extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class TURSubjectCurriculum {
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  subject string @description("Subject slug (e.g. mathematics, chemistry)")
  language string @description("Official language of Turkey")
  grade_level string @description("The canonical grade level for Turkey")
  learning_outcomes string @description("Per-subject learning outcomes extracted from the syllabus")
  source_url string @description("Canonical syllabus URL")
  publication_date string?
  content_hash string?
}

function ExtractTURSubjectCurriculum(
  nation: string,
  language: string,
  subject: string,
  text: string
) -> TURSubjectCurriculum {
  client Claude
  prompt #"
    Extract the canonical per-subject curriculum record from the
    following Turkey text. Preserve the subject slug + the official
    language(s) (tr) + the canonical grade level.

    Nation: { nation }
    Language: { language }
    Subject: { subject }
    Text: { text }

    { ctx.output_format }
  "#
}
