// Ukraine education extraction BAML schema.

class UkraineEducationDocument {
  ministry_education_science_id string @description("The canonical per-education document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of Ukraine")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractUkraineEducationDocument(
  country_code: string,
  language: string,
  text: string
) -> UkraineEducationDocument {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
