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
) -> CanadianProvinceDocument {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
