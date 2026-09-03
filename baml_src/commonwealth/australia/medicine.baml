// Australia medicine extraction BAML schema.

class AustraliaMedicineDocument {
  tga_id string @description("The canonical per-medicine document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractAustraliaMedicineDocument(
  country_code: string,
  language: string,
  text: string
) -> AustraliaMedicineDocument {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    AustraliaMedicineDocument {
      language "",
      title "",
      summary null,
      publication_date null,
      source_url "",
      content_hash null,
    }
  }
}
