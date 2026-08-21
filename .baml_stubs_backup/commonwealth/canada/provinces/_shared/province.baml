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
  prompt #"Auto-generated extraction prompt."#
}
