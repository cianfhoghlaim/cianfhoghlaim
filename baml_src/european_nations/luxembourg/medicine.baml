// Luxembourg medicine extraction BAML schema.

class LuxembourgHealthGuidance {
  agency string @description("The public-health agency issuing the guidance")
  advisory_id string @description("The canonical per-advisory document id")
  nation string @description("ISO 3166-1 alpha-3 (lowercase)")
  language string @description("Official language of the row (lb,fr,de)")
  title string
  target_audience string? @description("general_public | clinicians | parents | schools | employers")
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractLuxembourgHealthGuidance(
  nation: string,
  language: string,
  text: string
) -> LuxembourgHealthGuidance {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    LuxembourgHealthGuidance {
      title "",
      publication_date null,
      source_url "",
      content_hash null,
    }
  }
}
