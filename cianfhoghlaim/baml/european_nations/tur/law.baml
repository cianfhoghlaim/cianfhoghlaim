// TUR law extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class TURStatute {
  statute_id string @description("The canonical per-statute document id")
  title string
  jurisdiction string @description("The jurisdiction (Turkey)")
  official_status string @description("in_force | amended | repealed | draft")
  language string @description("Official language of Turkey")
  source_url string
  publication_date string?
  content_hash string?
}

function ExtractTURStatute(
  nation: string,
  language: string,
  text: string
) -> TURStatute {
  client Claude
  prompt #"
    Extract the canonical statute record from the following
    Turkey legislative text. Preserve the canonical statute id + the
    official status.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
