## ADDED Requirements

### Requirement: Anti-phish Space moved to private archive

The `spaces/anti-phish/` directory MUST NOT be a public Cianfhoghlaim HuggingFace Space. The 6 Colab notebooks + the original README MUST live in `archive/anti-phish-2022-academic/` (private archive, not pushed to HF) until a new openspec change (`modernize-anti-phish-space`) rebuilds the directory with the KCG canonical stack.

#### Scenario: User finds the old anti-phish Space

- **WHEN** an agent or user navigates to `spaces/anti-phish/`
- **THEN** the directory does not exist (it was moved to `archive/anti-phish-2022-academic/`)
- **AND** the `spaces/AGENTS.md` (added by the `spaces-priority-quick-reference` change) explains the move

#### Scenario: Re-publishing requires a new openspec change

- **WHEN** the user wants to re-publish the anti-phish work as a public HF Space
- **THEN** they MUST create a new `modernize-anti-phish-space` openspec change that uses the KCG canonical stack (LiteLLM gateway + BAML + ccc + Cognee) and does NOT include the personal reflection
