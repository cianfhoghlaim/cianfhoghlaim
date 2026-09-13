## MODIFIED Requirements

### Requirement: browser stack reaches 6-file GOLD_STANDARD
The `bonneagar/stacks/browser/` stack SHALL satisfy the 6-file
GOLD_STANDARD pattern by adding the missing `sidecar.yaml` +
`secrets.env` + `blueprint.yaml` + `.env.example` files, fixing the
broken `Dockerfile` CMD (`sruth.browser.server` →
`sruth_browser.server`), and adding the missing `Dockerfile.mcp` for
the `mcp-server` compose service. The 4 dead-code subdirectories
(`agent_os/`, `gemini-3-flash/`, `polymarket-research/`, and the
unused `stagehand-local` env reference) SHALL be removed.

#### Scenario: stack-doctor passes the browser stack
- **WHEN** `mise run devops:validate-stacks browser` is run
- **THEN** the `browser` stack SHALL pass all 6 GOLD_STANDARD checks
- **AND** the 4 dead-code subdirectories SHALL be removed

### Requirement: browser stack Gemini Deep Research backend
The `bonneagar/stacks/browser/sruth_browser/backends/` package SHALL
expose a new `GoogleDeepResearchBackend` class at
`backends/paid/gemini_deep_research.py` that wraps the Gemini Deep
Research API (`https://ai.google.dev/gemini-api/docs/deep-research`)
via the `google-genai` SDK. The backend SHALL be registered in
`browser_types.py:182` `BACKEND_PRIORITY` as the top-priority entry
for the `RESEARCH` capability.

#### Scenario: BackendRouter resolves RESEARCH capability
- **WHEN** the `BackendRouter` resolves a `Capability.RESEARCH` request
- **THEN** `GoogleDeepResearchBackend` MUST be tried first
- **AND** Firecrawl MUST be tried second
- **AND** Crawl4AI MUST be tried third

### Requirement: browser stack ADK orchestrator uses minimax alias
The `bonneagar/stacks/browser/sruth_browser/agents/orchestrator.py`
SHALL instantiate its 5 ADK agents using the `minimax` LiteLLM alias
instead of the hard-coded `gemini-2.0-flash` model. The backend router
SHALL resolve the `gemini-deep-research` alias to the latest Gemini
model with Deep Research support (`gemini-2.5-pro-deep-research`).

#### Scenario: Alias resolution
- **WHEN** the ADK orchestrator instantiates `LlmAgent(model="minimax")`
- **THEN** LiteLLM MUST resolve it through the 7-tier fallback chain
