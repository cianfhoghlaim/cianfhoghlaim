// EU nations + Ukraine shared jurisdiction BAML schema.

class NationJurisdictionMetadata {
  country_code string @description("ISO 3166-1 alpha-3 (lowercase) of the country the document is about")
  country_name string? @description("The English-language name of the country")
  region string? @description("The continent/region (e.g. 'europe', 'south_america', 'north_america', 'oceania', 'asia', 'africa')")
  official_languages string[] @description("List of the official language codes the jurisdiction publishes in (ISO 639-1)")
  jurisdiction_level string @description("european_union_member | european_union_candidate | european_union_eea_efta | commonwealth_member | us_state | sovereign_nation")
  political_status string? @description("constitutional_monarchy | parliamentary_republic | federal_republic | presidential_republic | unitary_state | federation")
  source_url string
  content_hash string?
}

function ExtractNationJurisdictionMetadata(
  countryCode: string,
  language: string,
  text: string
) -> NationJurisdictionMetadata {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
