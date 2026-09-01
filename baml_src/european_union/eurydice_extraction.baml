// Eurydice extraction BAML schema.

class EurydiceNationalEducationStructure {
  country_code string @description("ISO 3166-1 alpha-3 (lowercase) of the country the page describes")
  language EULanguage
  title string
  governance_model string? @description("decentralised / centralised / federal / etc.")
  compulsory_education_ages string? @description("E.g. '6-16'")
  primary_education_years int?
  lower_secondary_education_years int?
  upper_secondary_education_years int?
  source_url string
  content_hash string?
  last_updated string? @description("ISO 8601")
}

function ExtractEurydiceNationalEducationStructure(
  language: EULanguage,
  text: string
) -> EurydiceNationalEducationStructure {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ text }}
  "#

}
