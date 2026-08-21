// Poland law extraction BAML schema.

class PolandLawDocument {
  sejm_id string @description("The canonical per-law document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of Poland")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractPolandLawDocument(
  country_code: string,
  language: string,
  text: string
) -> PolandLawDocument {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
