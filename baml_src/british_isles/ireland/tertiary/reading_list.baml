// BAML Schema for UoG Reading Lists (per-module).
//
// Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.
//
// NEW in this change. Extracts the 3-10 essential + recommended
// reading items per module from the per-module handbook PDFs.
//
// The schema reuses the ReadingListItem + ReadingFormat types from the
// legacy university_extraction.baml; this file adds the per-module
// aggregation wrapper.

class ReadingListItem {
  format "isbn_13" | "doi" | "url" | "internal_ref" | "other"
  title string @description("The book / paper / resource title")
  authors string[] @description("Ordered list of author / editor names")
  year int? @description("Publication year (4-digit), or null if not visible")
  isbn_13 string? @description("13-digit ISBN, set when format = isbn_13")
  doi string? @description("Digital Object Identifier (without 'doi:' prefix), set when format = doi")
  url string? @description("Free-form URL, set when format = url or doi")
  library_ref string? @description("Library / shelf reference, set when format = internal_ref")
  essential bool @description("True if this reading is marked 'essential' or 'core' on the module page")
  confidence float @description("Extraction confidence 0.0-1.0")
}

class ReadingList {
  module_code string @description("FK → Module.module_code, e.g. 'CS203'")
  reading_list ReadingListItem[] @description("The 3-10 reading items, ordered by essential-then-display-order")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

function ExtractReadingList(input: string, module_code: string) -> ReadingList {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting per-module reading lists from a
    University of Galway module handbook PDF.

    For module {{ module_code }}, extract each reading item as
    {format, title, authors[], year, isbn_13?, doi?, url?, library_ref?,
    essential}.

    {{ ctx.output_format }}
    {{ input }}
  "#
}
