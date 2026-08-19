// EMA extraction BAML schema.

class EMAMedicine {
  medicine_id string @description("EMA medicine ID (e.g. EMEA/H/C/000123)")
  language EULanguage
  medicine_name string @description("Invented name in the row's language")
  active_substance string @description("Active substance (INN)")
  atc_code string? @description("Anatomical Therapeutic Chemical classification code")
  authorisation_status string @description("authorised / refused / suspended / withdrawn")
  authorisation_date string?
  marketing_authorisation_holder string? @description("The pharmaceutical company holding the MA")
  therapeutic_indication string? @description("Short summary of the approved indication")
  atc_class_description string?
  source_url string
  content_hash string?
}

function ExtractEMAMedicine(
  language: EULanguage,
  text: string
) -> EMAMedicine {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    EMAMedicine {
      language eulanguage {},
      authorisation_date null,
      atc_class_description null,
      source_url "",
      content_hash null,
    }
  }
}
