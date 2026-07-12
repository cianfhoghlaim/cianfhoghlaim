// MKD education extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class MKDSubjectCurriculum {
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  subject string @description("Subject slug (e.g. mathematics, chemistry)")
  language string @description("Official language of North Macedonia")
  grade_level string @description("The canonical grade level for North Macedonia")
  learning_outcomes string @description("Per-subject learning outcomes extracted from the syllabus")
  source_url string @description("Canonical syllabus URL")
  publication_date string?
  content_hash string?
}

function ExtractMKDSubjectCurriculum(
  nation: string,
  language: string,
  subject: string,
  text: string
) -> MKDSubjectCurriculum {
  client Claude
  prompt #"
    Extract the canonical per-subject curriculum record from the
    following North Macedonia text. Preserve the subject slug + the official
    language(s) (mk) + the canonical grade level.

    Nation: { nation }
    Language: { language }
    Subject: { subject }
    Text: { text }

    { ctx.output_format }
  "#
}
