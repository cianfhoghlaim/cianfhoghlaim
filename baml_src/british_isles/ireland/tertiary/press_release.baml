// BAML Schema for UoG Press Releases + News.
//
// Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.
//
// Migrated from
// kings_college_galway/baml_src/uog/processing/press_release.baml
// (retired per the umbrella change).

class PressRelease {
  url string @description("Canonical URL of the press release on universityofgalway.ie/news/")
  title_english string @description("Headline of the press release")
  title_irish string? @description("Irish-language headline, if available")
  published_date_iso string @description("ISO-8601 date of publication")
  category "research" | "student" | "partnership" | "award" | "event" | "funding" | "other"
  body_markdown string @description("Full press release body in markdown")
  authors string[] @description("Author / editor names")
  related_programme_ids string[] @description("FKs to Programme.programme_id, if mentioned")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Extraction confidence 0.0-1.0")
}

function ExtractPressRelease(input: string) -> PressRelease {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway press releases.

    Extract: url, title_english + irish, published_date_iso, category,
    body_markdown, authors[], related_programme_ids[].

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractPressReleaseBulk(input: string) -> PressRelease[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting every University of Galway press
    release from the news page. Return one PressRelease per release.

    {{ ctx.output_format }}
    {{ input }}
  "#
}
