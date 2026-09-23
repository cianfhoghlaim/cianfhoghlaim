// BAML Schema for UoG Research Outputs (publications + theses).
//
// Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.
//
// NEW in this change (replaces the KCG stub which had no real
// research_outputs.baml — the prior KCG source used a hardcoded list).

class ResearchOutput {
  url string @description("Canonical URL of the research output")
  title string @description("Title of the publication or thesis")
  type "journal_article" | "conference_paper" | "thesis" | "book_chapter" | "report" | "dataset" | "other"
  authors string[] @description("Author names, in publication order")
  year int @description("Publication year (4-digit)")
  doi string? @description("Digital Object Identifier (without 'doi:' prefix)")
  journal string? @description("Journal or conference name")
  abstract string? @description("Abstract or summary (1-3 sentences)")
  related_school_id string? @description("FK to School.school_id")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Extraction confidence 0.0-1.0")
}

function ExtractResearchOutput(input: string) -> ResearchOutput {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting University of Galway research outputs
    (journal articles + conference papers + theses + reports).

    Extract: url, title, type, authors[], year, doi, journal, abstract,
    related_school_id.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractResearchOutputBulk(input: string) -> ResearchOutput[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting every University of Galway research
    output from the page. Return one ResearchOutput per publication.

    {{ ctx.output_format }}
    {{ input }}
  "#
}
