// GEO law extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class GeorgiaStatute {
  statute_id string @description("The canonical per-statute document id")
  title string
  jurisdiction string @description("The jurisdiction (Georgia)")
  official_status string @description("in_force | amended | repealed | draft")
  language string @description("Official language of Georgia")
  source_url string
  publication_date string?
  content_hash string?
}

function ExtractGeorgiaStatute(
  nation: string,
  language: string,
  text: string
) -> GeorgiaStatute {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
