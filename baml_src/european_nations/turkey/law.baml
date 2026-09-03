// TUR law extraction BAML schema (EU candidate/neighbour
// full-depth expansion).

class TurkeyStatute {
  statute_id string @description("The canonical per-statute document id")
  title string
  jurisdiction string @description("The jurisdiction (Turkey)")
  official_status string @description("in_force | amended | repealed | draft")
  language string @description("Official language of Turkey")
  source_url string
  publication_date string?
  content_hash string?
}

function ExtractTurkeyStatute(
  nation: string,
  language: string,
  text: string
) -> TurkeyStatute {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    TurkeyStatute {
      title "",
      source_url "",
      publication_date null,
      content_hash null,
    }
  }
}
