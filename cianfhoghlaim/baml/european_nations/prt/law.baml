// PRT law extraction BAML schema (EU nations full-depth).

class PRTStatute {
  statute_id string @description("The canonical per-statute id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  jurisdiction string @description("The jurisdiction name (e.g. Portugal)")
  title string
  official_status string @description("in_force | amended | repealed")
  source_url string
  content_hash string?
  language string @description("Official language the statute was published in")
}

function ExtractPRTStatute(
  nation: string,
  language: string,
  text: string
) -> PRTStatute {
  client Claude
  prompt #"
    Extract the canonical Portugal statute record from the text.
    Preserve the statute_id and the official_status tag exactly.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
