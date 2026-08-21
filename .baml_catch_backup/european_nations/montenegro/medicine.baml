// MNE medicine / public-health extraction BAML schema (EU
// candidate/neighbour full-depth expansion).

class MontenegroHealthGuidance {
  agency string @description("The issuing public-health agency of Montenegro")
  advisory_id string @description("The canonical per-advisory document id")
  language string @description("Official language of Montenegro")
  target_audience string @description("general_public | clinicians | schools | travellers")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractMontenegroHealthGuidance(
  nation: string,
  language: string,
  text: string
) -> MontenegroHealthGuidance {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
