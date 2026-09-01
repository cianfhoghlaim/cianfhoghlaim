// Hungary law extraction BAML schema (EU nations full-depth).

class HungaryStatute {
  statute_id string @description("The canonical per-statute id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  jurisdiction string @description("The jurisdiction name (e.g. Hungary)")
  title string
  official_status string @description("in_force | amended | repealed")
  source_url string
  content_hash string?
  language string @description("Official language the statute was published in")
}

function ExtractHungaryStatute(
  nation: string,
  language: string,
  text: string
) -> HungaryStatute {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#
}
