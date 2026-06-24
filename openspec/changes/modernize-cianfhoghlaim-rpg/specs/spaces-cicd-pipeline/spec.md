## ADDED Requirements

### Requirement: cianfhoghlaim Pydantic schema validation

The `cianfhoghlaim` Space MUST validate every LLM response against the Pydantic schema (PNpcDialogue) before returning the dialogue to the UI. The Space MUST add `pydantic>=2.5` to `spaces/cianfhoghlaim/requirements.txt`.
