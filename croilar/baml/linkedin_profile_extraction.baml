// Croílár LinkedIn Profile Extraction Schema
// Extracts structured profile data from scraped LinkedIn pages.
// Used by all three flows: aleyum, cianfhoghlaim, carlcashman.
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
  isCurrentRole boolean @description("Whether the person currently holds this position")
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
  flowId string @description("The croilar flow ID this profile belongs to: aleyum, cianfhoghlaim, or carlcashman")
}

function ExtractLinkedInProfile(text: string) -> LinkedInProfile {
  // Extracts structured profile data from LinkedIn profile text.
  // Handles both scraped HTML and pre-processed JSON payloads.
  // The text input can be either:
  //   - The HTML content of a LinkedIn profile page (live scraping)
  //   - A JSON string of pre-extracted data (mock mode)
  //
  // The function should extract:
  //   - Name and headline from the top section
  //   - About section (summary)
  //   - Experience history (title, company, dates, descriptions)
  //   - Education history
  //   - Skills and endorsements
  //   - Recommendations received
  //
  // For mock mode (pre-extracted JSON), the function should parse
  // the JSON and convert field names to the target schema.
}

function ExtractExperienceHighlights(profile: LinkedInProfile) -> string {
  // Generates a 3-sentence professional summary from a LinkedIn profile.
  // Format: "NAME is a HEADLINE based in LOCATION. Their recent roles
  // include TITLE at COMPANY and TITLE at COMPANY. They studied
  // DEGREE at SCHOOL and are skilled in SKILL1, SKILL2, and SKILL3."
  //
  // This is used by the portfolio page to auto-generate the bio section.
}
