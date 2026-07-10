// Croílár Teaching Extraction Schema
// Extracts structured teaching records from school placement reports, student feedback,
// and curriculum materials in the author_cian_deacy_lyons.../teaching/ directory.
// Source: author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/teaching/

class Placement {
  school string @description("School name in original language (EN or GA)")
  school_type string @description("e.g. Post-Primary, Gaelscoil, Community School, Voluntary Secondary")
  location string
  startDate string
  endDate string
  subjects string[] @description("Subjects taught during placement")
  yearGroups string[] @description("e.g. Junior Cycle, Leaving Certificate, Transition Year")
  description_en string
  description_ga string | null
  cooperatingTeacher string | null @description("Cooperating teacher name")
  supervisor string | null @description("PME supervisor name")
  @@stream.done
}

class StudentFeedback {
  source string @description("e.g. Student, Cooperating Teacher, PME Supervisor")
  quote_en string
  quote_ga string | null
  rating number @description("1-5 rating, if numeric")
  category string @description("e.g. Classroom Management, Lesson Planning, Subject Knowledge, Rapport")
  @@stream.done
}

class CurriculumDesigned {
  title string
  subject string
  yearGroup string
  format string @description("e.g. Lesson Plan, Scheme of Work, Assessment Rubric, Worksheet, Presentation")
  description_en string
  description_ga string | null
  url string | null @description("Link to resource if hosted online")
  @@stream.done
}

class TeachingQualification {
  title string
  institution string
  year string
  type string @description("e.g. Degree, Certificate, Registration, Garda Vetting")
  referenceNumber string | null
  @@stream.done
}

function ExtractPlacement(text: string) -> Placement[] {
  // Extracts school placement records from teaching PDFs.
  // Returns school, dates, subjects, year groups, and descriptions.
}

function ExtractStudentFeedback(text: string) -> StudentFeedback[] {
  // Extracts student and supervisor feedback with ratings and categories.
  // Supports both English and Gaeilge source text.
}

function ExtractCurriculumDesigned(text: string) -> CurriculumDesigned[] {
  // Extracts curriculum materials designed during placements.
  // Lesson plans, schemes of work, rubrics, worksheets, presentations.
}

function ExtractTeachingQualification(text: string) -> TeachingQualification[] {
  // Extracts teaching qualifications, registrations, and certifications.
  // Teaching Council registration, Garda Vetting, BCS PGC, PME.
}
