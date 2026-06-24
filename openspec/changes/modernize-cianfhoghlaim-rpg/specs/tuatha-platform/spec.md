## ADDED Requirements

### Requirement: GenerateNpcDialogue Pydantic mirror

The canonical BAML function `GenerateNpcDialogue` (in `tuatha/baml_src/mythology_extraction.baml`) MUST have a Pydantic v2 mirror in `spaces/cianfhoghlaim/dialogue.py`. The Pydantic classes (`PNpcDialogue`, `PNpcDialogueExchange`) MUST mirror the BAML class shapes exactly, and `_validate_npc_response` MUST validate the LLM response against the Pydantic schema before falling back to the flat legacy schema.

#### Scenario: LLM returns valid NpcDialogueExchange

- **WHEN** the LiteLLM gateway returns a JSON object with `{npc_name, npc_title, turn_index, dialogue: {utterance_en, ..., asks_player_about}}`
- **THEN** `_validate_npc_response` validates it against `PNpcDialogue` (or `PNpcDialogueExchange` for the full shape)
- **AND** on success, maps to the flat dict for the UI
- **AND** on failure, falls back to the flat schema with defaults
