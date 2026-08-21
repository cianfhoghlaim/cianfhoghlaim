// Ukraine medicine extraction BAML schema.

class UkraineMedicineDocument {
  ministry_health_id string @description("The canonical per-medicine document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of Ukraine")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractUkraineMedicineDocument(
  country_code: string,
  language: string,
  text: string
) -> UkraineMedicineDocument {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
