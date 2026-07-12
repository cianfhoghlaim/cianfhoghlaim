// GEO law extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class GEOStatute {
  statute_id string @description("The canonical per-statute document id")
  title string
  jurisdiction string @description("The jurisdiction (Georgia)")
  official_status string @description("in_force | amended | repealed | draft")
  language string @description("Official language of Georgia")
  source_url string
  publication_date string?
  content_hash string?
}

function ExtractGEOStatute(
  nation: string,
  language: string,
  text: string
) -> GEOStatute {
  client Claude
  prompt #"
    Extract the canonical statute record from the following
    Georgia legislative text. Preserve the canonical statute id + the
    official status.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
