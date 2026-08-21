// Switzerland law extraction BAML schema.

class SwitzerlandStatute {
  statute_id string @description("The canonical per-statute document id")
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("Official language of the row (de,fr,it,rm)")
  jurisdiction string @description("Federal or sub-federal jurisdiction")
  title string
  official_status string? @description("in_force | amended | repealed | pending")
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractSwitzerlandStatute(
  nation: string,
  language: string,
  text: string
) -> SwitzerlandStatute {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
