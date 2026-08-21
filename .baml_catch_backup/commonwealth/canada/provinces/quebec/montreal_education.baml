// Montreal school board + university education extraction BAML schema.

class MontrealSchoolBoardRecord {
  url string
  school_board string @description("cssdm | emsb | lbpsb | mcgill_universities")
  language string @description("fr default for cssdm; en default for emsb + lbpsb")
  title string
  policy_id string? @description("The school-board-specific policy / curriculum id")
  grade_band string? @description("primary | secondary | cegep | university")
  publication_date string?
  source_url string
  content_hash string?
}

function ExtractMontrealSchoolBoardDocument(
  school_board: string,
  language: string,
  text: string
) -> MontrealSchoolBoardRecord {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#
}
