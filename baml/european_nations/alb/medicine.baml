// ALB medicine / public-health extraction BAML schema (EU
// candidate/neighbour full-depth expansion).

class ALBHealthGuidance {
  agency string @description("The issuing public-health agency of Albania")
  advisory_id string @description("The canonical per-advisory document id")
  language string @description("Official language of Albania")
  target_audience string @description("general_public | clinicians | schools | travellers")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractALBHealthGuidance(
  nation: string,
  language: string,
  text: string
) -> ALBHealthGuidance {
  client Claude
  prompt #"
    Extract the canonical public-health guidance record from the
    following Albania text. Preserve the issuing agency + the
    advisory id.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
