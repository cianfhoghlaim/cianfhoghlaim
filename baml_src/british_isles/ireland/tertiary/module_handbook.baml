// BAML Schema for UoG Module Handbooks (PDF extraction).
//
// Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.
//
// NEW in this change. Extracts the canonical 6-12 sections from
// per-module handbook PDFs published at
// https://www.universityofgalway.ie/programmes/<programme>/<module>.pdf
//
// The extraction runs through the BIEP v2 4-path OCR ensemble
// (BAML/Docling + Unstract + qwen3-vl-8b + gemma-4-26B-A4B) +
// RAGAS voting (per the centralized-registry spec).

class ModuleHandbookSection {
  section_title string @description("Heading from the handbook, e.g. 'Aims & Objectives'")
  section_body string @description("Full markdown body of the section")
  confidence float @description("Section-level extraction confidence 0.0-1.0")
}

class ModuleHandbook {
  module_code string @description("FK → Module.module_code, e.g. 'CS203'")
  pdf_url string @description("URL of the source PDF")
  sections ModuleHandbookSection[] @description("The 6-12 canonical handbook sections, in document order")
  total_pages int @description("Number of pages in the source PDF")
  reading_list_section_index int? @description("Index in sections[] of the Reading List section, if found")
  assessment_section_index int? @description("Index in sections[] of the Assessment section, if found")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Overall extraction confidence 0.0-1.0")
}

function ExtractModuleHandbook(input: string, module_code: string) -> ModuleHandbook {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting the canonical 6-12 sections from a
    University of Galway module handbook PDF.

    For module {{ module_code }}, extract each section as
    {section_title, section_body}. Typical sections include:
    'Aims & Objectives', 'Learning Outcomes', 'Content',
    'Assessment', 'Reading List', 'Timetable', 'Contact'.

    {{ ctx.output_format }}
    {{ input }}
  "#
}
