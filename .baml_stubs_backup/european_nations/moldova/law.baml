// MDA law extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class MoldovaStatute {
  statute_id string @description("The canonical per-statute document id")
  title string
  jurisdiction string @description("The jurisdiction (Moldova)")
  official_status string @description("in_force | amended | repealed | draft")
  language string @description("Official language of Moldova")
  source_url string
  publication_date string?
  content_hash string?
}

function ExtractMoldovaStatute(
  nation: string,
  language: string,
  text: string
) -> MoldovaStatute {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
