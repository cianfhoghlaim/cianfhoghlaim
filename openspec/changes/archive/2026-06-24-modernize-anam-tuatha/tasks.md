# Tasks: modernize-anam-tuatha

## 1. Add Pydantic schemas

- [x] Add `PExitCardQuestion` (mirrors the canonical BAML class)
- [x] Add `PExitCardSet` (the top-level result)

## 2. Update validation

- [x] Update `_coerce` to use the Pydantic schema
      (fall back to the flat schema on validation failure)

## 3. Add pydantic to requirements

- [x] Add `pydantic>=2.5` to `spaces/anam_sruth/tuatha/requirements.txt`

## 4. Spec deltas

- [x] 1 ADDED Requirement on `tuatha-platform`:
      "GenerateExitCardQuestions Pydantic mirror"
- [x] 1 ADDED Requirement on `spaces-cicd-pipeline`:
      "anam_tuatha Pydantic schema validation"

## 5. Commit + archive + push

- [x] Commit + archive + push
