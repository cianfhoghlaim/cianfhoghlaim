// ECDC extraction BAML schema.

class ECDCSurveillance {
  dataset_id string
  language EULanguage
  title string
  surveillance_topic string @description("E.g. 'measles', 'influenza', 'covid19', 'tb'")
  reporting_period_start string? @description("ISO 8601")
  reporting_period_end string? @description("ISO 8601")
  geography string? @description("EU / EEA / single member state")
  case_count int? @description("Reported case count for the period")
  source_url string
  content_hash string?
}

function ExtractECDCSurveillance(
  language: EULanguage,
  text: string
) -> ECDCSurveillance {
  client Claude
  prompt #"
    Extract the canonical ECDC surveillance record from the following
    surveillance text. The dataset_id is the ECDC atlas identifier.

    Language: {{ language }}
    Text: {{ text }}

    {{ ctx.output_format }}
  "#
}
