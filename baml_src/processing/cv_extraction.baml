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
  @@stream.done
}

class Award {
  title string
  issuer string
  year string
  description_en string
  category string @description("e.g. Academic, Professional, Teaching, Music")
  @@stream.done
}

class Publication {
  title string
  venue string
  year string
  authors string[]
  abstract_en string
  url string | null
  @@stream.done
}

class Reference {
  name string
  title string
  institution string
  email string | null
  relationship string @description("e.g. MSc Supervisor, Programme Director, Cooperating Teacher")
  phone string | null
  @@stream.done
}

class SkillCategoryCv {
  category string @description("e.g. Music Production, Software Development, Languages, Teaching")
  skills string[]
  proficiency float @description("0-100 self-assessed proficiency level")
  @@stream.done
}

class ProfessionalExperience {
  title string
  organization string
  startDate string
  endDate string | null
  description_en string
  description_ga string | null
  location string | null
  @@stream.done
}

function ExtractCV(text: string) -> EducationEntry[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractAward(text: string) -> Award[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractPublication(text: string) -> Publication[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractReference(text: string) -> Reference[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractSkills(text: string) -> SkillCategoryCv[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}

function ExtractExperience(text: string) -> ProfessionalExperience[] {  client ExtractEn
  prompt #"Auto-generated extraction prompt."#
}
