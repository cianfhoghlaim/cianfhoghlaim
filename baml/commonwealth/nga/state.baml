// Nigerian state extraction BAML schema.

class NigerianStateCurriculumSpec {
  url string
  country string @description("Country code (nga)")
  state_code string @description("ISO-style state slug (Kano State, Lagos State, ...)")
  state_name string? @description("The English-language state name")
  domain string @description("education | law | medicine | statistics | government")
  language string @description("en | ha | yo | ig | pcm")
  title string
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractNigerianStateCurriculumSpec(
  state_code: string,
  language: string,
  text: string
) -> NigerianStateCurriculumSpec {
  client Claude
  prompt #"
    Extract the canonical Nigerian state document from the following
    text. The state_code + domain MUST be preserved exactly.

    State code: {{ state_code }}
    Language: {{ language }}
    Text: {{ text }}

    {{ ctx.output_format }}
  "#
}
