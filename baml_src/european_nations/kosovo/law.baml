// XKX law extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class KosovoStatute {
  statute_id string @description("The canonical per-statute document id")
  title string
  jurisdiction string @description("The jurisdiction (Kosovo)")
  official_status string @description("in_force | amended | repealed | draft")
  language string @description("Official language of Kosovo")
  source_url string
  publication_date string?
  content_hash string?
}

function ExtractKosovoStatute(
  nation: string,
  language: string,
  text: string
) -> KosovoStatute {
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
