// SVK law extraction BAML schema (EU nations full-depth).

class SVKStatute {
  statute_id string @description("The canonical per-statute id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  jurisdiction string @description("The jurisdiction name (e.g. Slovakia)")
  title string
  official_status string @description("in_force | amended | repealed")
  source_url string
  content_hash string?
  language string @description("Official language the statute was published in")
}

function ExtractSVKStatute(
  nation: string,
  language: string,
  text: string
) -> SVKStatute {
  client Claude
  prompt #"
    Extract the canonical Slovakia statute record from the text.
    Preserve the statute_id and the official_status tag exactly.

    Nation: { nation }
    Language: { language }
    Text: { text }

    { ctx.output_format }
  "#
}
