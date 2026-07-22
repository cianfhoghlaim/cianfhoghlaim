// BIH law extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class BIHStatute {
  statute_id string @description("The canonical per-statute document id")
  title string
  jurisdiction string @description("The jurisdiction (Bosnia and Herzegovina)")
  official_status string @description("in_force | amended | repealed | draft")
  language string @description("Official language of Bosnia and Herzegovina")
  source_url string
  publication_date string?
  content_hash string?
}

function ExtractBIHStatute(
  nation: string,
  language: string,
  text: string
) -> BIHStatute {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
