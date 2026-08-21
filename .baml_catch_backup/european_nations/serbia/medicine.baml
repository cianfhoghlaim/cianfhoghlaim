// SRB medicine / public-health extraction BAML schema (EU
// candidate/neighbour full-depth expansion).

class SerbiaHealthGuidance {
  agency string @description("The issuing public-health agency of Serbia")
  advisory_id string @description("The canonical per-advisory document id")
  language string @description("Official language of Serbia")
  target_audience string @description("general_public | clinicians | schools | travellers")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractSerbiaHealthGuidance(
  nation: string,
  language: string,
  text: string
) -> SerbiaHealthGuidance {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
