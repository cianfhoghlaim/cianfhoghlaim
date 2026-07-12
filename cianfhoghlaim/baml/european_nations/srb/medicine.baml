// SRB medicine / public-health extraction BAML schema (EU
// candidate/neighbour full-depth expansion).

class SRBHealthGuidance {
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

function ExtractSRBHealthGuidance(
  nation: string,
  language: string,
  text: string
) -> SRBHealthGuidance {
  client Claude
  prompt #"
    Extract the canonical public-health guidance record from the
    following Serbia text. Preserve the issuing agency + the
    advisory id.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
