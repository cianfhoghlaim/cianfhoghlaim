// Romania law extraction BAML schema (EU nations full-depth).

class RomaniaStatute {
  statute_id string @description("The canonical per-statute id")
  country_code string @description("ISO 3166-1 alpha-3 (lowercase)")
  jurisdiction string @description("The jurisdiction name (e.g. Romania)")
  title string
  official_status string @description("in_force | amended | repealed")
  source_url string
  content_hash string?
  language string @description("Official language the statute was published in")
}

function ExtractRomaniaStatute(
  nation: string,
  language: string,
  text: string
) -> RomaniaStatute {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
