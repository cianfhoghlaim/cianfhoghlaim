// Croílár CV Extraction Schema
// Extracts structured CV data from the author's academic and professional PDFs.
// Source: author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/achievement/ + teaching/
//
// Emits TypeScript + Python client code via `bun run baml-cli compile`.

class EducationEntry {
  institution string
  degree string
  field string
  startYear string
  endYear string
  location string
  description_en string @description("English description of the programme or achievement")
  description_ga string @description("Gaeilge description, if present in the source")
  grade string | null
}

class Award {
  title string
  issuer string
  year string
  description_en string
  category string @description("e.g. Academic, Professional, Teaching, Music")
}

class Publication {
  title string
  venue string
  year string
  authors string[]
  abstract_en string
  url string | null
}

class Reference {
  name string
  title string
  institution string
  email string | null
  relationship string @description("e.g. MSc Supervisor, Programme Director, Cooperating Teacher")
  phone string | null
}

class SkillCategory {
  category string @description("e.g. Music Production, Software Development, Languages, Teaching")
  skills string[]
  proficiency number @description("0-100 self-assessed proficiency level")
}

class ProfessionalExperience {
  title string
  organization string
  startDate string
  endDate string | null
  description_en string
  description_ga string | null
  location string | null
}

function ExtractCV(text: string) -> EducationEntry[] {
  // Extracts education history from CV text.
  // Returns an array of education entries — degrees, diplomas, certificates.
  // Supports both English and Gaeilge source text.
  // Uses the specialised Irish models (UCCIX, GaBERT) from the LiteLLM proxy.
}

function ExtractAward(text: string) -> Award[] {
  // Extracts awards, scholarships, and honours.
  // Categorises into Academic, Professional, Teaching, and Music.
}

function ExtractPublication(text: string) -> Publication[] {
  // Extracts academic publications and conference papers.
  // Title, venue, year, authors, abstract.
}

function ExtractReference(text: string) -> Reference[] {
  // Extracts professional and academic references.
  // Name, title, institution, email, relationship.
}

function ExtractSkills(text: string) -> SkillCategory[] {
  // Extracts skill categories with proficiency levels.
  // Categories: Music Production, Software Development, Languages, Teaching.
}

function ExtractExperience(text: string) -> ProfessionalExperience[] {
  // Extracts professional experience history.
  // Title, organization, dates, description (en + ga).
}
