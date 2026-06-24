# Tasks: modernize-cianfhoghlaim-rpg

## 1. Add Pydantic schemas

- [x] Add `PNpcDialogue` (mirrors the canonical BAML class)
- [x] Add `PNpcDialogueExchange` (the top-level result)

## 2. Update validation

- [x] Update `_validate_npc_response` to use the Pydantic schema
      (accepts both nested BAML shape and flat legacy shape)

## 3. Add pydantic to requirements

- [x] Add `pydantic>=2.5` to `spaces/cianfhoghlaim/requirements.txt`

## 4. Spec deltas

- [x] 1 ADDED Requirement on `tuatha-platform`:
      "GenerateNpcDialogue Pydantic mirror"
- [x] 1 ADDED Requirement on `spaces-cicd-pipeline`:
      "cianfhoghlaim Pydantic schema validation"

## 5. Commit + archive + push

- [x] Commit + archive + push
