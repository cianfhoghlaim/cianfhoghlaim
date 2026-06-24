## Why

`spaces/cianfhoghlaim/dialogue.py` (the Hades-style RPG) has the
same pattern as an_scrudu (C1) + meaisin_cliste (C2): the
BAML `GenerateNpcDialogue` function has been promoted to
`tuatha/baml_src/mythology_extraction.baml` (A1) and the
LiteLLM gateway is the primary LLM tier (A2), but the Space's
`_validate_npc_response` still uses the flat legacy schema.

This change modernizes the Space (same pattern as C1 + C2):

1. Add Pydantic v2 schemas (`PNpcDialogue` + `PNpcDialogueExchange`) that mirror the canonical BAML classes
2. Update `_validate_npc_response` to validate against the Pydantic schema
3. Accept both the nested BAML shape (`{dialogue: {...}, npc_name, npc_title, turn_index}`) and the flat legacy shape
4. Add `pydantic>=2.5` to `requirements.txt`

## What changes

- `spaces/cianfhoghlaim/dialogue.py` — add 2 Pydantic models + update `_validate_npc_response` to use them
- `spaces/cianfhoghlaim/requirements.txt` — add `pydantic>=2.5`
- 1 ADDED Requirement to `tuatha-platform` spec
- 1 ADDED Requirement to `spaces-cicd-pipeline` spec
