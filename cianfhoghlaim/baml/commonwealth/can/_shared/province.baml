// Canadian province shared extraction BAML schema.

class CanadianProvinceDocument {
  url string
  province string @description("ISO-style province code (on, qc, bc, ab, sk, mb, ns, nb, pe, nl, nt, nu, yt)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractCanadianProvinceDocument(
  province: string,
  language: string,
  text: string
) -> CanadianProvinceDocument {
  client Claude
  prompt #"
    Extract the canonical Canadian province document from the
    following text.

    Province: {{ province }}
    Language: {{ language }}
    Text: {{ text }}

    {{ ctx.output_format }}
  "#
}
