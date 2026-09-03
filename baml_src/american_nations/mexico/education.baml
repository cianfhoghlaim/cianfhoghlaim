// MEX education extraction BAML schema.

class MexicoEducationDocument {
  sep_id string @description("The canonical per-education document id")
  jurisdiction string @description("ISO 3166-1 alpha-3 or sub-state slug")
  country_code string? @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractMexicoEducationDocument(
  jurisdiction: string,
  language: string,
  text: string
) -> MexicoEducationDocument {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    MexicoEducationDocument {
      language "",
      title "",
      summary null,
      publication_date null,
      source_url "",
      content_hash null,
    }
  }
}
