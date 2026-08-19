// NI medicine extraction BAML schema (BIEP parity).

class NorthernIrelandMedicineDocument {
  url string @description("Canonical syllabus / document URL")
  language string @description("The official language of the row")
  nation string @description("ISO 3166-1 alpha-3 or British Isles legacy slug")
  subject string? @description("Subject slug (e.g. mathematics, chemistry)")
  exam_board string? @description("Awarding body (CCEA)")
  title string
  summary string?
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractNorthernIrelandMedicineDocument(
  nation: string,
  language: string,
  text: string
) -> NorthernIrelandMedicineDocument {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    NorthernIrelandMedicineDocument {
      title "",
      summary null,
      publication_date null,
      source_url "",
      content_hash null,
    }
  }
}
