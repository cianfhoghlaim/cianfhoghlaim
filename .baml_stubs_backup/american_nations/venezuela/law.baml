// VEN law extraction BAML schema.

class VenezuelaLawDocument {
  tsj_id string @description("The canonical per-law document id")
  jurisdiction string @description("ISO 3166-1 alpha-3 or sub-state slug")
  country_code string? @description("ISO 3166-1 alpha-3 (lowercase)")
  language string
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractVenezuelaLawDocument(
  jurisdiction: string,
  language: string,
  text: string
) -> VenezuelaLawDocument {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
