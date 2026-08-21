// Eurostat extraction BAML schema.

class EurostatDatasetMetadata {
  dataset_id string @description("Eurostat dataset code (e.g. 'educ_uoe_grad02')")
  language EULanguage
  title string
  last_updated string? @description("ISO 8601")
  source_url string
  content_hash string?
  statistical_theme string? @description("E.g. 'education', 'labour_market', 'economy'")
  time_coverage_start string? @description("Earliest year covered")
  time_coverage_end string? @description("Latest year covered")
  geo_coverage string[]? @description("List of EU member states + EU-27 / EEA / EFTA aggregates")
  unit_of_measure string? @description("E.g. 'persons', '%', 'EUR'")
}

function ExtractEurostatDatasetMetadata(
  language: EULanguage,
  text: string
) -> EurostatDatasetMetadata {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
