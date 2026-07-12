// Quebec education extraction BAML schema.

class BilingualTextQuebec {
  fr string? @description("French text")
  en string? @description("English text")
}

class QuebecEducationBilingualRecord {
  url string @description("Canonical document URL")
  province string @description("Province code (qc)")
  language string @description("The language of the row (fr default for Quebec)")
  title BilingualTextQuebec
  summary BilingualTextQuebec?
  level string? @description("preschool | primary | secondary | CEGEP | university")
  subject string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractQuebecEducationDocument(
  province: string,
  language: string,
  text: string
) -> QuebecEducationBilingualRecord {
  client Claude
  prompt #"
    Extract the canonical Quebec education record from the following
    text. The title + summary MUST be bilingual (fr + en where present).

    Province: {{ province }}
    Language: {{ language }}
    Text: {{ text }}

    {{ ctx.output_format }}
  "#
}
