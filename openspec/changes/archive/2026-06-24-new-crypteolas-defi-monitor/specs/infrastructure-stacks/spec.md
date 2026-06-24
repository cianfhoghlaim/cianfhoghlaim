## ADDED Requirements

### Requirement: crypteolas DeFi Monitor Space

The crypteolas data platform MUST provide a DeFi Monitor HuggingFace Space at `spaces/crypteolas_defi_monitor/` that exposes the 4 streams (GitHub + DeFi + Knowledge Graph + Marimo) as a single Gradio app. The Space MUST be wired to the canonical Cognee + Graphiti knowledge graph and the Agno multi-agent team.

#### Scenario: User opens the DeFi Monitor

- **WHEN** a user navigates to the crypteolas_defi_monitor Space
- **THEN** they see 4 tabs (GitHub + DeFi + Knowledge Graph + Marimo)
- **AND** each tab shows the corresponding stream's data
- **AND** the Knowledge Graph tab is wired to Cognee + Graphiti
- **AND** the Marimo tab launches the 4 crypteolas notebooks
