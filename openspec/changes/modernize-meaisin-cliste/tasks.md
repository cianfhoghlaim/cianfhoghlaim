# Tasks: modernize-meaisin-cliste

## 1. Add Pydantic schemas

- [x] Add `PCurriculumMapping` (mirrors the canonical BAML class)
- [x] Add `PCrossNationComparison` (the top-level result)

## 2. Update validation

- [x] Update `_coerce` to use the Pydantic schema
      (fall back to the flat schema on validation failure)

## 3. Add pydantic to requirements

- [x] Add `pydantic>=2.5` to `spaces/meaisin_cliste/requirements.txt`

## 4. Spec deltas

- [x] 1 ADDED Requirement on `meaisinfhoghlaim-platform`:
      "CompareCelticNations Pydantic mirror"
- [x] 1 ADDED Requirement on `spaces-cicd-pipeline`:
      "meaisin_cliste Pydantic schema validation"

## 5. Validate + commit + push + archive

- [x] `openspec validate modernize-meaisin-cliste --strict`
- [x] Commit + archive + push
