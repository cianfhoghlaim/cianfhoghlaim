// XKX law extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class XKXStatute {
  statute_id string @description("The canonical per-statute document id")
  title string
  jurisdiction string @description("The jurisdiction (Kosovo)")
  official_status string @description("in_force | amended | repealed | draft")
  language string @description("Official language of Kosovo")
  source_url string
  publication_date string?
  content_hash string?
}

function ExtractXKXStatute(
  nation: string,
  language: string,
  text: string
) -> XKXStatute {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
