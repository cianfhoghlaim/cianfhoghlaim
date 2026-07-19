// MNE law extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class MNEStatute {
  statute_id string @description("The canonical per-statute document id")
  title string
  jurisdiction string @description("The jurisdiction (Montenegro)")
  official_status string @description("in_force | amended | repealed | draft")
  language string @description("Official language of Montenegro")
  source_url string
  publication_date string?
  content_hash string?
}

function ExtractMNEStatute(
  nation: string,
  language: string,
  text: string
) -> MNEStatute {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
