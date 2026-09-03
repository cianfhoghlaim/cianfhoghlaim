# image-generation-agent Specification

## Purpose

Define the agent that consumes the 5 `image_gen` MODEL_REGISTRY
entries (`flux2-dev`, `z-image-turbo`, `qwen-image`, `sdxx`,
`fibo`) for educational game assets (the retro-game-asset-pipeline)
+ Babylon.js textures (the educational MMO).

The system is added by the
2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
openspec change (Phase L).

## ADDED Requirements

### Requirement: image_generation_agent SHALL consume the 5 image_gen entries

The system SHALL provide an `image_generation_agent` ADK agent
that consumes the 5 `image_gen` MODEL_REGISTRY entries.

The agent MUST provide at minimum these 4 tools:

- `generate_2d_asset(prompt, style, size)` → returns the URL of
  the generated 2D asset + the CocoIndex record
- `generate_texture(name, pattern, size)` → returns the URL of
  the generated texture + the Babylon.js material reference
- `style_match(reference_image, prompt, count)` → returns a list
  of generated images matching the reference style
- `cocoindex_register(asset_url, metadata)` → registers the
  asset in the CocoIndex `image_generation` flow

The agent MUST route via `model_for('image_gen', role)` —
never hardcode a model string.

#### Scenario: The 5 models are registered in MODEL_REGISTRY

- **GIVEN** the 5 image_gen entries in `MODEL_REGISTRY`
- **WHEN** the operator runs
  `python -c "from meaisinfhoghlaim.models import MODEL_REGISTRY; print(len(MODEL_REGISTRY.filter(family='image_gen')))"`
- **THEN** the output is `>= 5`
- **AND** each entry MUST have `available: bool` flag
- **AND** the `image_generation_agent` MUST gracefully fall back
  to an available model when the requested role's primary entry
  is unavailable

### Requirement: The 5 image_gen entries SHALL have a consumer agent

Every entry in `MODEL_REGISTRY.filter(family='image_gen')` MUST
be consumable by at least one agent. The `image_generation_agent`
is the canonical consumer for all 5 entries.

#### Scenario: Adding a new image_gen entry

- **WHEN** a developer adds a new entry to
  `meaisinfhoghlaim/models/model_registry.py:MODEL_REGISTRY`
  with `family="image_gen"`
- **THEN** the entry MUST be consumable by `image_generation_agent`
  via `model_for('image_gen', role)`
- **AND** the entry's role MUST be documented in the
  `centralized-registry/SKILL.md §11.1` family table
- **AND** if the entry has a new role, the
  `image_generation_agent.py` MUST handle it
