// BIH medicine / public-health extraction BAML schema (EU
// candidate/neighbour full-depth expansion).

class BosniaAndHerzegovinaHealthGuidance {
  agency string @description("The issuing public-health agency of Bosnia and Herzegovina")
  advisory_id string @description("The canonical per-advisory document id")
  language string @description("Official language of Bosnia and Herzegovina")
  target_audience string @description("general_public | clinicians | schools | travellers")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractBosniaAndHerzegovinaHealthGuidance(
  nation: string,
  language: string,
  text: string
) -> BosniaAndHerzegovinaHealthGuidance {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
