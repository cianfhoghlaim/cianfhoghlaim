// BAML Schema for UoG Past Papers (per-module past paper index).
//
// Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.
//
// NEW in this change. The past papers for each module live at
// regexam.nuigalway.ie (authenticated M365-gated archive). The DLT
// source at dlt_sources/british_isles/ireland/tertiary/uog/regexam_papers.py
// scrapes them once the per-user credential vault is unlocked.

class PastPaper {
  paper_id string @description("Canonical paper ID, e.g. 'CS203-2024-P1'")
  module_code string @description("FK → Module.module_code, e.g. 'CS203'")
  year int @description("Examination year, e.g. 2024")
  paper_number int @description("Paper number (1, 2, or 3 for some modules)")
  pdf_url string @description("Direct URL to the past paper PDF on regexam.nuigalway.ie")
  has_marking_scheme bool @description("True if a marking scheme PDF is also available")
  marking_scheme_url string? @description("URL to the marking scheme PDF (if has_marking_scheme = true)")
  scraped_at string @description("ISO-8601 timestamp of the scrape")
  confidence float @description("Extraction confidence 0.0-1.0")
}

function ExtractPastPaper(input: string, module_code: string) -> PastPaper {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting per-module past papers from the
    University of Galway regexam.nuigalway.ie archive index page.

    For module {{ module_code }}, extract each past paper as
    {paper_id, year, paper_number, pdf_url, has_marking_scheme,
    marking_scheme_url?}.

    {{ ctx.output_format }}
    {{ input }}
  "#
}

function ExtractPastPapersBulk(input: string, module_code: string) -> PastPaper[] {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    You are an expert at extracting every past paper for module
    {{ module_code }} from the regexam.nuigalway.ie archive.

    {{ ctx.output_format }}
    {{ input }}
  "#
}
