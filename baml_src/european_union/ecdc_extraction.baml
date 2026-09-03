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
) -> ECDCSurveillance {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    ECDCSurveillance {
      dataset_id "",
      language eulanguage {},
      title "",
      source_url "",
      content_hash null,
    }
  }
}
