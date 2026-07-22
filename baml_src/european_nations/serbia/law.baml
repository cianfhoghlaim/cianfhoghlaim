// SRB law extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class SRBStatute {
  statute_id string @description("The canonical per-statute document id")
  title string
  jurisdiction string @description("The jurisdiction (Serbia)")
  official_status string @description("in_force | amended | repealed | draft")
  language string @description("Official language of Serbia")
  source_url string
  publication_date string?
  content_hash string?
}

function ExtractSRBStatute(
  nation: string,
  language: string,
  text: string
) -> SRBStatute {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
