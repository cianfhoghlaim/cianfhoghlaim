// Croílár ResearchGate Profile Extraction Schema
// Extracts structured profile + publication data from ResearchGate.
//
// Source: pipelines/researchgate/source.py → DuckDB → BAML extraction
// Emits TypeScript + Python client code via `bun run baml-cli compile`.
//
// ResearchGate has no public REST API; the source uses sruth-browser
// (Browserbase CDP) to scrape the public profile page, then routes the
// HTML through this schema for structured extraction.

class ResearchGatePublication {
  title string
  authors string[]
  venue string? @description("Journal / conference / preprint server")
  year int?
  doi string?
  abstract string?
  citationCount int?
  readCount int?
  recommendationCount int?
  url string
  @@stream.done
}

class ResearchGateProfile {
  name string
  headline string @description("Department / affiliation / role")
  institution string?
  location string?
  about string?
  fieldsOfStudy string[] @description("Self-declared research interests")
  skillsAndExpertise string[]
  publications ResearchGatePublication[]
  followers int?
  following int?
  hIndex int? @description("Hirsch index, if visible on the profile")
  totalReads int?
  totalCitations int?
  profileUrl string
  streamId string @description("The croilar Stream id this profile belongs to: music, teaching, cv, or research")
  ownerDisplayName string @description("Canonical owner display name, e.g. 'Cian Mac an Déisigh Uí Liatháin'")
  ownerSlug string? @description("Owner alias from Stream.owner, e.g. 'cianfhoghlaim'")
  @@stream.done
}

function ExtractResearchGateProfile(text: string) -> ResearchGateProfile {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    ResearchGateProfile {
      name "",
      institution null,
      location null,
      about null,
      skillsAndExpertise null,
      publications null,
      followers null,
      following null,
      totalReads null,
      totalCitations null,
      profileUrl "",
    }
  }
}

function ExtractResearchGatePublication(publication_text: string) -> ResearchGatePublication {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    ResearchGatePublication {
      title "",
      authors null,
      year null,
      doi null,
      abstract null,
      citationCount null,
      readCount null,
      recommendationCount null,
      url "",
    }
  }
}
