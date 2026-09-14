// BAML template: ExtractGeminiDeepResearchReport
//
// Per the openspec change
// `2026-09-06-adk-gemini-deep-research-control-plane-v1`.
// Pairs with the new `GoogleDeepResearchBackend` (sibling of
// `FirecrawlBackend` and `BrowserbaseBackend` in
// `bonneagar/stacks/browser/sruth_browser/backends/paid/`).
//
// Extracts a structured `GeminiDeepResearchOutput` from raw Deep
// Research output (markdown) — preserving the per-step interactions,
// citations, and key findings that the Gemini Deep Research API
// (`https://ai.google.dev/gemini-api/docs/deep-research`) produces.
//
// Note: the class name `GeminiDeepResearchOutput` is intentionally
// distinct from the existing `GeminiDeepResearchReport` in
// `baml_src/processing/author_archive.baml` (the author-archive variant
// has a different schema — topic + domain + summary + cited_urls —
// for retrospective PDF extraction, while this one captures the
// live-streaming API output with `interactions`).

class ResearchCitation {
  url string
  title string?
  claim string?
}

class ResearchInteraction {
  interaction_id string
  action string
  target string?
  rationale string?
}

class GeminiDeepResearchOutput {
  query string
  synthesized_report string
  interactions ResearchInteraction[]
  citations ResearchCitation[]
  key_findings string[]
  created_at string
  quality_score float?
}

function ExtractGeminiDeepResearchReport(text: string) -> GeminiDeepResearchOutput {
  client ExtractEn
  prompt #"
    {{ _.role("user") }}
    Extract a structured representation of a Gemini Deep Research report.

    Source type: markdown (long-form Deep Research output)

    Extract:
    - query: the original research query
    - synthesized_report: the final long-form markdown answer
    - interactions: ordered list of per-step agent actions
      (action, target URL or selector, rationale)
    - citations: per-claim source URLs with optional title and the claim
    - key_findings: list of short bullet takeaways
    - created_at: ISO 8601 timestamp of the report

    Return a `GeminiDeepResearchOutput` matching the schema. Use the
    BAML ClientRegistry fallback chain (Unsloth → LiteLLM → Gemini).

    {{ ctx.output_format }}

    {{ text }}
  "#
}
