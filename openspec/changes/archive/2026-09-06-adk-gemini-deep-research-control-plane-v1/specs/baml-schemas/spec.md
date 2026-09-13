## ADDED Requirements

### Requirement: ExtractGeminiDeepResearchReport BAML function
The system SHALL add a `ExtractGeminiDeepResearchReport` function to
`baml_src/_shared/gemini_deep_research.baml` that takes a long-form
Gemini Deep Research report (markdown) and returns a structured
`GeminiDeepResearchOutput` BAML class with `query`, `interactions`
(list of `ResearchInteraction`), `synthesized_report`, `citations`
(list of `ResearchCitation`), `key_findings` (list of strings),
`created_at` (datetime), and `quality_score` (float).

Note: the cianfhoghlaim-side class is named `GeminiDeepResearchOutput`
(not `GeminiDeepResearchReport`) because `GeminiDeepResearchReport`
is already used by `baml_src/processing/author_archive.baml:105`
(added by the 2026-06-16-author-archive-gemini-and-uos-ingestion
change for retrospective PDF extraction with a different schema —
`topic`, `domain`, `summary`, `cited_urls`, `gemini_account`,
`research_date`, `confidence`). The two classes serve distinct
purposes:

- `GeminiDeepResearchReport` (author_archive) — retrospective
  extraction from an archived PDF for the personal-archive use case.
- `GeminiDeepResearchOutput` (this change) — live-streaming API
  output with the `interactions` field used for AG-UI event
  streaming.

#### Scenario: Extract a Deep Research report
- **WHEN** the BAML runtime calls `ExtractGeminiDeepResearchReport(text=<raw_report>)`
- **THEN** the function MUST return a `GeminiDeepResearchOutput` instance
- **AND** MUST route through the canonical `ExtractEnPrimary` BAML client
- **AND** MUST use the LiteLLM `minimax` model alias

#### Scenario: Quality score below threshold
- **WHEN** the BAML runtime returns a `GeminiDeepResearchOutput` with `quality_score < 0.6`
- **THEN** the `extract_quality_loop` ADK LoopAgent MUST retry up to 3 times
- **AND** MUST fall back through the Unsloth → LiteLLM → MiniMax → Gemini provider chain

### Requirement: BAML class for browser stack Gemini Deep Research
The `bonneagar/stacks/browser/sruth_browser/baml/browser_extraction.baml`
SHALL add a `GeminiDeepResearchOutput` class with the same fields as
the cianfhoghlaim-side `ExtractGeminiDeepResearchReport` return type.
The class SHALL be codegen-compatible with the cianfhoghlaim-side
class (via the centralised BAML client registry).

#### Scenario: Class shape parity
- **WHEN** `baml-cli generate` is run on both repos
- **THEN** both `GeminiDeepResearchOutput` classes MUST have identical Pydantic schemas
