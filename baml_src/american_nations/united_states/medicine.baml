// US_US_CA medicine extraction BAML schema.

class US_US_CAMedicineDocument {
  cdph_id string @description("The canonical per-medicine document id")
  jurisdiction string @description("ISO 3166-1 alpha-3 or sub-state slug")
  country_code string? @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractUS_US_CAMedicineDocument(
  jurisdiction: string,
  language: string,
  text: string
) -> US_US_CAMedicineDocument {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    US_US_CAMedicineDocument {
      language "",
      title "",
      summary null,
      publication_date null,
      source_url "",
      content_hash null,
    }
  }
}
