// France law extraction BAML schema.

class FranceLawDocument {
  legifrance_id string @description("The canonical per-law document id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("The official language of France")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractFranceLawDocument(
  country_code: string,
  language: string,
  text: string
) -> FranceLawDocument {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    FranceLawDocument {
      title "",
      summary null,
      publication_date null,
      source_url "",
      content_hash null,
    }
  }
}
