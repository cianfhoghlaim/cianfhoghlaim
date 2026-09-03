// MKD education extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class NorthMacedoniaSubjectCurriculum {
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  subject string @description("Subject slug (e.g. mathematics, chemistry)")
  language string @description("Official language of North Macedonia")
  grade_level string @description("The canonical grade level for North Macedonia")
  learning_outcomes string @description("Per-subject learning outcomes extracted from the syllabus")
  source_url string @description("Canonical syllabus URL")
  publication_date string?
  content_hash string?
}

function ExtractNorthMacedoniaSubjectCurriculum(
  nation: string,
  language: string,
  subject: string,
  text: string
) -> NorthMacedoniaSubjectCurriculum {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    NorthMacedoniaSubjectCurriculum {
      publication_date null,
      content_hash null,
    }
  }
}
