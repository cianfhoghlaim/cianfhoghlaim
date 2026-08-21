// MNE law extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class MontenegroStatute {
  statute_id string @description("The canonical per-statute document id")
  title string
  jurisdiction string @description("The jurisdiction (Montenegro)")
  official_status string @description("in_force | amended | repealed | draft")
  language string @description("Official language of Montenegro")
  source_url string
  publication_date string?
  content_hash string?
}

function ExtractMontenegroStatute(
  nation: string,
  language: string,
  text: string
) -> MontenegroStatute {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
