// Romania medicine extraction BAML schema (EU nations full-depth).

class RomaniaHealthGuidance {
  agency string @description("The publishing agency (e.g. NIPH, EODY, NIJZ)")
  advisory_id string @description("The canonical advisory id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("Official language of the advisory")
  target_audience string @description("general_public | clinicians | schools | employers")
  title string
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractRomaniaHealthGuidance(
  nation: string,
  language: string,
  text: string
) -> RomaniaHealthGuidance {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    RomaniaHealthGuidance {
      title "",
      publication_date null,
      source_url "",
      content_hash null,
    }
  }
}
