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
) -> QuebecEducationBilingualRecord {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    QuebecEducationBilingualRecord {
      title bilingualtextquebec {},
      summary null,
      subject null,
      publication_date null,
      source_url "",
      content_hash null,
    }
  }
}
