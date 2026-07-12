// MKD law extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class MKDStatute {
  statute_id string @description("The canonical per-statute document id")
  title string
  jurisdiction string @description("The jurisdiction (North Macedonia)")
  official_status string @description("in_force | amended | repealed | draft")
  language string @description("Official language of North Macedonia")
  source_url string
  publication_date string?
  content_hash string?
}

function ExtractMKDStatute(
  nation: string,
  language: string,
  text: string
) -> MKDStatute {
  client Claude
  prompt #"
    Extract the canonical statute record from the following
    North Macedonia legislative text. Preserve the canonical statute id + the
    official status.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
