// Croílár LinkedIn Profile Extraction Schema
// Extracts structured profile data from scraped LinkedIn pages.
// Used by the Stream registry — see croilar/_shared/streams.py.
//
// Source: pipelines/linkedin/source.py → DuckDB → BAML extraction
// Emits TypeScript + Python client code via `bun run baml-cli compile`.

class LinkedInExperience {
  title string
  company string
  location string | null
  startDate string
  endDate string | null
  description string | null
  isCurrentRole bool @description("Whether the person currently holds this position")
}

class LinkedInEducation {
  school string
  degree string
  field string | null
  startYear string | null
  endYear string | null
}

class LinkedInProfile {
  name string
  headline string
  location string
  about string
  experience LinkedInExperience[]
  education LinkedInEducation[]
  skills string[]
  recommendations string[]
  profileUrl string
  streamId string @description("The croilar Stream id this profile belongs to: music, teaching, cv, or research")
  ownerDisplayName string @description("Canonical owner display name, e.g. 'Cian Mac an Déisigh Uí Liatháin'")
  ownerSlug string? @description("Owner alias from Stream.owner, e.g. 'cianfhoghlaim'")
  @@stream.done
}

function ExtractLinkedInProfile(text: string) -> LinkedInProfile {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    LinkedInProfile {
      name "",
      headline "",
      location "",
      about "",
      experience null,
      education null,
      skills null,
      recommendations null,
      profileUrl "",
    }
  }
}

function ExtractExperienceHighlights(profile: LinkedInProfile) -> string {  client ExtractEn
    prompt #"
    {{ _.role("user") }}
    You are an expert extractor. From the input below, extract every field
    in the return type according to the @description decorators on the
    class definition. Preserve the canonical field names + types.

    {{ ctx.output_format }}

    {{ input }}
  "#

  catch_all (err) {
    ""
  }
}
