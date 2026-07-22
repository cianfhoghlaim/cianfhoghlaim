// MKD medicine / public-health extraction BAML schema (EU
// candidate/neighbour full-depth expansion).

class MKDHealthGuidance {
  agency string @description("The issuing public-health agency of North Macedonia")
  advisory_id string @description("The canonical per-advisory document id")
  language string @description("Official language of North Macedonia")
  target_audience string @description("general_public | clinicians | schools | travellers")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractMKDHealthGuidance(
  nation: string,
  language: string,
  text: string
) -> MKDHealthGuidance {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
