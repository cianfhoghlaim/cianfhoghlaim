# centralized-model-registry — Delta for Sister-repo Lesson Transfer v1

## ADDED Requirements

### Requirement: Sister repos SHALL transfer the v5 model priority chain

The system MUST require the 5 sister repos (bonneagar + tuatha +
ciancheiltis + ciandlithe + cianchosaint) to transfer the v5 model
priority chain (Primary + UnslothGemma4 + VertexGemini35Flash +
Gemma-4 vision) per their own per-sister-repo customisation.

#### Scenario: bonneagar promotes the GCP mirror stacks

- **WHEN** the operator enables the GCP mirror stacks in
  `bonneagar/stacks/gcp-*/`
- **THEN** the deployment uses Vertex AI Gemini 3.5 Flash +
  Unsloth Studio Gemma 4 as the Tier 1 + Tier 2 chain

#### Scenario: tuatha uses the Primary + Gemma 4 fallback chain

- **WHEN** `~/dev/tuatha/tuatha/baml/` declares a BAML function
- **THEN** the function uses `client "Primary"` (the
  env-driven dispatcher)
- **AND** the function's fallback chain includes `UnslothGemma4`
  + `VertexGemini35Flash`

#### Scenario: ciancheiltis uses Gemma 4 for Celtic-language extraction

- **WHEN** the 6 Celtic-language BAML extraction functions are
  invoked in `~/dev/ciancheiltis/`
- **THEN** the functions route through `gemma-4-26b-a4b`
  via Unsloth Studio

#### Scenario: ciandlithe uses Document AI for OSINT legal-doc pipeline

- **WHEN** `~/dev/ciandlithe/` ingests an OSINT legal document
- **THEN** the OCR ensemble uses Document AI as the primary
  path
- **AND** the dossier-generator CopilotKit UI is rendered per the
  gemini_hackathon Stitch pattern

#### Scenario: cianchosaint uses Cloud Run ADK + AG-UI

- **WHEN** `~/dev/cianchosaint/` ingests an OSINT defence source
- **THEN** the ADK 2-stage coordinator runs on Cloud Run
- **AND** the per-persona dashboard is rendered via AG-UI

### Requirement: Sister-repo transfers SHALL be deeply per-sister

The system MUST require each sister-repo transfer to be deeply
customised to the sister repo's domain (NOT a wholesale copy).
Each sister repo gets its own BAML client roster + its own
CocoIndex App + its own CopilotKit/AG-UI agents.

#### Scenario: bonneagar transfer is IaC-focused

- **WHEN** the bonneagar transfer lands
- **THEN** the BAML clients + CocoIndex Apps + CopilotKit agents
  are IaC-specific (Komodo stack definitions + Pangolin
  resource specs + Locket template syntax)

#### Scenario: tuatha transfer is MMO-focused

- **WHEN** the tuatha transfer lands
- **THEN** the BAML clients + CocoIndex Apps + CopilotKit agents
  are MMO-specific (per-subject quest packs + per-persona
  dashboards + per-NCCA-subject ADK agents)