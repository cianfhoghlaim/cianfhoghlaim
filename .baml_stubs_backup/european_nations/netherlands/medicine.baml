// Netherlands medicine extraction BAML schema.

class NetherlandsHealthGuidance {
  agency string @description("The public-health agency issuing the guidance")
  advisory_id string @description("The canonical per-advisory document id")
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("Official language of the row (nl)")
  title string
  target_audience string? @description("general_public | clinicians | parents | schools | employers")
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractNetherlandsHealthGuidance(
  nation: string,
  language: string,
  text: string
) -> NetherlandsHealthGuidance {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
